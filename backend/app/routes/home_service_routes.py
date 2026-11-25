"""
Servicio a domicilio.

Una barbería NO puede publicarlo por sí sola:

  NONE -> (solicita) -> PENDING -> (admin aprueba) -> APPROVED
                                 -> (admin rechaza) -> REJECTED -> (corrige y solicita de nuevo)
  APPROVED -> (admin suspende) -> SUSPENDED

Al aprobarse se activa `offers_home_service`, que es lo que lee el
buscador y la reserva.
"""

import json
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.admin_dependencies import require_platform_admin
from app.models.barbershop_model import Barbershop
from app.models.user_model import User
from app.routes.barbershop_settings_routes import require_barbershop_settings_access
from app.services.notification_service import NotificationService

router = APIRouter(tags=["Servicio a domicilio"])


# =========================================================
# SCHEMAS
# =========================================================
class HomeServiceRequest(BaseModel):
    radius_km: Decimal = Field(gt=0, le=50)
    fee: Decimal = Field(ge=0, le=500000)
    min_notice_hours: int = Field(ge=0, le=72)
    zones: str | None = Field(default=None, max_length=500)

    # Declaraciones obligatorias
    hygiene_kit: bool
    barbers_verified: bool
    accepts_policy: bool
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("hygiene_kit", "barbers_verified", "accepts_policy")
    @classmethod
    def must_be_true(cls, value: bool):
        if not value:
            raise ValueError("Debes aceptar todos los requisitos para solicitar el servicio.")
        return value

    model_config = ConfigDict(str_strip_whitespace=True)


class HomeServiceTerms(BaseModel):
    fee: Decimal = Field(ge=0, le=500000)
    min_notice_hours: int = Field(ge=0, le=72)
    zones: str | None = Field(default=None, max_length=500)

    model_config = ConfigDict(str_strip_whitespace=True)


class HomeServiceReject(BaseModel):
    reason: str = Field(min_length=5, max_length=300)

    model_config = ConfigDict(str_strip_whitespace=True)


def _view(shop: Barbershop) -> dict:
    requirements = None
    if shop.home_service_requirements:
        try:
            requirements = json.loads(shop.home_service_requirements)
        except ValueError:
            requirements = None
    return {
        "barbershop_id": shop.id,
        "barbershop_name": shop.name,
        "status": shop.home_service_status,
        "offers_home_service": bool(shop.offers_home_service),
        "radius_km": float(shop.home_service_radius_km) if shop.home_service_radius_km is not None else None,
        "fee": float(shop.home_service_fee or 0),
        "min_notice_hours": shop.home_service_min_notice_hours,
        "zones": shop.home_service_zones,
        "requirements": requirements,
        "rejection_reason": shop.home_service_rejection_reason,
        "requested_at": shop.home_service_requested_at,
        "reviewed_at": shop.home_service_reviewed_at,
        "has_coordinates": shop.latitude is not None and shop.longitude is not None,
    }


def _get_shop(db: Session, barbershop_id: int) -> Barbershop:
    shop = db.get(Barbershop, barbershop_id)
    if not shop:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "La barbería no existe.")
    return shop


# =========================================================
# BARBERÍA (dueño / administrador de la barbería)
# =========================================================
@router.get("/barbershop-settings/{barbershop_id}/home-service")
def get_home_service(
    barbershop_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_barbershop_settings_access),
):
    return _view(_get_shop(db, barbershop_id))


@router.post("/barbershop-settings/{barbershop_id}/home-service/request")
def request_home_service(
    barbershop_id: int,
    data: HomeServiceRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_barbershop_settings_access),
):
    shop = _get_shop(db, barbershop_id)

    if shop.home_service_status == "PENDING":
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya tienes una solicitud en revisión.")
    if shop.home_service_status == "APPROVED":
        raise HTTPException(status.HTTP_409_CONFLICT, "El servicio a domicilio ya está aprobado.")
    if shop.latitude is None or shop.longitude is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Primero registra la ubicación (latitud y longitud) de la barbería: "
            "se usa para validar la zona de cobertura.",
        )

    # ¿Hay al menos un barbero y un servicio habilitados para domicilio?
    barbers = db.execute(text(
        "SELECT COUNT(*) FROM barbers WHERE barbershop_id = :i AND is_active = TRUE AND accepts_home_service = TRUE"
    ), {"i": barbershop_id}).scalar() or 0
    services = db.execute(text(
        "SELECT COUNT(*) FROM services WHERE barbershop_id = :i AND is_active = TRUE AND home_service_allowed = TRUE"
    ), {"i": barbershop_id}).scalar() or 0
    if barbers == 0 or services == 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Necesitas al menos un barbero que acepte domicilio y un servicio habilitado para domicilio.",
        )

    shop.home_service_status = "PENDING"
    shop.home_service_radius_km = data.radius_km
    shop.home_service_fee = data.fee
    shop.home_service_min_notice_hours = data.min_notice_hours
    shop.home_service_zones = data.zones
    shop.home_service_requirements = json.dumps({
        "hygiene_kit": data.hygiene_kit,
        "barbers_verified": data.barbers_verified,
        "accepts_policy": data.accepts_policy,
        "notes": data.notes,
        "declared_barbers": int(barbers),
        "declared_services": int(services),
    }, ensure_ascii=False)
    shop.home_service_rejection_reason = None
    shop.home_service_requested_at = datetime.now()
    shop.offers_home_service = False
    db.commit()

    NotificationService.home_service_requested(db, barbershop_id)
    return _view(shop)


