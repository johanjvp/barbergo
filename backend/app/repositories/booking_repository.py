from datetime import (
    date,
    datetime,
    timedelta
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.barber_block_model import (
    BarberBlock
)

from app.models.barber_model import (
    Barber
)

from app.models.barbershop_break_model import (
    BarbershopBreak
)

from app.models.booking_model import (
    Booking
)

from app.models.booking_status_model import (
    BookingStatus
)


class BookingRepository:

    BLOCKING_STATUSES = [
        "PENDING",
        "CONFIRMED",
        "IN_PROGRESS"
    ]


    # =====================================================
    # BLOQUEAR BARBERO
    #
    # Esto ayuda a evitar que dos clientes creen
    # simultáneamente una reserva para el mismo barbero.
    # =====================================================

    @staticmethod
    def lock_barber(
        db: Session,
        barber_id: int
    ) -> Barber | None:

        statement = (
            select(Barber)
            .where(
                Barber.id == barber_id,
                Barber.is_active.is_(True)
            )
            .with_for_update()
        )

        return db.scalar(statement)


    # =====================================================
    # ESTADO POR CÓDIGO
    # =====================================================

    @staticmethod
    def get_status_by_code(
        db: Session,
        code: str
    ) -> BookingStatus | None:

        statement = (
            select(BookingStatus)
            .where(
                BookingStatus.code == code
            )
        )

        return db.scalar(statement)


    # =====================================================
    # ESTADO POR ID
    # =====================================================

    @staticmethod
    def get_status_by_id(
        db: Session,
        status_id: int
    ) -> BookingStatus | None:

        statement = (
            select(BookingStatus)
            .where(
                BookingStatus.id == status_id
            )
        )

        return db.scalar(statement)


    # =====================================================
    # VERIFICAR DESCANSOS / ALMUERZO
    # =====================================================

    @staticmethod
    def has_barbershop_break_conflict(
        db: Session,
        barbershop_id: int,
        day_of_week: int,
        requested_date,
        start_at: datetime,
        end_at: datetime
    ) -> bool:

        breaks = (
            db.scalars(
                select(BarbershopBreak)
                .where(
                    BarbershopBreak.barbershop_id
                    == barbershop_id,

                    BarbershopBreak.day_of_week
                    == day_of_week,

                    BarbershopBreak.is_active.is_(True)
                )
            )
            .all()
        )

        for break_item in breaks:

            break_start = datetime.combine(
                requested_date,
                break_item.start_time
            )

            break_end = datetime.combine(
                requested_date,
                break_item.end_time
            )

            if (
                start_at < break_end
                and end_at > break_start
            ):

                return True

        return False


    # =====================================================
    # VERIFICAR BLOQUEOS DEL BARBERO
    # =====================================================

    @staticmethod
    def has_barber_block_conflict(
        db: Session,
        barber_id: int,
        start_at: datetime,
        end_at: datetime
    ) -> bool:

        statement = (
            select(BarberBlock.id)
            .where(
                BarberBlock.barber_id
                == barber_id,

                BarberBlock.start_at
                < end_at,

                BarberBlock.end_at
                > start_at
            )
            .limit(1)
        )

        return (
            db.scalar(statement)
            is not None
        )


    # =====================================================
    # VERIFICAR OTRAS RESERVAS
    # =====================================================

    @staticmethod
    def has_booking_conflict(
        db: Session,
        barber_id: int,
        start_at: datetime,
        end_at: datetime
    ) -> bool:

        statement = (
            select(Booking.id)
            .join(
                BookingStatus,
                BookingStatus.id
                == Booking.status_id
            )
            .where(
                Booking.barber_id
                == barber_id,

                Booking.start_at
                < end_at,

                Booking.end_at
                > start_at,

                BookingStatus.code.in_(
                    BookingRepository
                    .BLOCKING_STATUSES
                )
            )
            .limit(1)
        )

        return (
            db.scalar(statement)
            is not None
        )


    # =====================================================
    # CREAR RESERVA
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        booking: Booking
    ) -> Booking:

        db.add(
            booking
        )

        db.flush()

        return booking


    # =====================================================
    # RESERVAS DEL CLIENTE
    # =====================================================

    @staticmethod
    def list_by_client(
        db: Session,
        client_user_id: int
    ) -> list[Booking]:

        statement = (
            select(Booking)
            .where(
                Booking.client_user_id
                == client_user_id
            )
            .order_by(
                Booking.start_at.desc()
            )
        )

        return list(
            db.scalars(statement).all()
        )
        
                # =====================================================
    # RESERVAS DE UN BARBERO
    # CON FILTROS OPCIONALES
    # =====================================================

    @staticmethod
    def list_by_barber(
        db: Session,
        barber_id: int,
        requested_date: date | None = None,
        status_code: str | None = None
    ) -> list[Booking]:

        statement = (
            select(Booking)
            .where(
                Booking.barber_id
                == barber_id
            )
        )


        # -------------------------------------------------
        # FILTRAR POR FECHA
        #
        # No usamos DATE(start_at), porque preferimos
        # comparar por rango:
        #
        # 2026-09-21 00:00
        # hasta
        # 2026-09-22 00:00
        # -------------------------------------------------

        if requested_date is not None:

            day_start = datetime.combine(
                requested_date,
                datetime.min.time()
            )

            day_end = (
                day_start
                + timedelta(days=1)
            )

            statement = statement.where(
                Booking.start_at >= day_start,
                Booking.start_at < day_end
            )


        # -------------------------------------------------
        # FILTRAR POR ESTADO
        # -------------------------------------------------

        if status_code is not None:

            statement = (
                statement
                .join(
                    BookingStatus,
                    BookingStatus.id
                    == Booking.status_id
                )
                .where(
                    BookingStatus.code
                    == status_code
                )
            )


        # -------------------------------------------------
        # ORDEN CRONOLÓGICO
        # -------------------------------------------------

        statement = (
            statement
            .order_by(
                Booking.start_at.asc()
            )
        )

        return list(
            db.scalars(statement).all()
        )
        
            # =====================================================
    # OBTENER RESERVA POR ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        booking_id: int
    ) -> Booking | None:

        statement = (
            select(Booking)
            .where(
                Booking.id == booking_id
            )
        )

        return db.scalar(statement)