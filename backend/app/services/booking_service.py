from datetime import (
    datetime,
    timedelta
)

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BarberNotFoundError,
    BarbershopForbiddenError,
    BarbershopInactiveError,
    BarbershopNotFoundError,
    BookingConflictError,
    BookingNotFoundError,
    BookingStatusNotFoundError,
    InvalidBookingStatusTransitionError,
    InvalidBookingTimeError,
    PastBookingTimeError,
    ServiceNotAvailableForBarberError,
    BookingForbiddenError,
    BookingCancellationWindowError,
        HomeServiceError,
    PaymentMethodError,
)

from app.models.booking_model import (
    Booking
)

from app.models.user_model import (
    User
)

from app.repositories.availability_repository import (
    AvailabilityRepository
)

from app.repositories.barbershop_repository import (
    BarbershopRepository
)

from app.repositories.booking_repository import (
    BookingRepository
)

from app.core.geo import haversine_km
from sqlalchemy import text as sql_text
from app.schemas.booking_schema import (
    BookingCreate
)

from app.repositories.barber_repository import (
    BarberRepository
)

from app.repositories.barbershop_repository import (
    BarbershopRepository
)

class BookingService:

    SLOT_INTERVAL_MINUTES = 15


    # =====================================================
    # CONVERTIR RESERVA A RESPUESTA
    # =====================================================

    @staticmethod
    def _to_response(
        db: Session,
        booking: Booking
    ) -> dict:

        status = (
            BookingRepository
            .get_status_by_id(
                db,
                booking.status_id
            )
        )

        return {
            "id":
                booking.id,

            "client_user_id":
                booking.client_user_id,

            "barbershop_id":
                booking.barbershop_id,

            "barber_id":
                booking.barber_id,

            "service_id":
                booking.service_id,

            "status_id":
                booking.status_id,

            "status_code":
                status.code
                if status
                else "UNKNOWN",

            "start_at":
                booking.start_at,

            "end_at":
                booking.end_at,

            "service_price":
                booking.service_price,

            "customer_notes":
                booking.customer_notes,

            "barber_notes":
                booking.barber_notes,

            "created_at":
                booking.created_at,

            "updated_at": booking.updated_at,
            "guest_name": booking.guest_name,
            "guest_email": booking.guest_email,
            "booking_type": booking.booking_type or "IN_SHOP",
            "home_address": booking.home_address,
            "home_latitude": booking.home_latitude,
            "home_longitude": booking.home_longitude,
            "home_access_notes": booking.home_access_notes,
            "home_fee": booking.home_fee or 0,
            "payment_method": booking.payment_method,
            "payment_status": booking.payment_status or "PENDING",
            "payment_reference": booking.payment_reference
        }


        # =====================================================
    # VALIDAR SERVICIO A DOMICILIO
    # Devuelve el recargo de desplazamiento.
    # =====================================================
    @staticmethod
    def _validate_home_service(
        barbershop,
        barber,
        service,
        data: BookingCreate
    ):
        if (
            barbershop.home_service_status != "APPROVED"
            or not barbershop.offers_home_service
        ):
            raise HomeServiceError(
                "Esta barbería no ofrece "
                "servicio a domicilio."
            )

        if not barber.accepts_home_service:
            raise HomeServiceError(
                "Este barbero no atiende "
                "a domicilio."
            )

        if not service.home_service_allowed:
            raise HomeServiceError(
                "Este servicio no está disponible "
                "a domicilio."
            )

        if data.home is None:
            raise HomeServiceError(
                "Indica la dirección donde "
                "quieres recibir el servicio."
            )

        min_hours = (
            barbershop.home_service_min_notice_hours
            or 0
        )

        if (
            data.start_at
            < datetime.now()
            + timedelta(hours=min_hours)
        ):
            raise HomeServiceError(
                "Para domicilio debes reservar con al "
                f"menos {min_hours} hora(s) de anticipación."
            )

        if (
            barbershop.latitude is not None
            and barbershop.longitude is not None
            and barbershop.home_service_radius_km
        ):
            distance = haversine_km(
                barbershop.latitude,
                barbershop.longitude,
                data.home.latitude,
                data.home.longitude
            )

            if distance > float(
                barbershop.home_service_radius_km
            ):
                raise HomeServiceError(
                    "Tu dirección está fuera de la zona "
                    "de cobertura "
                    f"({barbershop.home_service_radius_km} km "
                    f"a la redonda, estás a {distance:.1f} km)."
                )

        return barbershop.home_service_fee or 0

    # =====================================================
    # VALIDAR MÉTODO DE PAGO
    #
    # Si la barbería configuró métodos de pago, el cliente
    # debe elegir uno de ellos.
    # =====================================================
    @staticmethod
    def _validate_payment_method(
        db: Session,
        barbershop_id: int,
        method: str | None
    ):
        enabled = list(
            db.execute(
                sql_text(
                    "SELECT method FROM barbershop_payment_methods "
                    "WHERE barbershop_id = :i AND is_active = TRUE"
                ),
                {"i": barbershop_id}
            ).scalars()
        )

        if not enabled:
            return

        if not method:
            raise PaymentMethodError(
                "Elige cómo vas a pagar tu cita."
            )

        if method not in enabled:
            raise PaymentMethodError(
                "La barbería no acepta ese método de pago."
            )

    # =====================================================
    # CREAR RESERVA
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        data: BookingCreate,
        current_user: User | None = None,
        guest: dict | None = None
    ):
        """
        Crea una reserva.

        * current_user -> cliente con cuenta
        * guest        -> cliente sin cuenta:
                          {name, email, phone, manage_token, verified_at}
        """
        try:
            if current_user is None and not guest:
                raise BookingForbiddenError()


            # =================================================
            # 1. NO PERMITIR FECHA/HORA PASADA
            # =================================================

            if data.start_at <= datetime.now():

                raise PastBookingTimeError()


            # =================================================
            # 2. BLOQUEAR BARBERO
            #
            # Mientras esta transacción se ejecuta,
            # otra reserva para el mismo barbero tendrá
            # que esperar.
            # =================================================

            barber = (
                BookingRepository.lock_barber(
                    db,
                    data.barber_id
                )
            )

            if not barber:

                raise BarberNotFoundError()


            # =================================================
            # 3. BARBERÍA
            # =================================================

            barbershop = (
                BarbershopRepository.get_by_id(
                    db,
                    barber.barbershop_id
                )
            )

            if not barbershop:

                raise BarbershopNotFoundError()


            if not barbershop.is_active:

                raise BarbershopInactiveError()


            # =================================================
            # 4. SERVICIO
            #
            # Además verifica que esté asignado al barbero.
            # =================================================

            service = (
                AvailabilityRepository
                .get_service_for_barber(
                    db,
                    barber.id,
                    data.service_id
                )
            )

            if not service:

                raise ServiceNotAvailableForBarberError()


            # =================================================
            # 5. CALCULAR FIN DE LA CITA
            # =================================================

            duration = timedelta(
                minutes=
                    service.duration_minutes
            )

            end_at = (
                data.start_at
                + duration
            )


            # =================================================
            # 6. DÍA DE LA SEMANA
            # =================================================

            day_of_week = (
                data.start_at
                .date()
                .weekday()
                + 1
            )


            # =================================================
            # 7. HORARIO DE LA BARBERÍA
            # =================================================

            shop_schedule = (
                AvailabilityRepository
                .get_barbershop_schedule(
                    db,
                    barber.barbershop_id,
                    day_of_week
                )
            )

            if not shop_schedule:

                raise InvalidBookingTimeError(
                    "La barbería está cerrada "
                    "ese día."
                )


            # =================================================
            # 8. HORARIO DEL BARBERO
            # =================================================

            barber_schedule = (
                AvailabilityRepository
                .get_barber_schedule(
                    db,
                    barber.id,
                    day_of_week
                )
            )

            if not barber_schedule:

                raise InvalidBookingTimeError(
                    "El barbero no trabaja "
                    "ese día."
                )


            # =================================================
            # 9. CONSTRUIR HORARIOS DEL DÍA
            # =================================================

            shop_start = datetime.combine(
                data.start_at.date(),
                shop_schedule.open_time
            )

            shop_end = datetime.combine(
                data.start_at.date(),
                shop_schedule.close_time
            )


            barber_start = datetime.combine(
                data.start_at.date(),
                barber_schedule.start_time
            )

            barber_end = datetime.combine(
                data.start_at.date(),
                barber_schedule.end_time
            )


            # =================================================
            # 10. JORNADA EFECTIVA
            #
            # Debe cumplir simultáneamente:
            #
            # horario barbería
            # +
            # horario barbero
            # =================================================

            work_start = max(
                shop_start,
                barber_start
            )

            work_end = min(
                shop_end,
                barber_end
            )


            # =================================================
            # 11. COMPROBAR QUE LA CITA COMPLETA QUEPA
            #
            # Ejemplo:
            #
            # cierre 18:00
            # servicio 50 min
            #
            # 17:00 -> 17:50 ✓
            # 17:15 -> 18:05 ✗
            # =================================================

            if (
                data.start_at < work_start
                or end_at > work_end
            ):

                raise InvalidBookingTimeError(
                    "El servicio no cabe completamente "
                    "dentro del horario disponible."
                )


            # =================================================
            # 12. VALIDAR SLOT DE 15 MINUTOS
            # =================================================

            seconds_from_start = int(
                (
                    data.start_at
                    - work_start
                ).total_seconds()
            )

            slot_seconds = (
                BookingService
                .SLOT_INTERVAL_MINUTES
                * 60
            )


            if (
                seconds_from_start
                % slot_seconds
                != 0
            ):

                raise InvalidBookingTimeError(
                    "La hora seleccionada no "
                    "corresponde a un horario válido."
                )


            if (
                data.start_at.second != 0
                or
                data.start_at.microsecond != 0
            ):

                raise InvalidBookingTimeError(
                    "La hora seleccionada no "
                    "corresponde a un horario válido."
                )


            # =================================================
            # 13. ALMUERZO / DESCANSOS DE BARBERÍA
            # =================================================

            break_conflict = (
                BookingRepository
                .has_barbershop_break_conflict(
                    db,
                    barber.barbershop_id,
                    day_of_week,
                    data.start_at.date(),
                    data.start_at,
                    end_at
                )
            )

            if break_conflict:

                raise BookingConflictError(
                    "El horario seleccionado cruza "
                    "un descanso de la barbería."
                )


            # =================================================
            # 14. BLOQUEOS PARTICULARES DEL BARBERO
            # =================================================

            block_conflict = (
                BookingRepository
                .has_barber_block_conflict(
                    db,
                    barber.id,
                    data.start_at,
                    end_at
                )
            )

            if block_conflict:

                raise BookingConflictError(
                    "El barbero no está disponible "
                    "en ese horario."
                )


            # =================================================
            # 15. OTRAS RESERVAS
            # =================================================

            booking_conflict = (
                BookingRepository
                .has_booking_conflict(
                    db,
                    barber.id,
                    data.start_at,
                    end_at
                )
            )

            if booking_conflict:

                raise BookingConflictError(
                    "El horario acaba de ser reservado "
                    "por otro cliente."
                )


                        # =================================================
            # 15.1 SERVICIO A DOMICILIO
            # =================================================
            home_fee = 0
            is_home = data.booking_type == "HOME"

            if is_home:
                home_fee = (
                    BookingService
                    ._validate_home_service(
                        barbershop,
                        barber,
                        service,
                        data
                    )
                )

            # =================================================
            # 15.2 MÉTODO DE PAGO (pago directo a la barbería)
            # =================================================
            BookingService._validate_payment_method(
                db,
                barber.barbershop_id,
                data.payment_method
            )

            # =================================================
            # 16. ESTADO INICIAL
            # =================================================

            if (
                is_home
                or barbershop
                .requires_manual_confirmation
            ):
                initial_status_code = (
                    "PENDING"
                )

            else:

                initial_status_code = (
                    "CONFIRMED"
                )


            initial_status = (
                BookingRepository
                .get_status_by_code(
                    db,
                    initial_status_code
                )
            )

            if not initial_status:

                raise BookingStatusNotFoundError()


            # =================================================
            # 17. CREAR RESERVA
            # =================================================

            booking = Booking(
                client_user_id=current_user.id if current_user else None,
                guest_name=guest["name"] if guest else None,
                guest_email=guest["email"] if guest else None,
                guest_phone=guest.get("phone") if guest else None,
                manage_token=guest["manage_token"] if guest else None,
                contact_verified_at=guest.get("verified_at") if guest else None,
                booking_type="HOME" if is_home else "IN_SHOP",
                home_address=data.home.address if is_home else None,
                home_latitude=data.home.latitude if is_home else None,
                home_longitude=data.home.longitude if is_home else None,
                home_access_notes=data.home.access_notes if is_home else None,
                home_fee=home_fee,
                payment_method=data.payment_method,

                barbershop_id=
                    barber.barbershop_id,

                barber_id=
                    barber.id,

                service_id=
                    service.id,

                status_id=
                    initial_status.id,

                start_at=
                    data.start_at,

                end_at=
                    end_at,

                # Copiamos el precio actual.
                # Si el servicio cambia de precio
                # posteriormente, esta reserva conserva
                # el precio original.
                service_price=
                    service.price,

                customer_notes=
                    data.customer_notes
            )


            BookingRepository.create(
                db,
                booking
            )


            # =================================================
            # 18. CONFIRMAR TRANSACCIÓN
            # =================================================

            db.commit()

            db.refresh(
                booking
            )


            return (
                BookingService._to_response(
                    db,
                    booking
                )
            )


        # =====================================================
        # ERRORES DE NEGOCIO
        # =====================================================

        except (
            BarberNotFoundError,
            BarbershopNotFoundError,
            BarbershopInactiveError,
            BookingConflictError,
            BookingStatusNotFoundError,
            InvalidBookingTimeError,
            PastBookingTimeError,
            ServiceNotAvailableForBarberError
        ):

            db.rollback()

            raise


        # =====================================================
        # ERROR SQL
        # =====================================================

        except SQLAlchemyError:

            db.rollback()

            raise


    # =====================================================
    # MIS RESERVAS
    # =====================================================

    @staticmethod
    def list_my_bookings(
        db: Session,
        current_user: User
    ):

        bookings = (
            BookingRepository
            .list_by_client(
                db,
                current_user.id
            )
        )

        return [
            BookingService._to_response(
                db,
                booking
            )
            for booking in bookings
        ]
        
    
           # =====================================================
    # RESERVAS ASIGNADAS A UN BARBERO
    # =====================================================

    @staticmethod
    def list_barber_bookings(
        db: Session,
        barber_id: int,
        current_user: User,
        requested_date=None,
        status_code: str | None = None
    ):

        # -------------------------------------------------
        # 1. COMPROBAR BARBERO
        # -------------------------------------------------

        barber = (
            BarberRepository.get_by_id(
                db,
                barber_id
            )
        )

        if not barber:
            raise BarberNotFoundError()


        # -------------------------------------------------
        # 2. ROLES DEL USUARIO
        # -------------------------------------------------

        roles = {
            role.name
            for role in current_user.roles
        }


        # -------------------------------------------------
        # 3. PLATFORM ADMIN
        # -------------------------------------------------

        if "PLATFORM_ADMIN" in roles:

            has_access = True


        # -------------------------------------------------
        # 4. PROPIO BARBERO
        # -------------------------------------------------

        elif barber.user_id == current_user.id:

            has_access = True


        # -------------------------------------------------
        # 5. DUEÑO DE LA BARBERÍA
        # -------------------------------------------------

        else:

            barbershop = (
                BarbershopRepository.get_by_id(
                    db,
                    barber.barbershop_id
                )
            )

            has_access = (
                barbershop is not None
                and
                barbershop.owner_user_id
                == current_user.id
            )


        # -------------------------------------------------
        # 6. SIN PERMISOS
        # -------------------------------------------------

        if not has_access:

            raise BarbershopForbiddenError()


        # -------------------------------------------------
        # 7. CONSULTAR CON FILTROS
        # -------------------------------------------------

        bookings = (
            BookingRepository.list_by_barber(
                db,
                barber_id,
                requested_date=requested_date,
                status_code=status_code
            )
        )


        # -------------------------------------------------
        # 8. RESPUESTA
        # -------------------------------------------------

        return [
            BookingService._to_response(
                db,
                booking
            )
            for booking in bookings
        ]
        
    # =====================================================
    # VALIDAR PERMISOS SOBRE UNA RESERVA
    # =====================================================

    @staticmethod
    def _validate_booking_management(
        db: Session,
        booking: Booking,
        current_user: User
    ):

        roles = {
            role.name
            for role in current_user.roles
        }


        # PLATFORM_ADMIN puede gestionar cualquier reserva
        if "PLATFORM_ADMIN" in roles:

            return


        # Obtener barbero de la reserva
        barber = (
            BarberRepository.get_by_id(
                db,
                booking.barber_id
            )
        )

        if not barber:

            raise BarberNotFoundError()


        # El propio barbero puede gestionar su reserva
        if barber.user_id == current_user.id:

            return


        # El dueño de la barbería también puede hacerlo
        barbershop = (
            BarbershopRepository.get_by_id(
                db,
                booking.barbershop_id
            )
        )

        if (
            barbershop
            and
            barbershop.owner_user_id
            == current_user.id
        ):

            return


        raise BarbershopForbiddenError()
    
        # =====================================================
    # CONFIRMAR RESERVA
    # =====================================================

    @staticmethod
    def confirm_booking(
        db: Session,
        booking_id: int,
        current_user: User
    ):

        booking = (
            BookingRepository.get_by_id(
                db,
                booking_id
            )
        )

        if not booking:

            raise BookingNotFoundError()


        BookingService._validate_booking_management(
            db,
            booking,
            current_user
        )


        # Obtener estado actual
        current_status = (
            BookingRepository.get_status_by_id(
                db,
                booking.status_id
            )
        )

        if (
            not current_status
            or current_status.code != "PENDING"
        ):

            raise InvalidBookingStatusTransitionError(
                "Solo una reserva PENDING "
                "puede ser confirmada."
            )


        # Obtener estado destino
        confirmed_status = (
            BookingRepository.get_status_by_code(
                db,
                "CONFIRMED"
            )
        )

        if not confirmed_status:

            raise BookingStatusNotFoundError()


        try:

            booking.status_id = (
                confirmed_status.id
            )

            db.commit()

            db.refresh(
                booking
            )

            return (
                BookingService._to_response(
                    db,
                    booking
                )
            )


        except SQLAlchemyError:

            db.rollback()

            raise


    # =====================================================
    # RECHAZAR RESERVA
    # =====================================================

    @staticmethod
    def reject_booking(
        db: Session,
        booking_id: int,
        current_user: User
    ):

        booking = (
            BookingRepository.get_by_id(
                db,
                booking_id
            )
        )

        if not booking:

            raise BookingNotFoundError()


        BookingService._validate_booking_management(
            db,
            booking,
            current_user
        )


        # Obtener estado actual
        current_status = (
            BookingRepository.get_status_by_id(
                db,
                booking.status_id
            )
        )

        if (
            not current_status
            or current_status.code != "PENDING"
        ):

            raise InvalidBookingStatusTransitionError(
                "Solo una reserva PENDING "
                "puede ser rechazada."
            )


        rejected_status = (
            BookingRepository.get_status_by_code(
                db,
                "REJECTED"
            )
        )

        if not rejected_status:

            raise BookingStatusNotFoundError()


        try:

            booking.status_id = (
                rejected_status.id
            )

            db.commit()

            db.refresh(
                booking
            )

            return (
                BookingService._to_response(
                    db,
                    booking
                )
            )


        except SQLAlchemyError:

            db.rollback()

            raise
        
        
            # =====================================================
    # CANCELAR RESERVA POR PARTE DEL CLIENTE
    # =====================================================

    @staticmethod
    def cancel_by_customer(
        db: Session,
        booking_id: int,
        current_user: User
    ):

        # -------------------------------------------------
        # 1. BUSCAR RESERVA
        # -------------------------------------------------

        booking = (
            BookingRepository.get_by_id(
                db,
                booking_id
            )
        )

        if not booking:
            raise BookingNotFoundError()


        # -------------------------------------------------
        # 2. SOLO EL CLIENTE DUEÑO DE LA RESERVA
        #    PUEDE CANCELARLA POR ESTA RUTA
        # -------------------------------------------------

        if (
            booking.client_user_id
            != current_user.id
        ):

            raise BookingForbiddenError()


        # -------------------------------------------------
        # 3. OBTENER ESTADO ACTUAL
        # -------------------------------------------------

        current_status = (
            BookingRepository.get_status_by_id(
                db,
                booking.status_id
            )
        )

        if not current_status:

            raise BookingStatusNotFoundError()


        # -------------------------------------------------
        # 4. SOLO PENDING O CONFIRMED
        #    PUEDEN SER CANCELADAS POR EL CLIENTE
        # -------------------------------------------------

        allowed_statuses = {
            "PENDING",
            "CONFIRMED"
        }

        if (
            current_status.code
            not in allowed_statuses
        ):

            raise InvalidBookingStatusTransitionError(
                "Esta reserva ya no puede ser "
                "cancelada por el cliente."
            )


        # -------------------------------------------------
        # 5. COMPROBAR QUE LA CITA NO HAYA COMENZADO
        # -------------------------------------------------

        now = datetime.now()

        if now >= booking.start_at:

            raise BookingCancellationWindowError(
                "La cita ya comenzó o su hora "
                "programada ya pasó."
            )


        # -------------------------------------------------
        # 6. OBTENER POLÍTICA DE LA BARBERÍA
        # -------------------------------------------------

        barbershop = (
            BarbershopRepository.get_by_id(
                db,
                booking.barbershop_id
            )
        )

        if not barbershop:

            raise BarbershopNotFoundError()


        cancellation_hours = (
            barbershop.cancellation_hours_before
            or 0
        )


        # -------------------------------------------------
        # 7. CALCULAR FECHA/HORA LÍMITE
        #
        # Ejemplo:
        #
        # cita: 18:00
        # política: 2 horas
        #
        # límite: 16:00
        # -------------------------------------------------

        cancellation_deadline = (
            booking.start_at
            - timedelta(
                hours=cancellation_hours
            )
        )


        # -------------------------------------------------
        # 8. COMPROBAR VENTANA DE CANCELACIÓN
        # -------------------------------------------------

        if now > cancellation_deadline:

            raise BookingCancellationWindowError(
                (
                    "La reserva solo puede cancelarse "
                    f"hasta {cancellation_hours} hora(s) "
                    "antes de la cita."
                )
            )


        # -------------------------------------------------
        # 9. OBTENER ESTADO DESTINO
        # -------------------------------------------------

        cancelled_status = (
            BookingRepository.get_status_by_code(
                db,
                "CANCELLED_BY_CUSTOMER"
            )
        )

        if not cancelled_status:

            raise BookingStatusNotFoundError()


        # -------------------------------------------------
        # 10. ACTUALIZAR
        # -------------------------------------------------

        try:

            booking.status_id = (
                cancelled_status.id
            )

            db.commit()

            db.refresh(
                booking
            )

            return (
                BookingService._to_response(
                    db,
                    booking
                )
            )


        except SQLAlchemyError:

            db.rollback()

            raise
        
        
            # =====================================================
    # INICIAR SERVICIO
    # CONFIRMED -> IN_PROGRESS
    # =====================================================

    @staticmethod
    def start_booking(
        db: Session,
        booking_id: int,
        current_user: User
    ):

        # -------------------------------------------------
        # 1. BUSCAR RESERVA
        # -------------------------------------------------

        booking = (
            BookingRepository.get_by_id(
                db,
                booking_id
            )
        )

        if not booking:
            raise BookingNotFoundError()


        # -------------------------------------------------
        # 2. VALIDAR PERMISOS
        #
        # Puede hacerlo:
        # - Barbero asignado
        # - Dueño de la barbería
        # - PLATFORM_ADMIN
        # -------------------------------------------------

        BookingService._validate_booking_management(
            db,
            booking,
            current_user
        )


        # -------------------------------------------------
        # 3. OBTENER ESTADO ACTUAL
        # -------------------------------------------------

        current_status = (
            BookingRepository.get_status_by_id(
                db,
                booking.status_id
            )
        )

        if not current_status:
            raise BookingStatusNotFoundError()


        # -------------------------------------------------
        # 4. SOLO CONFIRMED PUEDE INICIARSE
        # -------------------------------------------------

        if current_status.code != "CONFIRMED":

            raise InvalidBookingStatusTransitionError(
                "Solo una reserva CONFIRMED "
                "puede iniciar el servicio."
            )


        # -------------------------------------------------
        # 5. NO INICIAR ANTES DE LA HORA PROGRAMADA
        # -------------------------------------------------

        if datetime.now() < booking.start_at:

            raise InvalidBookingTimeError(
                "El servicio no puede iniciarse "
                "antes de la hora programada."
            )


        # -------------------------------------------------
        # 6. OBTENER IN_PROGRESS
        # -------------------------------------------------

        in_progress_status = (
            BookingRepository.get_status_by_code(
                db,
                "IN_PROGRESS"
            )
        )

        if not in_progress_status:
            raise BookingStatusNotFoundError()


        # -------------------------------------------------
        # 7. CAMBIAR ESTADO
        # -------------------------------------------------

        try:

            booking.status_id = (
                in_progress_status.id
            )

            db.commit()

            db.refresh(
                booking
            )

            return (
                BookingService._to_response(
                    db,
                    booking
                )
            )

        except SQLAlchemyError:

            db.rollback()

            raise


    # =====================================================
    # COMPLETAR SERVICIO
    # IN_PROGRESS -> COMPLETED
    # =====================================================

    @staticmethod
    def complete_booking(
        db: Session,
        booking_id: int,
        current_user: User
    ):

        # -------------------------------------------------
        # 1. BUSCAR RESERVA
        # -------------------------------------------------

        booking = (
            BookingRepository.get_by_id(
                db,
                booking_id
            )
        )

        if not booking:
            raise BookingNotFoundError()


        # -------------------------------------------------
        # 2. VALIDAR PERMISOS
        # -------------------------------------------------

        BookingService._validate_booking_management(
            db,
            booking,
            current_user
        )


        # -------------------------------------------------
        # 3. OBTENER ESTADO ACTUAL
        # -------------------------------------------------

        current_status = (
            BookingRepository.get_status_by_id(
                db,
                booking.status_id
            )
        )

        if not current_status:
            raise BookingStatusNotFoundError()


        # -------------------------------------------------
        # 4. SOLO IN_PROGRESS PUEDE COMPLETARSE
        # -------------------------------------------------

        if current_status.code != "IN_PROGRESS":

            raise InvalidBookingStatusTransitionError(
                "Solo una reserva IN_PROGRESS "
                "puede marcarse como completada."
            )


        # -------------------------------------------------
        # 5. OBTENER COMPLETED
        # -------------------------------------------------

        completed_status = (
            BookingRepository.get_status_by_code(
                db,
                "COMPLETED"
            )
        )

        if not completed_status:
            raise BookingStatusNotFoundError()


        # -------------------------------------------------
        # 6. CAMBIAR ESTADO
        # -------------------------------------------------

        try:

            booking.status_id = (
                completed_status.id
            )

            db.commit()

            db.refresh(
                booking
            )

            return (
                BookingService._to_response(
                    db,
                    booking
                )
            )

        except SQLAlchemyError:

            db.rollback()

            raise
        
            # =====================================================
    # MARCAR CLIENTE COMO NO SHOW
    # CONFIRMED -> NO_SHOW
    # =====================================================

    @staticmethod
    def mark_no_show(
        db: Session,
        booking_id: int,
        current_user: User
    ):

        # -------------------------------------------------
        # 1. BUSCAR RESERVA
        # -------------------------------------------------

        booking = (
            BookingRepository.get_by_id(
                db,
                booking_id
            )
        )

        if not booking:
            raise BookingNotFoundError()


        # -------------------------------------------------
        # 2. VALIDAR PERMISOS
        #
        # Permitidos:
        # - Barbero asignado
        # - Dueño de la barbería
        # - PLATFORM_ADMIN
        # -------------------------------------------------

        BookingService._validate_booking_management(
            db,
            booking,
            current_user
        )


        # -------------------------------------------------
        # 3. OBTENER ESTADO ACTUAL
        # -------------------------------------------------

        current_status = (
            BookingRepository.get_status_by_id(
                db,
                booking.status_id
            )
        )

        if not current_status:
            raise BookingStatusNotFoundError()


        # -------------------------------------------------
        # 4. SOLO CONFIRMED PUEDE PASAR A NO_SHOW
        # -------------------------------------------------

        if current_status.code != "CONFIRMED":

            raise InvalidBookingStatusTransitionError(
                "Solo una reserva CONFIRMED "
                "puede marcarse como NO_SHOW."
            )


        # -------------------------------------------------
        # 5. OBTENER BARBERÍA
        # -------------------------------------------------

        barbershop = (
            BarbershopRepository.get_by_id(
                db,
                booking.barbershop_id
            )
        )

        if not barbershop:
            raise BarbershopNotFoundError()


        # -------------------------------------------------
        # 6. OBTENER MINUTOS DE TOLERANCIA
        # -------------------------------------------------

        tolerance_minutes = (
            barbershop.tolerance_minutes
            or 0
        )


        # -------------------------------------------------
        # 7. CALCULAR HORA EN QUE PUEDE
        #    MARCARSE COMO NO_SHOW
        #
        # Ejemplo:
        #
        # cita: 10:00
        # tolerancia: 15
        #
        # no_show_available_at = 10:15
        # -------------------------------------------------

        no_show_available_at = (
            booking.start_at
            + timedelta(
                minutes=tolerance_minutes
            )
        )


        # -------------------------------------------------
        # 8. VALIDAR TOLERANCIA
        # -------------------------------------------------

        now = datetime.now()

        if now < no_show_available_at:

            raise InvalidBookingTimeError(
                (
                    "La reserva solo puede marcarse "
                    "como NO_SHOW después de "
                    f"{tolerance_minutes} minuto(s) "
                    "de tolerancia."
                )
            )


        # -------------------------------------------------
        # 9. OBTENER ESTADO NO_SHOW
        # -------------------------------------------------

        no_show_status = (
            BookingRepository.get_status_by_code(
                db,
                "NO_SHOW"
            )
        )

        if not no_show_status:
            raise BookingStatusNotFoundError()


        # -------------------------------------------------
        # 10. CAMBIAR ESTADO
        # -------------------------------------------------

        try:

            booking.status_id = (
                no_show_status.id
            )

            db.commit()

            db.refresh(
                booking
            )

            return (
                BookingService._to_response(
                    db,
                    booking
                )
            )


        except SQLAlchemyError:

            db.rollback()

            raise