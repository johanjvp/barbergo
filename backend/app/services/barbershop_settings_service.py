from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.barbershop_settings_repository import (
    BarbershopSettingsRepository
)

from app.schemas.barbershop_settings_schema import (
    BarbershopSettingsUpdate
)


class BarbershopSettingsService:

    # =====================================================
    # OBTENER CONFIGURACIÓN
    # =====================================================

    @staticmethod
    def get_settings(
        db: Session,
        barbershop_id: int
    ) -> dict:

        # -------------------------------------------------
        # VALIDAR ID
        # -------------------------------------------------

        if barbershop_id <= 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "La barbería indicada "
                    "no es válida."
                )
            )


        # -------------------------------------------------
        # OBTENER O CREAR CONFIGURACIÓN
        # -------------------------------------------------

        settings = (
            BarbershopSettingsRepository
            .create_default_if_missing(
                db=db,
                barbershop_id=barbershop_id
            )
        )


        if settings is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "La barbería no existe."
                )
            )


        return settings


    # =====================================================
    # ACTUALIZAR CONFIGURACIÓN
    # =====================================================

    @staticmethod
    def update_settings(
        db: Session,
        barbershop_id: int,
        payload: BarbershopSettingsUpdate
    ) -> dict:

        # -------------------------------------------------
        # VALIDAR ID
        # -------------------------------------------------

        if barbershop_id <= 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "La barbería indicada "
                    "no es válida."
                )
            )


        # -------------------------------------------------
        # CONFIGURACIÓN ACTUAL
        # -------------------------------------------------

        current_settings = (
            BarbershopSettingsService
            .get_settings(
                db=db,
                barbershop_id=barbershop_id
            )
        )


        # -------------------------------------------------
        # CAMPOS ENVIADOS
        # -------------------------------------------------

        values = (
            payload.model_dump(
                exclude_unset=True,
                exclude_none=True
            )
        )


        if not values:

            raise HTTPException(
                status_code=400,
                detail=(
                    "No se enviaron "
                    "configuraciones para actualizar."
                )
            )


        # -------------------------------------------------
        # ESTADO RESULTANTE
        # -------------------------------------------------
        # Se mezclan los valores actuales
        # con los nuevos antes de guardar.
        # -------------------------------------------------

        merged_settings = {
            **current_settings,
            **values
        }


        # -------------------------------------------------
        # VALIDAR REGLAS DE NEGOCIO
        # -------------------------------------------------

        (
            BarbershopSettingsService
            ._validate_business_rules(
                merged_settings
            )
        )


        # -------------------------------------------------
        # ACTUALIZAR
        # -------------------------------------------------

        updated_settings = (
            BarbershopSettingsRepository
            .update_settings(
                db=db,
                barbershop_id=barbershop_id,
                values=values
            )
        )


        if updated_settings is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No fue posible encontrar "
                    "la barbería."
                )
            )


        return {
            "barbershop_id":
                barbershop_id,

            "updated":
                True,

            "message":
                "Configuración actualizada correctamente.",

            "settings":
                updated_settings
        }


    # =====================================================
    # CAMBIAR CONFIRMACIÓN AUTOMÁTICA
    # =====================================================

    @staticmethod
    def update_auto_confirmation(
        db: Session,
        barbershop_id: int,
        enabled: bool
    ) -> dict:

        # -------------------------------------------------
        # VALIDAR BARBERÍA
        # -------------------------------------------------

        current_settings = (
            BarbershopSettingsService
            .get_settings(
                db=db,
                barbershop_id=barbershop_id
            )
        )


        # -------------------------------------------------
        # EVITAR UPDATE INNECESARIO
        # -------------------------------------------------

        if (
            current_settings[
                "auto_confirm_bookings"
            ]
            ==
            enabled
        ):

            return {
                "barbershop_id":
                    barbershop_id,

                "updated":
                    False,

                "message":
                    (
                        "La confirmación automática "
                        "ya se encuentra "
                        +
                        (
                            "activada."
                            if enabled
                            else
                            "desactivada."
                        )
                    ),

                "settings":
                    current_settings
            }


        # -------------------------------------------------
        # ACTUALIZAR
        # -------------------------------------------------

        updated_settings = (
            BarbershopSettingsRepository
            .update_auto_confirmation(
                db=db,
                barbershop_id=barbershop_id,
                enabled=enabled
            )
        )


        if updated_settings is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "La barbería no existe."
                )
            )


        return {
            "barbershop_id":
                barbershop_id,

            "updated":
                True,

            "message":
                (
                    "Confirmación automática "
                    +
                    (
                        "activada correctamente."
                        if enabled
                        else
                        "desactivada correctamente."
                    )
                ),

            "settings":
                updated_settings
        }


    # =====================================================
    # VALIDAR REGLAS DE NEGOCIO
    # =====================================================

    @staticmethod
    def _validate_business_rules(
        settings: dict
    ) -> None:

        # =================================================
        # ANTICIPACIÓN MÍNIMA VS HORIZONTE MÁXIMO
        # =================================================

        min_notice = int(
            settings.get(
                "min_booking_notice_minutes",
                0
            )
            or 0
        )


        max_days = int(
            settings.get(
                "max_booking_days_ahead",
                30
            )
            or 30
        )


        max_minutes = (
            max_days
            *
            24
            *
            60
        )


        if (
            min_notice >
            max_minutes
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "La anticipación mínima "
                    "de una reserva no puede "
                    "ser superior al período "
                    "máximo permitido para reservar."
                )
            )


        # =================================================
        # SELECCIÓN / ASIGNACIÓN DE BARBERO
        # =================================================
        #
        # Debe existir al menos una forma
        # de determinar qué barbero realizará
        # el servicio.
        #
        # Puede ser:
        #
        # 1. El cliente elige al barbero.
        # 2. El cliente selecciona
        #    cualquier barbero disponible.
        #
        # =================================================

        customer_can_choose = bool(
            settings.get(
                "customer_can_choose_barber",
                True
            )
        )


        allow_any_barber = bool(
            settings.get(
                "allow_any_available_barber",
                True
            )
        )


        if (
            not customer_can_choose
            and
            not allow_any_barber
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Debe existir al menos "
                    "una forma de asignar el barbero: "
                    "permitir que el cliente lo elija "
                    "o permitir seleccionar cualquier "
                    "barbero disponible."
                )
            )


        # =================================================
        # INTERVALO DE AGENDA
        # =================================================

        booking_interval = int(
            settings.get(
                "booking_interval_minutes",
                15
            )
            or 15
        )


        allowed_intervals = {
            5,
            10,
            15,
            20,
            30,
            45,
            60
        }


        if (
            booking_interval
            not in
            allowed_intervals
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "El intervalo de agenda debe "
                    "ser de 5, 10, 15, 20, 30, "
                    "45 o 60 minutos."
                )
            )


        # =================================================
        # BUFFER ENTRE SERVICIOS
        # =================================================

        buffer_minutes = int(
            settings.get(
                "buffer_between_bookings_minutes",
                0
            )
            or 0
        )


        allowed_buffers = {
            0,
            5,
            10,
            15,
            20,
            30,
            45,
            60
        }


        if (
            buffer_minutes
            not in
            allowed_buffers
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "El tiempo entre servicios "
                    "debe ser de 0, 5, 10, 15, "
                    "20, 30, 45 o 60 minutos."
                )
            )


        # =================================================
        # RECORDATORIOS
        # =================================================

        send_reminders = bool(
            settings.get(
                "send_booking_reminders",
                True
            )
        )


        reminder_minutes = int(
            settings.get(
                "reminder_minutes_before",
                120
            )
            or 0
        )


        if (
            send_reminders
            and
            reminder_minutes <= 0
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Si los recordatorios están "
                    "activados, debes indicar "
                    "con cuánta anticipación "
                    "se enviarán."
                )
            )


        # =================================================
        # CANCELACIÓN
        # =================================================

        allow_cancellation = bool(
            settings.get(
                "allow_customer_cancellation",
                True
            )
        )


        cancellation_limit = int(
            settings.get(
                "cancellation_limit_minutes",
                120
            )
            or 0
        )


        if (
            allow_cancellation
            and
            cancellation_limit < 0
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "El límite de cancelación "
                    "no puede ser negativo."
                )
            )


        # =================================================
        # REPROGRAMACIÓN
        # =================================================

        allow_reschedule = bool(
            settings.get(
                "allow_reschedule",
                True
            )
        )


        reschedule_limit = int(
            settings.get(
                "reschedule_limit_minutes",
                120
            )
            or 0
        )


        if (
            allow_reschedule
            and
            reschedule_limit < 0
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "El límite de reprogramación "
                    "no puede ser negativo."
                )
            )