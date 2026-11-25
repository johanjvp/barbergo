from sqlalchemy import text
from sqlalchemy.orm import Session


class BarbershopSettingsRepository:

    # =====================================================
    # CAMPOS QUE PUEDEN MODIFICARSE
    # =====================================================

    ALLOWED_FIELDS = {

        # GENERAL
        "bookings_enabled",

        # RESERVAS
        "auto_confirm_bookings",
        "allow_same_day_booking",
        "min_booking_notice_minutes",
        "max_booking_days_ahead",
        "booking_interval_minutes",
        "buffer_between_bookings_minutes",
        "allow_overbooking",

        # CANCELACIÓN
        "allow_customer_cancellation",
        "cancellation_limit_minutes",

        # REPROGRAMACIÓN
        "allow_reschedule",
        "reschedule_limit_minutes",

        # BARBERO
        "customer_can_choose_barber",
        "allow_any_available_barber",

        # CLIENTE
        "require_customer_account",
        "require_customer_phone",
        "allow_customer_notes",

        # PERMISOS BARBERO
        "barber_can_confirm_bookings",
        "barber_can_cancel_bookings",
        "barber_can_start_service",
        "barber_can_complete_service",
        "barber_can_block_schedule",
        "barber_can_edit_schedule",

        # OPERACIÓN
        "tolerance_minutes",

        # NOTIFICACIONES
        "notify_barber_new_booking",
        "notify_barber_cancellation",
        "notify_customer_confirmation",
        "notify_customer_cancellation",
        "send_booking_reminders",
        "reminder_minutes_before"
    }


    # =====================================================
    # OBTENER CONFIGURACIÓN DE BARBERÍA
    # =====================================================

    @staticmethod
    def get_by_barbershop(
        db: Session,
        barbershop_id: int
    ) -> dict | None:

        row = (
            db.execute(
                text(
                    """
                    SELECT

                        bs.id,

                        bs.barbershop_id,

                        b.name AS barbershop_name,

                        b.is_active AS barbershop_is_active,


                        -- =================================
                        -- GENERAL
                        -- =================================

                        bs.bookings_enabled,


                        -- =================================
                        -- RESERVAS
                        -- =================================

                        bs.auto_confirm_bookings,

                        bs.allow_same_day_booking,

                        bs.min_booking_notice_minutes,

                        bs.max_booking_days_ahead,

                        bs.booking_interval_minutes,

                        bs.buffer_between_bookings_minutes,

                        bs.allow_overbooking,


                        -- =================================
                        -- CANCELACIÓN
                        -- =================================

                        bs.allow_customer_cancellation,

                        bs.cancellation_limit_minutes,


                        -- =================================
                        -- REPROGRAMACIÓN
                        -- =================================

                        bs.allow_reschedule,

                        bs.reschedule_limit_minutes,


                        -- =================================
                        -- SELECCIÓN DE BARBERO
                        -- =================================

                        bs.customer_can_choose_barber,

                        bs.allow_any_available_barber,


                        -- =================================
                        -- CLIENTES
                        -- =================================

                        bs.require_customer_account,

                        bs.require_customer_phone,

                        bs.allow_customer_notes,


                        -- =================================
                        -- PERMISOS DEL BARBERO
                        -- =================================

                        bs.barber_can_confirm_bookings,

                        bs.barber_can_cancel_bookings,

                        bs.barber_can_start_service,

                        bs.barber_can_complete_service,

                        bs.barber_can_block_schedule,

                        bs.barber_can_edit_schedule,


                        -- =================================
                        -- OPERACIÓN
                        -- =================================

                        bs.tolerance_minutes,


                        -- =================================
                        -- NOTIFICACIONES
                        -- =================================

                        bs.notify_barber_new_booking,

                        bs.notify_barber_cancellation,

                        bs.notify_customer_confirmation,

                        bs.notify_customer_cancellation,

                        bs.send_booking_reminders,

                        bs.reminder_minutes_before,


                        -- =================================
                        -- AUDITORÍA
                        -- =================================

                        bs.created_at,

                        bs.updated_at


                    FROM barbershop_settings bs

                    INNER JOIN barbershops b
                        ON b.id = bs.barbershop_id

                    WHERE
                        bs.barbershop_id =
                            :barbershop_id

                    LIMIT 1
                    """
                ),
                {
                    "barbershop_id":
                        barbershop_id
                }
            )
            .mappings()
            .first()
        )


        if not row:

            return None


        return (
            BarbershopSettingsRepository
            ._serialize(
                row
            )
        )


    # =====================================================
    # VERIFICAR BARBERÍA
    # =====================================================

    @staticmethod
    def barbershop_exists(
        db: Session,
        barbershop_id: int
    ) -> bool:

        result = (
            db.execute(
                text(
                    """
                    SELECT
                        id

                    FROM barbershops

                    WHERE
                        id = :barbershop_id

                    LIMIT 1
                    """
                ),
                {
                    "barbershop_id":
                        barbershop_id
                }
            )
            .scalar()
        )


        return (
            result is not None
        )


    # =====================================================
    # CREAR CONFIGURACIÓN SI NO EXISTE
    # =====================================================

    @staticmethod
    def create_default_if_missing(
        db: Session,
        barbershop_id: int
    ) -> dict | None:

        if not (
            BarbershopSettingsRepository
            .barbershop_exists(
                db=db,
                barbershop_id=barbershop_id
            )
        ):

            return None


        existing = (
            BarbershopSettingsRepository
            .get_by_barbershop(
                db=db,
                barbershop_id=barbershop_id
            )
        )


        if existing:

            return existing


        # -------------------------------------------------
        # TOMAR CONFIGURACIÓN LEGACY DE BARBERSHOPS
        # -------------------------------------------------

        legacy = (
            db.execute(
                text(
                    """
                    SELECT

                        requires_manual_confirmation,

                        cancellation_hours_before,

                        tolerance_minutes

                    FROM barbershops

                    WHERE
                        id = :barbershop_id

                    LIMIT 1
                    """
                ),
                {
                    "barbershop_id":
                        barbershop_id
                }
            )
            .mappings()
            .first()
        )


        if not legacy:

            return None


        auto_confirm = (
            0
            if
            bool(
                legacy[
                    "requires_manual_confirmation"
                ]
            )
            else
            1
        )


        cancellation_minutes = (
            int(
                legacy[
                    "cancellation_hours_before"
                ]
                or 2
            )
            *
            60
        )


        tolerance_minutes = (
            int(
                legacy[
                    "tolerance_minutes"
                ]
                or 10
            )
        )


        try:

            db.execute(
                text(
                    """
                    INSERT INTO barbershop_settings (

                        barbershop_id,

                        auto_confirm_bookings,

                        cancellation_limit_minutes,

                        tolerance_minutes

                    )

                    VALUES (

                        :barbershop_id,

                        :auto_confirm_bookings,

                        :cancellation_limit_minutes,

                        :tolerance_minutes

                    )
                    """
                ),
                {
                    "barbershop_id":
                        barbershop_id,

                    "auto_confirm_bookings":
                        auto_confirm,

                    "cancellation_limit_minutes":
                        cancellation_minutes,

                    "tolerance_minutes":
                        tolerance_minutes
                }
            )


            db.commit()


        except Exception:

            db.rollback()

            raise


        return (
            BarbershopSettingsRepository
            .get_by_barbershop(
                db=db,
                barbershop_id=barbershop_id
            )
        )


    # =====================================================
    # ACTUALIZAR CONFIGURACIÓN
    # =====================================================

    @staticmethod
    def update_settings(
        db: Session,
        barbershop_id: int,
        values: dict
    ) -> dict | None:

        existing = (
            BarbershopSettingsRepository
            .create_default_if_missing(
                db=db,
                barbershop_id=barbershop_id
            )
        )


        if not existing:

            return None


        # -------------------------------------------------
        # FILTRAR SOLO CAMPOS AUTORIZADOS
        # -------------------------------------------------

        clean_values = {

            key: value

            for key, value
            in values.items()

            if key
            in
            BarbershopSettingsRepository
            .ALLOWED_FIELDS

        }


        if not clean_values:

            return existing


        # -------------------------------------------------
        # CONSTRUIR UPDATE SOLO CON CAMPOS PERMITIDOS
        # -------------------------------------------------

        set_parts = []


        params = {
            "barbershop_id":
                barbershop_id
        }


        for key, value in clean_values.items():

            set_parts.append(
                f"{key} = :{key}"
            )

            params[key] = value


        set_clause = (
            ", ".join(
                set_parts
            )
        )


        try:

            db.execute(
                text(
                    f"""
                    UPDATE barbershop_settings

                    SET

                        {set_clause},

                        updated_at =
                            CURRENT_TIMESTAMP

                    WHERE
                        barbershop_id =
                            :barbershop_id
                    """
                ),
                params
            )


            db.commit()


        except Exception:

            db.rollback()

            raise


        return (
            BarbershopSettingsRepository
            .get_by_barbershop(
                db=db,
                barbershop_id=barbershop_id
            )
        )


    # =====================================================
    # ACTUALIZAR SOLO CONFIRMACIÓN AUTOMÁTICA
    # =====================================================

    @staticmethod
    def update_auto_confirmation(
        db: Session,
        barbershop_id: int,
        enabled: bool
    ) -> dict | None:

        return (
            BarbershopSettingsRepository
            .update_settings(
                db=db,
                barbershop_id=barbershop_id,
                values={
                    "auto_confirm_bookings":
                        bool(enabled)
                }
            )
        )


    # =====================================================
    # SERIALIZAR
    # =====================================================

    @staticmethod
    def _serialize(
        row
    ) -> dict:

        boolean_fields = {

            "barbershop_is_active",

            "bookings_enabled",

            "auto_confirm_bookings",

            "allow_same_day_booking",

            "allow_overbooking",

            "allow_customer_cancellation",

            "allow_reschedule",

            "customer_can_choose_barber",

            "allow_any_available_barber",

            "require_customer_account",

            "require_customer_phone",

            "allow_customer_notes",

            "barber_can_confirm_bookings",

            "barber_can_cancel_bookings",

            "barber_can_start_service",

            "barber_can_complete_service",

            "barber_can_block_schedule",

            "barber_can_edit_schedule",

            "notify_barber_new_booking",

            "notify_barber_cancellation",

            "notify_customer_confirmation",

            "notify_customer_cancellation",

            "send_booking_reminders"
        }


        integer_fields = {

            "id",

            "barbershop_id",

            "min_booking_notice_minutes",

            "max_booking_days_ahead",

            "booking_interval_minutes",

            "buffer_between_bookings_minutes",

            "cancellation_limit_minutes",

            "reschedule_limit_minutes",

            "tolerance_minutes",

            "reminder_minutes_before"
        }


        result = {}


        for key, value in row.items():

            if key in boolean_fields:

                result[key] = bool(
                    value
                )


            elif key in integer_fields:

                result[key] = (
                    int(value)
                    if value is not None
                    else 0
                )


            elif key in {
                "created_at",
                "updated_at"
            }:

                result[key] = (
                    value.isoformat()
                    if value
                    else None
                )


            else:

                result[key] = value


        return result