from sqlalchemy.orm import Session

from app.services.admin_service import (
    AdminService
)


class AdminController:


    # =====================================================
    # DASHBOARD
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ) -> dict:

        return (
            AdminService
            .get_dashboard(
                db
            )
        )


    # =====================================================
    # BARBERÍAS
    # =====================================================

    @staticmethod
    def barbershops(
        db: Session,
        search: str | None = None,
        status_filter: str = "all",
        limit: int = 50,
        offset: int = 0
    ) -> dict:

        return (
            AdminService
            .get_barbershops(
                db=db,
                search=search,
                status_filter=
                    status_filter,
                limit=limit,
                offset=offset
            )
        )

    # =====================================================
    # DETALLE ADMINISTRATIVO DE BARBERÍA
    # =====================================================

    @staticmethod
    def barbershop_detail(
        db: Session,
        barbershop_id: int
    ) -> dict | None:

        return (
            AdminService
            .get_barbershop_detail(
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
            AdminService
            .update_barbershop_status(
                db=db,
                barbershop_id=
                    barbershop_id,
                is_active=
                    is_active
            )
        )


    # =====================================================
    # USUARIOS
    # =====================================================

    @staticmethod
    def users(
        db: Session,
        search: str | None = None,
        role_filter: str = "all",
        status_filter: str = "all",
        limit: int = 100,
        offset: int = 0
    ) -> dict:

        return (
            AdminService
            .get_users(
                db=db,
                search=search,
                role_filter=
                    role_filter,
                status_filter=
                    status_filter,
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

        return (
            AdminService
            .update_user_status(
                db=db,
                user_id=
                    user_id,
                is_active=
                    is_active,
                current_admin_id=
                    current_admin_id
            )
        )


    # =====================================================
    # RESERVAS
    # =====================================================

    @staticmethod
    def bookings(
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

        return (
            AdminService
            .get_bookings(
                db=db,

                search=
                    search,

                status_filter=
                    status_filter,

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
    # CANCELAR RESERVA
    # =====================================================

    @staticmethod
    def cancel_booking(
        db: Session,
        booking_id: int
    ) -> dict:

        return (
            AdminService
            .cancel_booking(
                db=db,
                booking_id=
                    booking_id
            )
        )


    # =====================================================
    # CONFIRMAR RESERVA
    # =====================================================

    @staticmethod
    def confirm_booking(
        db: Session,
        booking_id: int
    ) -> dict:

        return (
            AdminService
            .confirm_booking(
                db=db,
                booking_id=
                    booking_id
            )
        )


    # =====================================================
    # COMPLETAR RESERVA
    # =====================================================

    @staticmethod
    def complete_booking(
        db: Session,
        booking_id: int
    ) -> dict:

        return (
            AdminService
            .complete_booking(
                db=db,
                booking_id=
                    booking_id
            )
        )