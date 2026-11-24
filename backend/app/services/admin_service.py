import os


from datetime import (
    date,
    timedelta
)

from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.admin_repository import (
    AdminRepository
)


class AdminService:



    # =====================================================
    # OBTENER COMISIÓN CONFIGURADA
    # =====================================================

    @staticmethod
    def _get_commission_rate() -> float:

        raw_value = (
            os.getenv(
                "PLATFORM_COMMISSION_RATE",
                "0.10"
            )
        )


        try:

            rate = float(
                raw_value
            )

        except (
            TypeError,
            ValueError
        ):

            rate = 0.10


        # -------------------------------------------------
        # SEGURIDAD
        # -------------------------------------------------
        # La comisión debe estar entre 0 y 1.
        #
        # Ejemplo:
        # 0.10 = 10 %
        # 0.15 = 15 %
        # -------------------------------------------------

        if (
            rate < 0
            or
            rate > 1
        ):

            rate = 0.10


        return rate


    # =====================================================
    # COMPLETAR SERIE DE 30 DÍAS
    # =====================================================

    @staticmethod
    def _build_30_day_series(
        raw_data: list[dict]
    ) -> list[dict]:

        data_map = {

            str(
                item[
                    "date"
                ]
            ):
                int(
                    item[
                        "total"
                    ]
                    or 0
                )

            for item in raw_data

        }


        today = (
            date.today()
        )


        series = []


        for days_ago in range(
            29,
            -1,
            -1
        ):

            current_date = (
                today
                -
                timedelta(
                    days=days_ago
                )
            )


            date_key = (
                current_date
                .isoformat()
            )


            series.append(
                {

                    "date":
                        date_key,

                    "total":
                        data_map
                        .get(
                            date_key,
                            0
                        )

                }
            )


        return series


    # =====================================================
    # DASHBOARD GENERAL
    # =====================================================

    @staticmethod
    def get_dashboard(
        db: Session
    ) -> dict:

        # =================================================
        # USUARIOS
        # =================================================

        users_total = (
            AdminRepository
            .count_users(
                db
            )
        )


        users_today = (
            AdminRepository
            .count_users_today(
                db
            )
        )


        users_this_week = (
            AdminRepository
            .count_users_this_week(
                db
            )
        )


        users_this_month = (
            AdminRepository
            .count_users_this_month(
                db
            )
        )


        unique_customers = (
            AdminRepository
            .count_unique_customers(
                db
            )
        )


        returning_customers = (
            AdminRepository
            .count_returning_customers(
                db
            )
        )


        # =================================================
        # TASA DE RECURRENCIA
        # =================================================

        if (
            unique_customers > 0
        ):

            returning_customer_rate = (
                round(
                    (
                        returning_customers
                        /
                        unique_customers
                    )
                    *
                    100,
                    2
                )
            )

        else:

            returning_customer_rate = 0.0


        # =================================================
        # BARBERÍAS
        # =================================================

        barbershops_total = (
            AdminRepository
            .count_barbershops(
                db
            )
        )


        barbershops_active = (
            AdminRepository
            .count_active_barbershops(
                db
            )
        )


        barbershops_inactive = (
            max(
                barbershops_total
                -
                barbershops_active,
                0
            )
        )


        barbershops_new_this_month = (
            AdminRepository
            .count_new_barbershops_this_month(
                db
            )
        )


        # =================================================
        # RESERVAS
        # =================================================

        bookings_total = (
            AdminRepository
            .count_bookings(
                db
            )
        )


        bookings_today = (
            AdminRepository
            .count_bookings_today(
                db
            )
        )


        bookings_this_week = (
            AdminRepository
            .count_bookings_this_week(
                db
            )
        )


        bookings_this_month = (
            AdminRepository
            .count_bookings_this_month(
                db
            )
        )


        # =================================================
        # ESTADOS
        # =================================================

        status_counts = (
            AdminRepository
            .booking_status_counts(
                db
            )
        )


        pending = (
            status_counts
            .get(
                "PENDING",
                0
            )
        )


        confirmed = (
            status_counts
            .get(
                "CONFIRMED",
                0
            )
        )


        in_progress = (
            status_counts
            .get(
                "IN_PROGRESS",
                0
            )
        )


        completed = (
            status_counts
            .get(
                "COMPLETED",
                0
            )
        )


        cancelled_by_customer = (
            status_counts
            .get(
                "CANCELLED_BY_CUSTOMER",
                0
            )
        )


        cancelled_by_barber = (
            status_counts
            .get(
                "CANCELLED_BY_BARBER",
                0
            )
        )


        cancelled_by_admin = (
            status_counts
            .get(
                "CANCELLED_BY_ADMIN",
                0
            )
        )


        cancelled = (
            cancelled_by_customer
            +
            cancelled_by_barber
            +
            cancelled_by_admin
        )


        no_show = (
            status_counts
            .get(
                "NO_SHOW",
                0
            )
        )


        rejected = (
            status_counts
            .get(
                "REJECTED",
                0
            )
        )


        cancellation_rate = (
            AdminRepository
            .cancellation_rate(
                db
            )
        )


        no_show_rate = (
            AdminRepository
            .no_show_rate(
                db
            )
        )


        # =================================================
        # FINANCIERO OPERATIVO
        # =================================================

        financial = (
            AdminRepository
            .financial_summary(
                db
            )
        )


        reserved_value = (
            financial[
                "reserved_value"
            ]
        )


        average_ticket = (
            financial[
                "average_ticket"
            ]
        )


        reserved_value_today = (
            AdminRepository
            .reserved_value_today(
                db
            )
        )


        reserved_value_this_month = (
            AdminRepository
            .reserved_value_this_month(
                db
            )
        )


        completed_value_this_month = (
            AdminRepository
            .completed_value_this_month(
                db
            )
        )


        # =================================================
        # SIMULACIÓN FINANCIERA
        # =================================================

        simulation_base = (
            AdminRepository
            .financial_simulation_base(
                db
            )
        )


        commission_rate = (
            AdminService
            ._get_commission_rate()
        )


        commission_percentage = (
            round(
                commission_rate
                *
                100,
                2
            )
        )


        gross_booking_value = (
            simulation_base[
                "gross_booking_value"
            ]
        )


        completed_value = (
            simulation_base[
                "completed_value"
            ]
        )


        cancelled_value = (
            simulation_base[
                "cancelled_value"
            ]
        )


        no_show_value = (
            simulation_base[
                "no_show_value"
            ]
        )


        rejected_value = (
            simulation_base[
                "rejected_value"
            ]
        )


        # -------------------------------------------------
        # PROYECCIÓN SOBRE TODAS LAS RESERVAS VÁLIDAS
        # -------------------------------------------------

        projected_platform_revenue = (
            gross_booking_value
            *
            commission_rate
        )


        projected_barbershop_payout = (
            gross_booking_value
            -
            projected_platform_revenue
        )


        # -------------------------------------------------
        # RESERVAS COMPLETADAS
        # -------------------------------------------------

        completed_platform_revenue = (
            completed_value
            *
            commission_rate
        )


        completed_barbershop_payout = (
            completed_value
            -
            completed_platform_revenue
        )


        # -------------------------------------------------
        # MES ACTUAL
        # -------------------------------------------------

        projected_platform_revenue_this_month = (
            reserved_value_this_month
            *
            commission_rate
        )


        projected_barbershop_payout_this_month = (
            reserved_value_this_month
            -
            projected_platform_revenue_this_month
        )


        completed_platform_revenue_this_month = (
            completed_value_this_month
            *
            commission_rate
        )


        completed_barbershop_payout_this_month = (
            completed_value_this_month
            -
            completed_platform_revenue_this_month
        )


        # =================================================
        # VALOR POTENCIAL PERDIDO
        # =================================================

        lost_value = (
            cancelled_value
            +
            no_show_value
            +
            rejected_value
        )


        lost_platform_revenue = (
            lost_value
            *
            commission_rate
        )


        # =================================================
        # CRECIMIENTO DE USUARIOS
        # =================================================

        raw_users_growth = (
            AdminRepository
            .users_growth_last_30_days(
                db
            )
        )


        users_growth = (
            AdminService
            ._build_30_day_series(
                raw_users_growth
            )
        )


        # =================================================
        # CRECIMIENTO DE RESERVAS
        # =================================================

        raw_bookings_growth = (
            AdminRepository
            .bookings_growth_last_30_days(
                db
            )
        )


        bookings_growth = (
            AdminService
            ._build_30_day_series(
                raw_bookings_growth
            )
        )


        # =================================================
        # RANKINGS
        # =================================================

        top_barbershops = (
            AdminRepository
            .top_barbershops(
                db,
                limit=5
            )
        )


        top_services = (
            AdminRepository
            .top_services(
                db,
                limit=5
            )
        )


        top_barbers = (
            AdminRepository
            .top_barbers(
                db,
                limit=5
            )
        )


        # =================================================
        # RESPUESTA FINAL
        # =================================================

        return {

            # =================================================
            # USUARIOS
            # =================================================

            "users": {

                "total":
                    users_total,

                "today":
                    users_today,

                "this_week":
                    users_this_week,

                "this_month":
                    users_this_month,

                "unique_customers":
                    unique_customers,

                "returning_customers":
                    returning_customers,

                "returning_customer_rate":
                    returning_customer_rate

            },


            # =================================================
            # BARBERÍAS
            # =================================================

            "barbershops": {

                "total":
                    barbershops_total,

                "active":
                    barbershops_active,

                "inactive":
                    barbershops_inactive,

                "new_this_month":
                    barbershops_new_this_month

            },


            # =================================================
            # RESERVAS
            # =================================================

            "bookings": {

                "total":
                    bookings_total,

                "today":
                    bookings_today,

                "this_week":
                    bookings_this_week,

                "this_month":
                    bookings_this_month,

                "pending":
                    pending,

                "confirmed":
                    confirmed,

                "in_progress":
                    in_progress,

                "completed":
                    completed,

                "cancelled":
                    cancelled,

                "cancelled_by_customer":
                    cancelled_by_customer,

                "cancelled_by_barber":
                    cancelled_by_barber,

                "cancelled_by_admin":
                    cancelled_by_admin,

                "no_show":
                    no_show,

                "rejected":
                    rejected,

                "cancellation_rate":
                    cancellation_rate,

                "no_show_rate":
                    no_show_rate

            },


            # =================================================
            # INFORMACIÓN ECONÓMICA DERIVADA DE RESERVAS
            # =================================================

            "financial": {

                "reserved_value":
                    reserved_value,

                "reserved_value_today":
                    reserved_value_today,

                "reserved_value_this_month":
                    reserved_value_this_month,

                "completed_value_this_month":
                    completed_value_this_month,

                "average_ticket":
                    average_ticket

            },


            # =================================================
            # SIMULACIÓN ECONÓMICA
            # =================================================

            "financial_simulation": {

                "is_simulation":
                    True,

                "currency":
                    "COP",

                "commission_rate":
                    commission_rate,

                "commission_percentage":
                    commission_percentage,


                # ---------------------------------------------
                # GMV SIMULADO
                # ---------------------------------------------

                "gross_booking_value":
                    gross_booking_value,

                "completed_value":
                    completed_value,


                # ---------------------------------------------
                # INGRESOS PROYECTADOS BARBERGO
                # ---------------------------------------------

                "projected_platform_revenue":
                    round(
                        projected_platform_revenue,
                        2
                    ),

                "completed_platform_revenue":
                    round(
                        completed_platform_revenue,
                        2
                    ),


                # ---------------------------------------------
                # LIQUIDACIÓN A BARBERÍAS
                # ---------------------------------------------

                "projected_barbershop_payout":
                    round(
                        projected_barbershop_payout,
                        2
                    ),

                "completed_barbershop_payout":
                    round(
                        completed_barbershop_payout,
                        2
                    ),


                # ---------------------------------------------
                # MES ACTUAL
                # ---------------------------------------------

                "projected_platform_revenue_this_month":
                    round(
                        projected_platform_revenue_this_month,
                        2
                    ),

                "projected_barbershop_payout_this_month":
                    round(
                        projected_barbershop_payout_this_month,
                        2
                    ),

                "completed_platform_revenue_this_month":
                    round(
                        completed_platform_revenue_this_month,
                        2
                    ),

                "completed_barbershop_payout_this_month":
                    round(
                        completed_barbershop_payout_this_month,
                        2
                    ),


                # ---------------------------------------------
                # VALORES NO CONVERTIDOS
                # ---------------------------------------------

                "cancelled_value":
                    cancelled_value,

                "no_show_value":
                    no_show_value,

                "rejected_value":
                    rejected_value,

                "lost_value":
                    lost_value,

                "lost_platform_revenue":
                    round(
                        lost_platform_revenue,
                        2
                    )

            },


            # =================================================
            # GRÁFICAS
            # =================================================

            "growth": {

                "users":
                    users_growth,

                "bookings":
                    bookings_growth

            },


            # =================================================
            # RANKINGS
            # =================================================

            "rankings": {

                "top_barbershops":
                    top_barbershops,

                "top_services":
                    top_services,

                "top_barbers":
                    top_barbers

            }

        }


    # =====================================================
    # LISTADO DE BARBERÍAS
    # =====================================================

    @staticmethod
    def get_barbershops(
        db: Session,
        search: str | None = None,
        status_filter: str = "all",
        limit: int = 50,
        offset: int = 0
    ) -> dict:

        allowed_statuses = {
            "all",
            "active",
            "inactive"
        }


        if (
            status_filter
            not in
            allowed_statuses
        ):

            status_filter = "all"


        limit = max(
            1,
            min(
                limit,
                100
            )
        )


        offset = max(
            offset,
            0
        )


        return (
            AdminRepository
            .list_barbershops_admin(
                db=db,
                search=search,
                status_filter=status_filter,
                limit=limit,
                offset=offset
            )
        )


    # =====================================================
    # DETALLE ADMINISTRATIVO DE BARBERÍA
    # =====================================================

    @staticmethod
    def get_barbershop_detail(
        db: Session,
        barbershop_id: int
    ) -> dict | None:

        if (
            barbershop_id <= 0
        ):

            raise HTTPException(
                status_code=422,
                detail=(
                    "La barbería seleccionada "
                    "no es válida."
                )
            )


        return (
            AdminRepository
            .get_barbershop_detail_admin(
                db=db,
                barbershop_id=
                    barbershop_id
            )
        )

    # =====================================================
    # ACTIVAR / DESACTIVAR BARBERÍA
    # =====================================================

    @staticmethod
    def update_barbershop_status(
        db: Session,
        barbershop_id: int,
        is_active: bool
    ) -> dict | None:

        return (
            AdminRepository
            .update_barbershop_status(
                db=db,
                barbershop_id=
                    barbershop_id,
                is_active=
                    is_active
            )
        )


    # =====================================================
    # ADMIN - USUARIOS
    # =====================================================

    @staticmethod
    def get_users(
        db: Session,
        search: str | None = None,
        role_filter: str = "all",
        status_filter: str = "all",
        limit: int = 100,
        offset: int = 0
    ) -> dict:

        allowed_roles = {
            "all",
            "CLIENT",
            "BARBER",
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        }


        if role_filter == "all":

            normalized_role = "all"

        else:

            normalized_role = (
                role_filter
                .strip()
                .upper()
            )


        if (
            normalized_role
            not in allowed_roles
        ):

            normalized_role = "all"


        allowed_statuses = {
            "all",
            "active",
            "inactive"
        }


        normalized_status = (
            status_filter
            .strip()
            .lower()
        )


        if (
            normalized_status
            not in allowed_statuses
        ):

            normalized_status = "all"


        limit = max(
            1,
            min(
                limit,
                100
            )
        )


        offset = max(
            offset,
            0
        )


        return (
            AdminRepository
            .list_users_admin(
                db=db,
                search=search,
                role_filter=
                    normalized_role,
                status_filter=
                    normalized_status,
                limit=limit,
                offset=offset
            )
        )


    # =====================================================
    # ACTIVAR / INHABILITAR USUARIO
    # =====================================================

    @staticmethod
    def update_user_status(
        db: Session,
        user_id: int,
        is_active: bool,
        current_admin_id: int
    ) -> dict:

        # -------------------------------------------------
        # NO PERMITIR AUTO-INHABILITACIÓN
        # -------------------------------------------------

        if (
            user_id == current_admin_id
            and
            is_active is False
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "No puedes inhabilitar "
                    "tu propia cuenta administrativa."
                )
            )


        # -------------------------------------------------
        # ACTUALIZAR USUARIO
        # -------------------------------------------------

        user = (
            AdminRepository
            .update_user_status(
                db=db,
                user_id=user_id,
                is_active=is_active
            )
        )


        # -------------------------------------------------
        # USUARIO NO EXISTE
        # -------------------------------------------------

        if user is None:

            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado."
            )


        # -------------------------------------------------
        # RESPUESTA
        # -------------------------------------------------

        return {

            "id":
                user.id,

            "is_active":
                bool(
                    user.is_active
                ),

            "message": (
                "Usuario reactivado correctamente."
                if user.is_active
                else
                "Usuario inhabilitado correctamente."
            )

        }


    # =====================================================
    # ADMIN - RESERVAS
    # =====================================================

        # =====================================================
    # ADMIN - RESERVAS
    # =====================================================

    @staticmethod
    def get_bookings(
        db: Session,
        search: str | None = None,
        status_filter: str = "all",
        barbershop_id: int | None = None,
        barber_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int = 20,
        offset: int = 0
    ) -> dict:

        # =================================================
        # ESTADOS PERMITIDOS
        # =================================================

        allowed_statuses = {
            "all",
            "PENDING",
            "CONFIRMED",
            "IN_PROGRESS",
            "COMPLETED",
            "CANCELLED_BY_CUSTOMER",
            "CANCELLED_BY_BARBER",
            "CANCELLED_BY_ADMIN",
            "REJECTED",
            "NO_SHOW"
        }


        # =================================================
        # NORMALIZAR ESTADO
        # =================================================

        if (
            status_filter
            and
            status_filter.lower()
            != "all"
        ):

            normalized_status = (
                status_filter
                .strip()
                .upper()
            )

        else:

            normalized_status = "all"


        if (
            normalized_status
            not in
            allowed_statuses
        ):

            normalized_status = "all"


        # =================================================
        # VALIDAR BARBERÍA
        # =================================================

        if (
            barbershop_id
            is not None
            and
            barbershop_id <= 0
        ):

            raise HTTPException(
                status_code=422,
                detail=(
                    "La barbería seleccionada "
                    "no es válida."
                )
            )


        # =================================================
        # VALIDAR BARBERO
        # =================================================

        if (
            barber_id
            is not None
            and
            barber_id <= 0
        ):

            raise HTTPException(
                status_code=422,
                detail=(
                    "El barbero seleccionado "
                    "no es válido."
                )
            )


        # =================================================
        # VALIDAR FECHA INICIAL
        # =================================================

        if date_from:

            try:

                date.fromisoformat(
                    date_from
                )

            except ValueError:

                raise HTTPException(
                    status_code=422,
                    detail=(
                        "La fecha inicial "
                        "no tiene un formato válido."
                    )
                )


        # =================================================
        # VALIDAR FECHA FINAL
        # =================================================

        if date_to:

            try:

                date.fromisoformat(
                    date_to
                )

            except ValueError:

                raise HTTPException(
                    status_code=422,
                    detail=(
                        "La fecha final "
                        "no tiene un formato válido."
                    )
                )


        # =================================================
        # VALIDAR RANGO DE FECHAS
        # =================================================

        if (
            date_from
            and
            date_to
            and
            date_from > date_to
        ):

            raise HTTPException(
                status_code=422,
                detail=(
                    "La fecha inicial no puede "
                    "ser posterior a la fecha final."
                )
            )


        # =================================================
        # VALIDAR LÍMITE
        # =================================================

        limit = max(
            1,
            min(
                limit,
                100
            )
        )


        # =================================================
        # VALIDAR OFFSET
        # =================================================

        offset = max(
            offset,
            0
        )


        # =================================================
        # CONSULTAR REPOSITORIO
        # =================================================

        return (
            AdminRepository
            .list_bookings_admin(
                db=db,

                search=
                    search,

                status_filter=
                    normalized_status,

                barbershop_id=
                    barbershop_id,

                barber_id=
                    barber_id,

                date_from=
                    date_from,

                date_to=
                    date_to,

                limit=
                    limit,

                offset=
                    offset
            )
        )


    # =====================================================
    # ADMIN - CANCELAR RESERVA
    # =====================================================

    @staticmethod
    def cancel_booking(
        db: Session,
        booking_id: int
    ) -> dict:

        result = (
            AdminRepository
            .cancel_booking_admin(
                db=db,
                booking_id=booking_id
            )
        )


        # -------------------------------------------------
        # RESERVA NO ENCONTRADA
        # -------------------------------------------------

        if result is None:

            raise HTTPException(
                status_code=404,
                detail="Reserva no encontrada."
            )


        # -------------------------------------------------
        # CANCELACIÓN NO REALIZADA
        # -------------------------------------------------

        if (
            result.get(
                "cancelled"
            )
            is False
        ):

            reason = (
                result.get(
                    "reason"
                )
            )


            if (
                reason ==
                "INVALID_STATUS"
            ):

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "La reserva no puede ser cancelada "
                        "desde su estado actual."
                    )
                )


            if (
                reason ==
                "ADMIN_STATUS_NOT_CONFIGURED"
            ):

                raise HTTPException(
                    status_code=500,
                    detail=(
                        "El estado "
                        "CANCELLED_BY_ADMIN "
                        "no está configurado."
                    )
                )


            raise HTTPException(
                status_code=409,
                detail=(
                    "No fue posible cancelar "
                    "la reserva."
                )
            )


        # -------------------------------------------------
        # RESPUESTA
        # -------------------------------------------------

        return {

            **result,

            "message":
                "Reserva cancelada correctamente por el administrador."

        }
        
    # =====================================================
    # ADMIN - CONFIRMAR RESERVA
    # =====================================================

    @staticmethod
    def confirm_booking(
        db: Session,
        booking_id: int
    ) -> dict:

        # -------------------------------------------------
        # VALIDAR ID
        # -------------------------------------------------

        if (
            booking_id <= 0
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "La reserva indicada "
                    "no es válida."
                )
            )


        # -------------------------------------------------
        # CONFIRMAR EN REPOSITORIO
        # -------------------------------------------------

        result = (
            AdminRepository
            .confirm_booking_admin(
                db=db,
                booking_id=booking_id
            )
        )


        # -------------------------------------------------
        # RESERVA NO ENCONTRADA
        # -------------------------------------------------

        if (
            result is None
        ):

            raise HTTPException(
                status_code=404,
                detail=(
                    "Reserva no encontrada."
                )
            )


        # -------------------------------------------------
        # CONFIRMACIÓN NO REALIZADA
        # -------------------------------------------------

        if (
            result.get(
                "confirmed"
            )
            is False
        ):

            reason = (
                result.get(
                    "reason"
                )
            )


            # ---------------------------------------------
            # ESTADO NO PERMITE CONFIRMACIÓN
            # ---------------------------------------------

            if (
                reason ==
                "INVALID_STATUS"
            ):

                current_status = (
                    result.get(
                        "status_name"
                    )
                    or
                    result.get(
                        "status_code"
                    )
                    or
                    "desconocido"
                )


                raise HTTPException(
                    status_code=409,
                    detail=(
                        "La reserva no puede "
                        "ser confirmada desde "
                        "su estado actual: "
                        f"{current_status}."
                    )
                )


            # ---------------------------------------------
            # ESTADO CONFIRMED NO CONFIGURADO
            # ---------------------------------------------

            if (
                reason ==
                "CONFIRMED_STATUS_NOT_CONFIGURED"
            ):

                raise HTTPException(
                    status_code=500,
                    detail=(
                        "El estado CONFIRMED "
                        "no está configurado "
                        "en la base de datos."
                    )
                )


            # ---------------------------------------------
            # ERROR GENERAL
            # ---------------------------------------------

            raise HTTPException(
                status_code=400,
                detail=(
                    "No fue posible confirmar "
                    "la reserva."
                )
            )


        # -------------------------------------------------
        # RESPUESTA
        # -------------------------------------------------

        return {

            "id":
                result[
                    "id"
                ],

            "confirmed":
                True,

            "status_id":
                result[
                    "status_id"
                ],

            "status_code":
                result[
                    "status_code"
                ],

            "status_name":
                result[
                    "status_name"
                ],

            "message":
                (
                    "Reserva confirmada "
                    "correctamente."
                )

        }

    # =====================================================
    # ADMIN - COMPLETAR RESERVA
    # =====================================================

    @staticmethod
    def complete_booking(
        db: Session,
        booking_id: int
    ) -> dict:

        # -------------------------------------------------
        # VALIDAR ID
        # -------------------------------------------------

        if (
            booking_id <= 0
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "La reserva indicada "
                    "no es válida."
                )
            )


        # -------------------------------------------------
        # COMPLETAR EN REPOSITORIO
        # -------------------------------------------------

        result = (
            AdminRepository
            .complete_booking_admin(
                db=db,
                booking_id=booking_id
            )
        )


        # -------------------------------------------------
        # RESERVA NO ENCONTRADA
        # -------------------------------------------------

        if (
            result is None
        ):

            raise HTTPException(
                status_code=404,
                detail=(
                    "Reserva no encontrada."
                )
            )


        # -------------------------------------------------
        # COMPLETADO NO REALIZADO
        # -------------------------------------------------

        if (
            result.get(
                "completed"
            )
            is False
        ):

            reason = (
                result.get(
                    "reason"
                )
            )


            # ---------------------------------------------
            # ESTADO NO PERMITE COMPLETAR
            # ---------------------------------------------

            if (
                reason ==
                "INVALID_STATUS"
            ):

                current_status = (
                    result.get(
                        "status_name"
                    )
                    or
                    result.get(
                        "status_code"
                    )
                    or
                    "desconocido"
                )


                raise HTTPException(
                    status_code=409,
                    detail=(
                        "La reserva no puede "
                        "marcarse como completada "
                        "desde su estado actual: "
                        f"{current_status}."
                    )
                )


            # ---------------------------------------------
            # COMPLETED NO CONFIGURADO
            # ---------------------------------------------

            if (
                reason ==
                "COMPLETED_STATUS_NOT_CONFIGURED"
            ):

                raise HTTPException(
                    status_code=500,
                    detail=(
                        "El estado COMPLETED "
                        "no está configurado "
                        "en la base de datos."
                    )
                )


            # ---------------------------------------------
            # ERROR GENERAL
            # ---------------------------------------------

            raise HTTPException(
                status_code=400,
                detail=(
                    "No fue posible completar "
                    "la reserva."
                )
            )


        # -------------------------------------------------
        # RESPUESTA
        # -------------------------------------------------

        return {

            "id":
                result[
                    "id"
                ],

            "completed":
                True,

            "status_id":
                result[
                    "status_id"
                ],

            "status_code":
                result[
                    "status_code"
                ],

            "status_name":
                result[
                    "status_name"
                ],

            "message":
                (
                    "Servicio marcado como "
                    "completado correctamente."
                )

        }