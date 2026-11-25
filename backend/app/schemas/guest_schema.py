from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.booking_schema import BookingCreate, BookingResponse


class GuestCodeRequest(BaseModel):
    email: EmailStr

    model_config = ConfigDict(str_strip_whitespace=True)


class GuestCodeResponse(BaseModel):
    sent: bool = True
    expires_in_minutes: int


class GuestBookingCreate(BookingCreate):
    """Reserva sin cuenta: datos de contacto + código enviado al correo."""

    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)
    code: str = Field(min_length=6, max_length=6, pattern=r"^[0-9]{6}$")
    accept_terms: bool

    @field_validator("accept_terms")
    @classmethod
    def must_accept(cls, value: bool):
        if not value:
            raise ValueError("Debes aceptar el tratamiento de tus datos para reservar.")
        return value


class GuestBookingCreated(BookingResponse):
    manage_token: str


class GuestBookingView(BaseModel):
    id: int
    status_code: str
    start_at: datetime
    end_at: datetime
    guest_name: str | None
    barbershop_name: str
    barbershop_address: str | None
    barbershop_phone: str | None
    service_name: str
    barber_name: str
    service_price: Decimal
    home_fee: Decimal
    booking_type: str
    home_address: str | None
    can_cancel: bool
    cancel_deadline: datetime | None
    cancellation_hours_before: int
    payment_method: str | None = None
    payment_status: str = "PENDING"
    payment_reference: str | None = None
    payment_details: dict | None = None
