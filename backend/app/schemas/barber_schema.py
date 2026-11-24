from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


# =========================================================
# CREAR BARBERO
# =========================================================

class BarberCreate(BaseModel):

    user_id: int = Field(
        gt=0
    )

    bio: str | None = None

    years_experience: int | None = Field(
        default=None,
        ge=0,
        le=80
    )

    accepts_home_service: bool = False

    service_ids: list[int] = Field(
        default_factory=list
    )


# =========================================================
# ACTUALIZAR BARBERO
# =========================================================

class BarberUpdate(BaseModel):

    bio: str | None = None

    years_experience: int | None = Field(
        default=None,
        ge=0,
        le=80
    )

    accepts_home_service: bool | None = None

    is_active: bool | None = None

    service_ids: list[int] | None = None


# =========================================================
# RESPUESTA
# =========================================================

class BarberResponse(BaseModel):

    id: int

    user_id: int

    barbershop_id: int


    # -----------------------------------------------------
    # INFORMACIÓN DEL USUARIO
    # -----------------------------------------------------

    first_name: str

    last_name: str


    # -----------------------------------------------------
    # INFORMACIÓN DEL BARBERO
    # -----------------------------------------------------

    bio: str | None

    years_experience: int | None

    accepts_home_service: bool

    is_active: bool

    service_ids: list[int]


    created_at: datetime

    updated_at: datetime


    model_config = ConfigDict(
        from_attributes=True
    )