@router.patch("/barbershop-settings/{barbershop_id}/home-service/terms")
def update_home_service_terms(
    barbershop_id: int,
    data: HomeServiceTerms,
    db: Session = Depends(get_db),
    _user: User = Depends(require_barbershop_settings_access),
):
    """Ajustar tarifa, anticipación y zonas (no cambia el radio aprobado)."""
    shop = _get_shop(db, barbershop_id)
    if shop.home_service_status != "APPROVED":
        raise HTTPException(status.HTTP_409_CONFLICT, "El servicio a domicilio aún no está aprobado.")
    shop.home_service_fee = data.fee
    shop.home_service_min_notice_hours = data.min_notice_hours
    shop.home_service_zones = data.zones
    db.commit()
    return _view(shop)


@router.delete("/barbershop-settings/{barbershop_id}/home-service")
def disable_home_service(
    barbershop_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_barbershop_settings_access),
):
    shop = _get_shop(db, barbershop_id)
    shop.home_service_status = "NONE"
    shop.offers_home_service = False
    db.commit()
    return _view(shop)


# =========================================================
# ADMINISTRADOR DE LA PLATAFORMA
# =========================================================
@router.get("/admin/home-service/requests")
def list_home_service_requests(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_platform_admin),
):
    query = db.query(Barbershop).filter(Barbershop.home_service_status != "NONE")
    if status_filter:
        query = query.filter(Barbershop.home_service_status == status_filter.upper())
    shops = query.order_by(Barbershop.home_service_requested_at.desc()).limit(200).all()
    return [_view(s) for s in shops]


@router.post("/admin/barbershops/{barbershop_id}/home-service/approve")
def approve_home_service(
    barbershop_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_platform_admin),
):
    shop = _get_shop(db, barbershop_id)
    if shop.home_service_status not in ("PENDING", "SUSPENDED"):
        raise HTTPException(status.HTTP_409_CONFLICT, "Solo se pueden aprobar solicitudes pendientes o suspendidas.")
    shop.home_service_status = "APPROVED"
    shop.offers_home_service = True
    shop.home_service_rejection_reason = None
    shop.home_service_reviewed_at = datetime.now()
    db.commit()
    NotificationService.home_service_decision(db, barbershop_id, True, None)
    return _view(shop)


@router.post("/admin/barbershops/{barbershop_id}/home-service/reject")
def reject_home_service(
    barbershop_id: int,
    data: HomeServiceReject,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_platform_admin),
):
    shop = _get_shop(db, barbershop_id)
    if shop.home_service_status != "PENDING":
        raise HTTPException(status.HTTP_409_CONFLICT, "Solo se pueden rechazar solicitudes pendientes.")
    shop.home_service_status = "REJECTED"
    shop.offers_home_service = False
    shop.home_service_rejection_reason = data.reason
    shop.home_service_reviewed_at = datetime.now()
    db.commit()
    NotificationService.home_service_decision(db, barbershop_id, False, data.reason)
    return _view(shop)


@router.post("/admin/barbershops/{barbershop_id}/home-service/suspend")
def suspend_home_service(
    barbershop_id: int,
    data: HomeServiceReject,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_platform_admin),
):
    shop = _get_shop(db, barbershop_id)
    if shop.home_service_status != "APPROVED":
        raise HTTPException(status.HTTP_409_CONFLICT, "Solo se puede suspender un servicio aprobado.")
    shop.home_service_status = "SUSPENDED"
    shop.offers_home_service = False
    shop.home_service_rejection_reason = data.reason
    shop.home_service_reviewed_at = datetime.now()
    db.commit()
    NotificationService.home_service_decision(db, barbershop_id, False, data.reason)
    return _view(shop)
