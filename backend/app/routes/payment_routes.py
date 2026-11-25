"""
Pago directo a la barbería (sin pasarela).

Métodos: efectivo, transferencia bancaria, consignación, Nequi y Daviplata.
La barbería publica sus datos de pago; el cliente elige uno al reservar,
paga por su cuenta y puede reportar la referencia; la barbería confirma
cuando verifica que recibió el dinero.

  payment_status:  PENDING -> REPORTED (cliente avisó) -> PAID (barbería verificó)
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Literal

from app.core.rate_limit import check_rate_limit, client_ip
from app.db.session import get_db
from app.dependencies.auth_dependencies import get_current_user
from app.models.booking_model import Booking
from app.models.user_model import User
from app.routes.barbershop_settings_routes import require_barbershop_settings_access

router = APIRouter(tags=["Pagos"])

Method = Literal["CASH", "BANK_TRANSFER", "DEPOSIT", "NEQUI", "DAVIPLATA"]


# =========================================================
# SCHEMAS
# =========================================================
class PaymentMethodIn(BaseModel):
    method: Method
    bank_name: str | None = Field(default=None, max_length=80)
    account_type: str | None = Field(default=None, max_length=20)
    account_number: str | None = Field(default=None, max_length=40)
    account_holder: str | None = Field(default=None, max_length=120)
    holder_document: str | None = Field(default=None, max_length=30)
    instructions: str | None = Field(default=None, max_length=300)
    is_active: bool = True

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def check_required(self):
        if not self.is_active or self.method == "CASH":
            return self
        digits = "".join(c for c in (self.account_number or "") if c.isdigit())
        if self.method in ("NEQUI", "DAVIPLATA"):
            if len(digits) != 10:
                raise ValueError(f"El número de {self.method.title()} debe tener 10 dígitos.")
            if not self.account_holder:
                raise ValueError(f"Indica a nombre de quién está el {self.method.title()}.")
        else:
            if not (self.bank_name and self.account_number and self.account_holder):
                raise ValueError("Transferencia y consignación requieren banco, número de cuenta y titular.")
        return self


class PaymentMethodsIn(BaseModel):
    methods: list[PaymentMethodIn] = Field(max_length=5)

    @model_validator(mode="after")
    def unique(self):
        names = [m.method for m in self.methods]
        if len(names) != len(set(names)):
            raise ValueError("No repitas métodos de pago.")
        return self


class PaymentStatusIn(BaseModel):
    status: Literal["PAID", "PENDING"]


class PaymentReferenceIn(BaseModel):
    reference: str = Field(min_length=3, max_length=80)

    model_config = ConfigDict(str_strip_whitespace=True)


# =========================================================
# HELPERS
# =========================================================
COLS = ("method, bank_name, account_type, account_number, account_holder, "
        "holder_document, instructions, is_active")


def _methods(db: Session, barbershop_id: int, only_active: bool) -> list[dict]:
    sql = f"SELECT {COLS} FROM barbershop_payment_methods WHERE barbershop_id = :i"
    if only_active:
        sql += " AND is_active = TRUE"
    sql += " ORDER BY id"
    rows = db.execute(text(sql), {"i": barbershop_id}).mappings().all()
    return [{**dict(r), "is_active": bool(r["is_active"])} for r in rows]


# =========================================================
# PÚBLICO: métodos que acepta una barbería
# =========================================================
@router.get("/barbershops/{barbershop_id}/payment-methods")
def public_payment_methods(barbershop_id: int, db: Session = Depends(get_db)):
    return _methods(db, barbershop_id, only_active=True)


# =========================================================
# BARBERÍA: configurar métodos
# =========================================================
@router.get("/barbershop-settings/{barbershop_id}/payment-methods")
def get_payment_methods(
    barbershop_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_barbershop_settings_access),
):
    return _methods(db, barbershop_id, only_active=False)


@router.put("/barbershop-settings/{barbershop_id}/payment-methods")
def save_payment_methods(
    barbershop_id: int,
    data: PaymentMethodsIn,
    db: Session = Depends(get_db),
    _user: User = Depends(require_barbershop_settings_access),
):
    db.execute(text("DELETE FROM barbershop_payment_methods WHERE barbershop_id = :i"), {"i": barbershop_id})
    for m in data.methods:
        db.execute(text("""
            INSERT INTO barbershop_payment_methods
              (barbershop_id, method, bank_name, account_type, account_number,
               account_holder, holder_document, instructions, is_active)
            VALUES (:shop, :method, :bank, :atype, :number, :holder, :doc, :ins, :active)
        """), {
            "shop": barbershop_id, "method": m.method,
            "bank": m.bank_name, "atype": m.account_type, "number": m.account_number,
            "holder": m.account_holder, "doc": m.holder_document, "ins": m.instructions,
            "active": bool(m.is_active),
        })
    db.commit()
    return _methods(db, barbershop_id, only_active=False)


# =========================================================
# BARBERÍA: verificar pagos
# =========================================================
@router.get("/barbershop-settings/{barbershop_id}/payments")
def list_payments(
    barbershop_id: int,
    state: Literal["OPEN", "PAID", "ALL"] = "OPEN",
    db: Session = Depends(get_db),
    _user: User = Depends(require_barbershop_settings_access),
):
    where = {
        "OPEN": "AND b.payment_status IN ('PENDING','REPORTED')",
        "PAID": "AND b.payment_status = 'PAID'",
        "ALL": "",
    }[state]
    rows = db.execute(text(f"""
        SELECT b.id, b.start_at, b.service_price, b.home_fee, b.payment_method,
               b.payment_status, b.payment_reference, b.payment_reported_at,
               COALESCE(CONCAT(u.first_name, ' ', u.last_name), b.guest_name) AS client_name,
               s.name AS service_name, st.code AS booking_status
        FROM bookings b
        JOIN services s ON s.id = b.service_id
        JOIN booking_statuses st ON st.id = b.status_id
        LEFT JOIN users u ON u.id = b.client_user_id
        WHERE b.barbershop_id = :i
          AND b.payment_method IS NOT NULL
          AND st.code IN ('PENDING','CONFIRMED','IN_PROGRESS','COMPLETED')
          {where}
        ORDER BY b.start_at DESC
        LIMIT 100
    """), {"i": barbershop_id}).mappings().all()
    return [
        {**dict(r), "total": float(r["service_price"] or 0) + float(r["home_fee"] or 0)}
        for r in rows
    ]


@router.patch("/barbershop-settings/{barbershop_id}/payments/{booking_id}")
def set_payment_status(
    barbershop_id: int,
    booking_id: int,
    data: PaymentStatusIn,
    db: Session = Depends(get_db),
    _user: User = Depends(require_barbershop_settings_access),
):
    booking = db.get(Booking, booking_id)
    if not booking or booking.barbershop_id != barbershop_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reserva no encontrada.")
    if not booking.payment_method:
        raise HTTPException(status.HTTP_409_CONFLICT, "Esta reserva no tiene un método de pago.")

    booking.payment_status = data.status
    booking.payment_confirmed_at = datetime.now() if data.status == "PAID" else None
    db.commit()
    return {"id": booking.id, "payment_status": booking.payment_status}


# =========================================================
# CLIENTE: reportar referencia de pago
# =========================================================
def _report(booking: Booking, reference: str, db: Session) -> dict:
    if not booking.payment_method or booking.payment_method == "CASH":
        raise HTTPException(status.HTTP_409_CONFLICT, "Esta reserva no requiere reportar un pago.")
    if booking.payment_status == "PAID":
        raise HTTPException(status.HTTP_409_CONFLICT, "El pago ya fue confirmado por la barbería.")
    booking.payment_reference = reference
    booking.payment_status = "REPORTED"
    booking.payment_reported_at = datetime.now()
    db.commit()
    return {"id": booking.id, "payment_status": booking.payment_status, "payment_reference": reference}


@router.post("/bookings/{booking_id}/payment-reference")
def report_payment(
    booking_id: int,
    data: PaymentReferenceIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.get(Booking, booking_id)
    if not booking or booking.client_user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reserva no encontrada.")
    return _report(booking, data.reference, db)


@router.post("/guest/bookings/{token}/payment-reference")
def report_guest_payment(
    token: str,
    data: PaymentReferenceIn,
    request: Request,
    db: Session = Depends(get_db),
):
    check_rate_limit(f"guest-pay:{client_ip(request)}", max_hits=20, window_seconds=600)
    booking = db.query(Booking).filter(Booking.manage_token == token).first()
    if not booking or len(token) < 20:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reserva no encontrada.")
    return _report(booking, data.reference, db)
