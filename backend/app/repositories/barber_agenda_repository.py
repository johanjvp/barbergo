from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.barber_model import Barber
from app.models.barbershop_model import Barbershop
from app.models.booking_model import Booking
from app.models.booking_status_model import BookingStatus
from app.models.service_model import Service
from app.models.user_model import User


class BarberAgendaRepository:


    # =====================================================
    # OBTENER BARBERO POR USUARIO AUTENTICADO
    # =====================================================

    @staticmethod
    def get_barber_by_user_id(
        db: Session,
        user_id: int
    ) -> dict | None:

        statement = (
            select(
                Barber.id.label(
                    "barber_id"
                ),

                Barber.user_id,

                Barber.barbershop_id,

                Barber.is_active.label(
                    "barber_is_active"
                ),

                User.first_name,

                User.last_name,

                Barbershop.name.label(
                    "barbershop_name"
                ),

                Barbershop.address.label(
                    "barbershop_address"
                ),

                Barbershop.city.label(
                    "barbershop_city"
                ),

                Barbershop.is_active.label(
                    "barbershop_is_active"
                )
            )

            .join(
                User,
                User.id == Barber.user_id
            )

            .join(
                Barbershop,
                Barbershop.id
                ==
                Barber.barbershop_id
            )

            .where(
                Barber.user_id
                ==
                user_id
            )

            .limit(1)
        )


        row = (
            db.execute(
                statement
            )
            .mappings()
            .first()
        )


        if not row:

            return None


        return dict(
            row
        )


    # =====================================================
    # OBTENER AGENDA DEL BARBERO
    # =====================================================

    @staticmethod
    def get_bookings(
        db: Session,
        barber_id: int,
        start_at: datetime,
        end_at: datetime
    ) -> list[dict]:

        statement = (

            select(

                Booking.id,

                Booking.client_user_id,

                Booking.service_id,

                Booking.status_id,

                Booking.start_at,

                Booking.end_at,

                Booking.service_price,

                Booking.customer_notes,

                Booking.barber_notes,


                # -----------------------------------------
                # CLIENTE
                # -----------------------------------------

                User.first_name.label(
                    "client_first_name"
                ),

                User.last_name.label(
                    "client_last_name"
                ),

                User.phone.label(
                    "client_phone"
                ),


                # -----------------------------------------
                # SERVICIO
                # -----------------------------------------

                Service.name.label(
                    "service_name"
                ),

                Service.duration_minutes.label(
                    "duration_minutes"
                ),


                # -----------------------------------------
                # ESTADO
                # -----------------------------------------

                BookingStatus.code.label(
                    "status_code"
                ),

                BookingStatus.name.label(
                    "status_name"
                )

            )

            .join(
                User,
                User.id
                ==
                Booking.client_user_id
            )

            .join(
                Service,
                Service.id
                ==
                Booking.service_id
            )

            .join(
                BookingStatus,
                BookingStatus.id
                ==
                Booking.status_id
            )

            .where(

                Booking.barber_id
                ==
                barber_id,

                Booking.start_at
                >=
                start_at,

                Booking.start_at
                <
                end_at
            )

            .order_by(
                Booking.start_at.asc()
            )

        )


        rows = (
            db.execute(
                statement
            )
            .mappings()
            .all()
        )


        return [
            dict(
                row
            )
            for row in rows
        ]