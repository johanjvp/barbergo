"""
Reservas sin cuenta (invitados).

Flujo:
  1. request_code        -> se envía un código de 6 dígitos al correo
  2. create_booking      -> valida el código y crea la reserva con un
                            enlace de gestión (token) para ver / cancelar
  3. get_by_token        -> el invitado consulta su cita
  4. cancel_by_token     -> el invitado cancela dentro de la política
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    BookingCancellationWindowError,
    BookingNotFoundError,
    BookingStatusNotFoundError,
    InvalidBookingStatusTransitionError,
)
from app.models.booking_model import Booking
from app.repositories.barbershop_repository import BarbershopRepository
from app.repositories.booking_repository import BookingRepository
from app.schemas.guest_schema import GuestBookingCreate
from app.services.booking_service import BookingService
from app.services.notification_service import NotificationService


class GuestBookingService:

    CODE_TTL_MINUTES = 10
    MAX_ATTEMPTS = 5
    MAX_CODES_PER_WINDOW = 3          # por correo
    CODE_WINDOW_MINUTES = 10

    # =====================================================
    # CÓDIGO
    # =====================================================
    @staticmethod
    def _hash(email: str, code: str) -> str:
        return hmac.new(
            settings.JWT_SECRET_KEY.encode(),
            f"{email}:{code}".encode(),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def request_code(db: Session, email: str) -> int:
        email = email.strip().lower()
        now = datetime.now()

        recent = db.execute(text("""
            SELECT COUNT(*) FROM email_verifications
            WHERE email = :email AND created_at >= :since
        """), {
            "email": email,
            "since": now - timedelta(minutes=GuestBookingService.CODE_WINDOW_MINUTES),
        }).scalar() or 0

        if recent >= GuestBookingService.MAX_CODES_PER_WINDOW:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Ya enviamos varios códigos a este correo. Espera unos minutos.",
            )

        code = f"{secrets.randbelow(1_000_000):06d}"
        db.execute(text("""
            INSERT INTO email_verifications (email, code_hash, purpose, expires_at)
            VALUES (:email, :hash, 'GUEST_BOOKING', :expires)
        """), {
            "email": email,
            "hash": GuestBookingService._hash(email, code),
            "expires": now + timedelta(minutes=GuestBookingService.CODE_TTL_MINUTES),
        })
        db.commit()

        NotificationService.send_verification_code(
            email, code, GuestBookingService.CODE_TTL_MINUTES
        )
        return GuestBookingService.CODE_TTL_MINUTES

    @staticmethod
    def _check_code(db: Session, email: str, code: str) -> int:
        """Valida el código. Devuelve el id de verificación (sin consumirlo)."""
        email = email.strip().lower()
        row = db.execute(text("""
            SELECT id, code_hash, attempts
            FROM email_verifications
            WHERE email = :email AND used_at IS NULL AND expires_at > :now
            ORDER BY id DESC LIMIT 1
        """), {"email": email, "now": datetime.now()}).mappings().first()

        bad = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código es incorrecto o ya venció. Solicita uno nuevo.",
        )
        if not row or row["attempts"] >= GuestBookingService.MAX_ATTEMPTS:
            raise bad

        if not hmac.compare_digest(row["code_hash"], GuestBookingService._hash(email, code)):
            db.execute(text(
                "UPDATE email_verifications SET attempts = attempts + 1 WHERE id = :id"
            ), {"id": row["id"]})
            db.commit()
            raise bad

        return row["id"]

    @staticmethod
    def _consume(db: Session, verification_id: int) -> None:
        db.execute(text(
            "UPDATE email_verifications SET used_at = :now WHERE id = :id"
        ), {"id": verification_id, "now": datetime.now()})
        db.commit()

    # =====================================================
    # CREAR
    # =====================================================
    @staticmethod
    def _assert_guests_allowed(db: Session, barber_id: int) -> None:
        """Respeta el ajuste de la barbería 'exigir cuenta al cliente'."""
        try:
            row = db.execute(text("""
                SELECT bs.require_customer_account, bs.bookings_enabled
                FROM barbershop_settings bs
                JOIN barbers b ON b.barbershop_id = bs.barbershop_id
                WHERE b.id = :barber LIMIT 1
            """), {"barber": barber_id}).first()
        except Exception:
            db.rollback()   # la tabla de ajustes puede no existir: no se bloquea
            return

        if row and row[0]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Esta barbería solo acepta reservas de clientes con cuenta. "
                       "Inicia sesión o crea una cuenta gratis para reservar.",
            )
        if row and row[1] is not None and not row[1]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta barbería no está recibiendo reservas en este momento.",
            )

    @staticmethod
    def create_booking(db: Session, data: GuestBookingCreate) -> dict:
        email = str(data.email).strip().lower()
        GuestBookingService._assert_guests_allowed(db, data.barber_id)
        verification_id = GuestBookingService._check_code(db, email, data.code)

        token = secrets.token_urlsafe(32)

        response = BookingService.create(
            db,
            data,
            current_user=None,
            guest={
                "name": data.name.strip(),
                "email": email,
                "phone": data.phone.strip(),
                "manage_token": token,
                "verified_at": datetime.now(),
            },
        )

        GuestBookingService._consume(db, verification_id)
        NotificationService.booking_event(db, response["id"], "CREATED_GUEST")

        response["manage_token"] = token
        return response

    # =====================================================
    # CONSULTAR / CANCELAR POR TOKEN
    # =====================================================
    @staticmethod
    def _by_token(db: Session, token: str) -> Booking:
        booking = db.query(Booking).filter(Booking.manage_token == token).first()
        if not booking or len(token) < 20:
            raise BookingNotFoundError()
        return booking

    @staticmethod
    def get_by_token(db: Session, token: str) -> dict:
        booking = GuestBookingService._by_token(db, token)
        ctx = NotificationService.booking_context(db, booking.id)
        shop = BarbershopRepository.get_by_id(db, booking.barbershop_id)
        hours = (shop.cancellation_hours_before or 0) if shop else 0
        deadline = booking.start_at - timedelta(hours=hours)

        can_cancel = (
            ctx["status_code"] in ("PENDING", "CONFIRMED")
            and datetime.now() <= deadline
        )

        return {
            "id": booking.id,
            "status_code": ctx["status_code"],
            "start_at": booking.start_at,
            "end_at": booking.end_at,
            "guest_name": booking.guest_name,
            "barbershop_name": ctx["shop_name"],
            "barbershop_address": ctx["shop_address"],
            "barbershop_phone": ctx["shop_phone"],
            "service_name": ctx["service_name"],
            "barber_name": ctx["barber_name"],
            "service_price": booking.service_price,
            "home_fee": booking.home_fee or 0,
            "booking_type": booking.booking_type or "IN_SHOP",
            "home_address": booking.home_address,
            "can_cancel": can_cancel,
            "cancel_deadline": deadline,
            "cancellation_hours_before": hours,
            "payment_method": booking.payment_method,
            "payment_status": booking.payment_status or "PENDING",
            "payment_reference": booking.payment_reference,
            "payment_details": (
                {
                    "bank_name": ctx.get("bank_name"),
                    "account_type": ctx.get("account_type"),
                    "account_number": ctx.get("account_number"),
                    "account_holder": ctx.get("account_holder"),
                    "holder_document": ctx.get("holder_document"),
                    "instructions": ctx.get("pay_instructions"),
                }
                if booking.payment_method
                else None
            ),
        }

    @staticmethod
    def cancel_by_token(db: Session, token: str) -> dict:
        booking = GuestBookingService._by_token(db, token)
        current = BookingRepository.get_status_by_id(db, booking.status_id)

        if not current or current.code not in ("PENDING", "CONFIRMED"):
            raise InvalidBookingStatusTransitionError(
                "Esta reserva ya no puede ser cancelada."
            )

        shop = BarbershopRepository.get_by_id(db, booking.barbershop_id)
        hours = (shop.cancellation_hours_before or 0) if shop else 0
        now = datetime.now()

        if now >= booking.start_at:
            raise BookingCancellationWindowError(
                "La cita ya comenzó o su hora programada ya pasó."
            )
        if now > booking.start_at - timedelta(hours=hours):
            raise BookingCancellationWindowError(
                f"La reserva solo puede cancelarse hasta {hours} hora(s) antes de la cita."
            )

        cancelled = BookingRepository.get_status_by_code(db, "CANCELLED_BY_CUSTOMER")
        if not cancelled:
            raise BookingStatusNotFoundError()

        # El cambio de estado dispara el correo de cancelación
        # (ver app/services/booking_events.py).
        booking.status_id = cancelled.id
        db.commit()
        return GuestBookingService.get_by_token(db, token)
