from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.barbershop_break_model import (
    BarbershopBreak
)

from app.models.barbershop_schedule_model import (
    BarbershopSchedule
)

from app.models.barber_block_model import (
    BarberBlock
)

from app.models.barber_model import (
    Barber
)

from app.models.barber_schedule_model import (
    BarberSchedule
)

from app.models.barber_service_association import (
    barber_services
)

from app.models.booking_model import (
    Booking
)

from app.models.booking_status_model import (
    BookingStatus
)

from app.models.service_model import (
    Service
)


class AvailabilityRepository:

    # =====================================================
    # BARBERO
    # =====================================================

    @staticmethod
    def get_barber(
        db: Session,
        barber_id: int
    ) -> Barber | None:

        statement = (
            select(Barber)
            .where(
                Barber.id == barber_id,
                Barber.is_active.is_(True)
            )
        )

        return db.scalar(statement)


    # =====================================================
    # SERVICIO DEL BARBERO
    # =====================================================

    @staticmethod
    def get_service_for_barber(
        db: Session,
        barber_id: int,
        service_id: int
    ) -> Service | None:

        statement = (
            select(Service)
            .join(
                barber_services,
                barber_services.c.service_id
                == Service.id
            )
            .where(
                barber_services.c.barber_id
                == barber_id,

                Service.id
                == service_id,

                Service.is_active.is_(True)
            )
        )

        return db.scalar(statement)


    # =====================================================
    # HORARIO DE LA BARBERÍA
    # =====================================================

    @staticmethod
    def get_barbershop_schedule(
        db: Session,
        barbershop_id: int,
        day_of_week: int
    ) -> BarbershopSchedule | None:

        statement = (
            select(BarbershopSchedule)
            .where(
                BarbershopSchedule.barbershop_id
                == barbershop_id,

                BarbershopSchedule.day_of_week
                == day_of_week,

                BarbershopSchedule.is_open.is_(True)
            )
        )

        return db.scalar(statement)


    # =====================================================
    # DESCANSOS DE LA BARBERÍA
    # =====================================================

    @staticmethod
    def get_barbershop_breaks(
        db: Session,
        barbershop_id: int,
        day_of_week: int
    ) -> list[BarbershopBreak]:

        statement = (
            select(BarbershopBreak)
            .where(
                BarbershopBreak.barbershop_id
                == barbershop_id,

                BarbershopBreak.day_of_week
                == day_of_week,

                BarbershopBreak.is_active.is_(True)
            )
            .order_by(
                BarbershopBreak.start_time.asc()
            )
        )

        return list(
            db.scalars(statement).all()
        )


    # =====================================================
    # HORARIO DEL BARBERO
    # =====================================================

    @staticmethod
    def get_barber_schedule(
        db: Session,
        barber_id: int,
        day_of_week: int
    ) -> BarberSchedule | None:

        statement = (
            select(BarberSchedule)
            .where(
                BarberSchedule.barber_id
                == barber_id,

                BarberSchedule.day_of_week
                == day_of_week,

                BarberSchedule.is_working.is_(True)
            )
        )

        return db.scalar(statement)


    # =====================================================
    # BLOQUEOS PARTICULARES DEL BARBERO
    # =====================================================

    @staticmethod
    def get_blocks(
        db: Session,
        barber_id: int,
        start_day: datetime,
        end_day: datetime
    ) -> list[BarberBlock]:

        statement = (
            select(BarberBlock)
            .where(
                BarberBlock.barber_id
                == barber_id,

                BarberBlock.start_at
                < end_day,

                BarberBlock.end_at
                > start_day
            )
            .order_by(
                BarberBlock.start_at.asc()
            )
        )

        return list(
            db.scalars(statement).all()
        )


    # =====================================================
    # RESERVAS QUE OCUPAN HORARIO
    # =====================================================

    @staticmethod
    def get_blocking_bookings(
        db: Session,
        barber_id: int,
        start_day: datetime,
        end_day: datetime
    ) -> list[Booking]:

        blocking_statuses = [
            "PENDING",
            "CONFIRMED",
            "IN_PROGRESS"
        ]

        statement = (
            select(Booking)
            .join(
                BookingStatus,
                BookingStatus.id
                == Booking.status_id
            )
            .where(
                Booking.barber_id
                == barber_id,

                Booking.start_at
                < end_day,

                Booking.end_at
                > start_day,

                BookingStatus.code.in_(
                    blocking_statuses
                )
            )
            .order_by(
                Booking.start_at.asc()
            )
        )

        return list(
            db.scalars(statement).all()
        )