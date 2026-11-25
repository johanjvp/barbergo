from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)


# =========================================================
# CREAR RESERVA
# =========================================================

class HomeAddress(BaseModel):
    address: str = Field(min_length=6, max_length=300)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    access_notes: str | None = Field(default=None, max_length=300)

    model_config = ConfigDict(str_strip_whitespace=True)


class BookingCreate(BaseModel):
    booking_type: Literal["IN_SHOP", "HOME"] = "IN_SHOP"
    home: HomeAddress | None = None
    payment_method: Literal[
        "CASH", "BANK_TRANSFER", "DEPOSIT", "NEQUI", "DAVIPLATA"
    ] | None = None


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

    client_user_id: int | None = None

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
    guest_name: str | None = None
    guest_email: str | None = None
    booking_type: str = "IN_SHOP"
    home_address: str | None = None
    home_latitude: Decimal | None = None
    home_longitude: Decimal | None = None
    home_access_notes: str | None = None
    home_fee: Decimal = Decimal("0")
    payment_method: str | None = None
    payment_status: str = "PENDING"
    payment_reference: str | None = None
