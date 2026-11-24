from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)


# =========================================================
# CREAR RESERVA
# =========================================================

class BookingCreate(BaseModel):

    barber_id: int = Field(
        gt=0
    )

    service_id: int = Field(
        gt=0
    )

    start_at: datetime

    customer_notes: str | None = Field(
        default=None,
        max_length=500
    )


    @field_validator("start_at")
    @classmethod
    def validate_start_at(
        cls,
        value: datetime
    ):

        # Por ahora nuestra BD maneja DATETIME
        # sin zona horaria.

        if value.tzinfo is not None:

            raise ValueError(
                "start_at debe enviarse "
                "sin zona horaria."
            )

        return value


    model_config = ConfigDict(
        str_strip_whitespace=True
    )


# =========================================================
# RESPUESTA
# =========================================================

class BookingResponse(BaseModel):

    id: int

    client_user_id: int

    barbershop_id: int
    barber_id: int
    service_id: int

    status_id: int
    status_code: str

    start_at: datetime
    end_at: datetime

    service_price: Decimal

    customer_notes: str | None
    barber_notes: str | None

    created_at: datetime
    updated_at: datetime