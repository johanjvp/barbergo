from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field
)


class BarbershopCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=150
    )

    description: str | None = None

    address: str = Field(
        min_length=5,
        max_length=255
    )

    neighborhood: str | None = Field(
        default=None,
        max_length=120
    )

    city: str = "Barranquilla"

    department: str = "Atlántico"

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180
    )

    phone: str | None = Field(
        default=None,
        max_length=30
    )

    email: EmailStr | None = None

    only_men: bool = False

    offers_vip: bool = False

    offers_home_service: bool = False

    requires_manual_confirmation: bool = False

    cancellation_hours_before: int = Field(
        default=2,
        ge=0,
        le=168
    )

    tolerance_minutes: int = Field(
        default=10,
        ge=0,
        le=60
    )

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


class BarbershopUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    description: str | None = None

    address: str | None = Field(
        default=None,
        min_length=5,
        max_length=255
    )

    neighborhood: str | None = None

    city: str | None = None

    department: str | None = None

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180
    )

    phone: str | None = None

    email: EmailStr | None = None

    only_men: bool | None = None

    offers_vip: bool | None = None

    offers_home_service: bool | None = None

    requires_manual_confirmation: bool | None = None

    cancellation_hours_before: int | None = Field(
        default=None,
        ge=0,
        le=168
    )

    tolerance_minutes: int | None = Field(
        default=None,
        ge=0,
        le=60
    )

    is_active: bool | None = None

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


class BarbershopResponse(BaseModel):

    id: int
    owner_user_id: int

    name: str
    description: str | None

    address: str
    neighborhood: str | None

    city: str
    department: str

    latitude: float | None
    longitude: float | None

    phone: str | None
    email: str | None

    only_men: bool
    offers_vip: bool
    offers_home_service: bool

    requires_manual_confirmation: bool

    cancellation_hours_before: int
    tolerance_minutes: int

    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )