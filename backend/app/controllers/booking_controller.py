from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BarberNotFoundError,
    BarbershopForbiddenError,
    BarbershopInactiveError,
    BarbershopNotFoundError,
    BookingConflictError,
    BookingStatusNotFoundError,
    InvalidBookingTimeError,
    PastBookingTimeError,
    ServiceNotAvailableForBarberError,
    BookingNotFoundError,
    InvalidBookingStatusTransitionError,
    BarbershopForbiddenError,
    BookingCancellationWindowError,
    BookingForbiddenError
)

from app.models.user_model import (
    User
)

from app.schemas.booking_schema import (
    BookingCreate
)

from app.services.booking_service import (
    BookingService
)


class BookingController:

    # =====================================================
    # CREAR
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        data: BookingCreate,
        current_user: User
    ):

        try:

            return BookingService.create(
                db,
                data,
                current_user
            )


        except BarberNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Barbero no encontrado."
            )


        except BarbershopNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Barbería no encontrada."
            )


        except BarbershopInactiveError:

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,

                detail=(
                    "La barbería no se encuentra "
                    "disponible actualmente."
                )
            )


        except ServiceNotAvailableForBarberError:

            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,

                detail=(
                    "El barbero no ofrece "
                    "el servicio solicitado."
                )
            )


        except PastBookingTimeError:

            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,

                detail=(
                    "No se puede crear una reserva "
                    "en una fecha u hora pasada."
                )
            )


        except InvalidBookingTimeError as error:

            raise HTTPException(
                status_code=
                    status.HTTP_400_BAD_REQUEST,

                detail=str(error)
            )


        except BookingConflictError as error:

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,

                detail=str(error)
            )


        except BookingStatusNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=(
                    "No se encuentra configurado "
                    "el estado inicial de la reserva."
                )
            )


        except SQLAlchemyError as error:

            print(
                "ERROR SQL BOOKING:",
                repr(error)
            )

            raise HTTPException(
                status_code=
                    status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=(
                    "No fue posible crear "
                    "la reserva."
                )
            )


    # =====================================================
    # MIS RESERVAS
    # =====================================================

    @staticmethod
    def list_my_bookings(
        db: Session,
        current_user: User
    ):

        return (
            BookingService
            .list_my_bookings(
                db,
                current_user
            )
        )
        
        
        # =====================================================
    # RESERVAS DE UN BARBERO
    # =====================================================

    @staticmethod
    def list_barber_bookings(
        db: Session,
        barber_id: int,
        current_user: User,
        requested_date=None,
        status_code: str | None = None
    ):

        try:

            return (
                BookingService
                .list_barber_bookings(
                    db,
                    barber_id,
                    current_user,
                    requested_date,
                    status_code
                )
            )


        except BarberNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Barbero no encontrado."
            )


        except BarbershopForbiddenError:

            raise HTTPException(
                status_code=
                    status.HTTP_403_FORBIDDEN,

                detail=(
                    "No tienes permisos para "
                    "consultar las reservas "
                    "de este barbero."
                )
            )
            
                # =====================================================
    # CONFIRMAR RESERVA
    # =====================================================

    @staticmethod
    def confirm_booking(
        db: Session,
        booking_id: int,
        current_user: User
    ):

        try:

            return (
                BookingService.confirm_booking(
                    db,
                    booking_id,
                    current_user
                )
            )


        except BookingNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Reserva no encontrada."
            )


        except BarberNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Barbero no encontrado."
            )


        except BarbershopForbiddenError:

            raise HTTPException(
                status_code=
                    status.HTTP_403_FORBIDDEN,

                detail=(
                    "No tienes permisos para "
                    "gestionar esta reserva."
                )
            )


        except InvalidBookingStatusTransitionError as error:

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,

                detail=str(error)
            )


        except BookingStatusNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=(
                    "No se encuentra configurado "
                    "el estado CONFIRMED."
                )
            )


    # =====================================================
    # RECHAZAR RESERVA
    # =====================================================

    @staticmethod
    def reject_booking(
        db: Session,
        booking_id: int,
        current_user: User
    ):

        try:

            return (
                BookingService.reject_booking(
                    db,
                    booking_id,
                    current_user
                )
            )


        except BookingNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Reserva no encontrada."
            )


        except BarberNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Barbero no encontrado."
            )


        except BarbershopForbiddenError:

            raise HTTPException(
                status_code=
                    status.HTTP_403_FORBIDDEN,

                detail=(
                    "No tienes permisos para "
                    "gestionar esta reserva."
                )
            )


        except InvalidBookingStatusTransitionError as error:

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,

                detail=str(error)
            )


        except BookingStatusNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=(
                    "No se encuentra configurado "
                    "el estado REJECTED."
                )
            )
            
                # =====================================================
    # CANCELAR RESERVA POR EL CLIENTE
    # =====================================================

    @staticmethod
    def cancel_by_customer(
        db: Session,
        booking_id: int,
        current_user: User
    ):

        try:

            return (
                BookingService
                .cancel_by_customer(
                    db,
                    booking_id,
                    current_user
                )
            )


        except BookingNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Reserva no encontrada."
            )


        except BookingForbiddenError:

            raise HTTPException(
                status_code=
                    status.HTTP_403_FORBIDDEN,

                detail=(
                    "No tienes permisos para "
                    "cancelar esta reserva."
                )
            )


        except BarbershopNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Barbería no encontrada."
            )


        except InvalidBookingStatusTransitionError as error:

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,

                detail=str(error)
            )


        except BookingCancellationWindowError as error:

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,

                detail=str(error)
            )


        except BookingStatusNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=(
                    "No se encuentra configurado "
                    "el estado de cancelación."
                )
            )
            
                # =====================================================
    # INICIAR SERVICIO
    # =====================================================

    @staticmethod
    def start_booking(
        db: Session,
        booking_id: int,
        current_user: User
    ):

        try:

            return (
                BookingService.start_booking(
                    db,
                    booking_id,
                    current_user
                )
            )


        except BookingNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Reserva no encontrada."
            )


        except BarberNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Barbero no encontrado."
            )


        except BarbershopForbiddenError:

            raise HTTPException(
                status_code=
                    status.HTTP_403_FORBIDDEN,

                detail=(
                    "No tienes permisos para "
                    "iniciar esta reserva."
                )
            )


        except InvalidBookingStatusTransitionError as error:

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,

                detail=str(error)
            )


        except InvalidBookingTimeError as error:

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,

                detail=str(error)
            )


        except BookingStatusNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=(
                    "No se encuentra configurado "
                    "el estado IN_PROGRESS."
                )
            )


    # =====================================================
    # COMPLETAR SERVICIO
    # =====================================================

    @staticmethod
    def complete_booking(
        db: Session,
        booking_id: int,
        current_user: User
    ):

        try:

            return (
                BookingService.complete_booking(
                    db,
                    booking_id,
                    current_user
                )
            )


        except BookingNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Reserva no encontrada."
            )


        except BarberNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Barbero no encontrado."
            )


        except BarbershopForbiddenError:

            raise HTTPException(
                status_code=
                    status.HTTP_403_FORBIDDEN,

                detail=(
                    "No tienes permisos para "
                    "completar esta reserva."
                )
            )


        except InvalidBookingStatusTransitionError as error:

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,

                detail=str(error)
            )


        except BookingStatusNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=(
                    "No se encuentra configurado "
                    "el estado COMPLETED."
                )
            )
            
            
                # =====================================================
    # MARCAR NO SHOW
    # =====================================================

    @staticmethod
    def mark_no_show(
        db: Session,
        booking_id: int,
        current_user: User
    ):

        try:

            return (
                BookingService.mark_no_show(
                    db,
                    booking_id,
                    current_user
                )
            )


        except BookingNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Reserva no encontrada."
            )


        except BarbershopNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Barbería no encontrada."
            )


        except BarberNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_404_NOT_FOUND,

                detail=
                    "Barbero no encontrado."
            )


        except BarbershopForbiddenError:

            raise HTTPException(
                status_code=
                    status.HTTP_403_FORBIDDEN,

                detail=(
                    "No tienes permisos para "
                    "marcar esta reserva como NO_SHOW."
                )
            )


        except InvalidBookingStatusTransitionError as error:

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,

                detail=str(error)
            )


        except InvalidBookingTimeError as error:

            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,

                detail=str(error)
            )


        except BookingStatusNotFoundError:

            raise HTTPException(
                status_code=
                    status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=(
                    "No se encuentra configurado "
                    "el estado NO_SHOW."
                )
            )