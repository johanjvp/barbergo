from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# =========================================================
# BASE
# =========================================================

class BarbershopSettingsBase(BaseModel):

    # =====================================================
    # CONTROL GENERAL
    # =====================================================

    bookings_enabled: bool


    # =====================================================
    # RESERVAS
    # =====================================================

    auto_confirm_bookings: bool

    allow_same_day_booking: bool

    min_booking_notice_minutes: int = Field(
        ge=0,
        le=10080,
    )

    max_booking_days_ahead: int = Field(
        ge=1,
        le=365,
    )

    booking_interval_minutes: int = Field(
        ge=5,
        le=120,
    )

    buffer_between_bookings_minutes: int = Field(
        ge=0,
        le=180,
    )

    allow_overbooking: bool


    # =====================================================
    # CANCELACIONES
    # =====================================================

    allow_customer_cancellation: bool

    cancellation_limit_minutes: int = Field(
        ge=0,
        le=43200,
    )


    # =====================================================
    # REPROGRAMACIONES
    # =====================================================

    allow_reschedule: bool

    reschedule_limit_minutes: int = Field(
        ge=0,
        le=43200,
    )


    # =====================================================
    # SELECCIÓN DE BARBERO
    # =====================================================

    customer_can_choose_barber: bool

    allow_any_available_barber: bool


    # =====================================================
    # CLIENTES
    # =====================================================

    require_customer_account: bool

    require_customer_phone: bool

    allow_customer_notes: bool


    # =====================================================
    # PERMISOS DEL BARBERO
    # =====================================================

    barber_can_confirm_bookings: bool

    barber_can_cancel_bookings: bool

    barber_can_start_service: bool

    barber_can_complete_service: bool

    barber_can_block_schedule: bool

    barber_can_edit_schedule: bool


    # =====================================================
    # OPERACIÓN
    # =====================================================

    tolerance_minutes: int = Field(
        ge=0,
        le=120,
    )


    # =====================================================
    # NOTIFICACIONES
    # =====================================================

    notify_barber_new_booking: bool

    notify_barber_cancellation: bool

    notify_customer_confirmation: bool

    notify_customer_cancellation: bool

    send_booking_reminders: bool

    reminder_minutes_before: int = Field(
        ge=0,
        le=10080,
    )


# =========================================================
# ACTUALIZAR CONFIGURACIÓN
# TODOS LOS CAMPOS SON OPCIONALES
# =========================================================

class BarbershopSettingsUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )


    # =====================================================
    # GENERAL
    # =====================================================

    bookings_enabled: bool | None = None


    # =====================================================
    # RESERVAS
    # =====================================================

    auto_confirm_bookings: bool | None = None

    allow_same_day_booking: bool | None = None

    min_booking_notice_minutes: int | None = Field(
        default=None,
        ge=0,
        le=10080,
    )

    max_booking_days_ahead: int | None = Field(
        default=None,
        ge=1,
        le=365,
    )

    booking_interval_minutes: int | None = Field(
        default=None,
        ge=5,
        le=120,
    )

    buffer_between_bookings_minutes: int | None = Field(
        default=None,
        ge=0,
        le=180,
    )

    allow_overbooking: bool | None = None


    # =====================================================
    # CANCELACIONES
    # =====================================================

    allow_customer_cancellation: bool | None = None

    cancellation_limit_minutes: int | None = Field(
        default=None,
        ge=0,
        le=43200,
    )


    # =====================================================
    # REPROGRAMACIONES
    # =====================================================

    allow_reschedule: bool | None = None

    reschedule_limit_minutes: int | None = Field(
        default=None,
        ge=0,
        le=43200,
    )


    # =====================================================
    # SELECCIÓN DE BARBERO
    # =====================================================

    customer_can_choose_barber: bool | None = None

    allow_any_available_barber: bool | None = None


    # =====================================================
    # CLIENTES
    # =====================================================

    require_customer_account: bool | None = None

    require_customer_phone: bool | None = None

    allow_customer_notes: bool | None = None


    # =====================================================
    # PERMISOS BARBERO
    # =====================================================

    barber_can_confirm_bookings: bool | None = None

    barber_can_cancel_bookings: bool | None = None

    barber_can_start_service: bool | None = None

    barber_can_complete_service: bool | None = None

    barber_can_block_schedule: bool | None = None

    barber_can_edit_schedule: bool | None = None


    # =====================================================
    # OPERACIÓN
    # =====================================================

    tolerance_minutes: int | None = Field(
        default=None,
        ge=0,
        le=120,
    )


    # =====================================================
    # NOTIFICACIONES
    # =====================================================

    notify_barber_new_booking: bool | None = None

    notify_barber_cancellation: bool | None = None

    notify_customer_confirmation: bool | None = None

    notify_customer_cancellation: bool | None = None

    send_booking_reminders: bool | None = None

    reminder_minutes_before: int | None = Field(
        default=None,
        ge=0,
        le=10080,
    )


    # =====================================================
    # VALIDAR QUE SE ENVÍE AL MENOS UN CAMPO
    # =====================================================

    @model_validator(mode="after")
    def validate_not_empty(self):

        values = self.model_dump(
            exclude_none=True
        )

        if not values:
            raise ValueError(
                "Debes enviar al menos una configuración para actualizar."
            )

        return self


# =========================================================
# ACTIVAR / DESACTIVAR CONFIRMACIÓN AUTOMÁTICA
# =========================================================

class AutoConfirmBookingUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    enabled: bool


# =========================================================
# RESPUESTA DE CONFIGURACIÓN
# =========================================================

class BarbershopSettingsResponse(
    BarbershopSettingsBase
):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    barbershop_id: int

    barbershop_name: str

    barbershop_is_active: bool

    created_at: datetime | None = None

    updated_at: datetime | None = None


# =========================================================
# RESPUESTA SIMPLE DE CAMBIO
# =========================================================

class BarbershopSettingActionResponse(
    BaseModel
):

    barbershop_id: int

    updated: bool

    message: str

    settings: BarbershopSettingsResponse