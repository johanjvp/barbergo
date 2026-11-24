from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
    
)


# =========================================================
# CREAR SERVICIO
# =========================================================

class ServiceCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=120
    )

    description: str | None = None

    price: Decimal = Field(
        gt=0,
        decimal_places=2,
        max_digits=12
    )

    duration_minutes: int = Field(
        gt=0,
        le=480
    )

    is_vip: bool = False

    home_service_allowed: bool = False

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


# =========================================================
# ACTUALIZAR SERVICIO
# =========================================================

class ServiceUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=120
    )

    description: str | None = None

    price: Decimal | None = Field(
        default=None,
        gt=0,
        decimal_places=2,
        max_digits=12
    )

    duration_minutes: int | None = Field(
        default=None,
        gt=0,
        le=480
    )

    is_vip: bool | None = None

    home_service_allowed: bool | None = None

    is_active: bool | None = None

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


# =========================================================
# RESPUESTA
# =========================================================

class ServiceResponse(BaseModel):

    id: int
    barbershop_id: int

    name: str
    description: str | None

    price: Decimal
    duration_minutes: int

    is_vip: bool
    home_service_allowed: bool
    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )