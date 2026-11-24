from datetime import datetime

from sqlalchemy import (
    select
)

from sqlalchemy.orm import Session

from app.models.barber_block_model import BarberBlock
from app.models.barber_schedule_model import BarberSchedule
from app.models.barbershop_schedule_model import BarbershopSchedule
from app.models.barbershop_break_model import BarbershopBreak


class ScheduleRepository:

    # =====================================================
    # BARBERÍA
    # =====================================================

    @staticmethod
    def get_barbershop_day(
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
                == day_of_week
            )
        )

        return db.scalar(
            statement
        )


    @staticmethod
    def list_barbershop(
        db: Session,
        barbershop_id: int
    ) -> list[BarbershopSchedule]:

        statement = (
            select(BarbershopSchedule)
            .where(
                BarbershopSchedule.barbershop_id
                == barbershop_id
            )
            .order_by(
                BarbershopSchedule.day_of_week.asc()
            )
        )

        return list(
            db.scalars(
                statement
            ).all()
        )


    # =====================================================
    # BARBERO
    # =====================================================

    @staticmethod
    def get_barber_day(
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
                == day_of_week
            )
        )

        return db.scalar(
            statement
        )


    @staticmethod
    def list_barber(
        db: Session,
        barber_id: int
    ) -> list[BarberSchedule]:

        statement = (
            select(BarberSchedule)
            .where(
                BarberSchedule.barber_id
                == barber_id
            )
            .order_by(
                BarberSchedule.day_of_week.asc()
            )
        )

        return list(
            db.scalars(
                statement
            ).all()
        )


    # =====================================================
    # BLOQUEOS
    # =====================================================

    @staticmethod
    def create_block(
        db: Session,
        block: BarberBlock
    ) -> BarberBlock:

        db.add(
            block
        )

        db.flush()

        return block


    @staticmethod
    def get_block_by_id(
        db: Session,
        block_id: int
    ) -> BarberBlock | None:

        statement = (
            select(BarberBlock)
            .where(
                BarberBlock.id
                == block_id
            )
        )

        return db.scalar(
            statement
        )


    @staticmethod
    def list_blocks(
        db: Session,
        barber_id: int
    ) -> list[BarberBlock]:

        statement = (
            select(BarberBlock)
            .where(
                BarberBlock.barber_id
                == barber_id
            )
            .order_by(
                BarberBlock.start_at.asc()
            )
        )

        return list(
            db.scalars(
                statement
            ).all()
        )


    @staticmethod
    def list_blocks_in_range(
        db: Session,
        barber_id: int,
        start_at: datetime,
        end_at: datetime
    ) -> list[BarberBlock]:

        statement = (
            select(BarberBlock)
            .where(
                BarberBlock.barber_id
                == barber_id,

                BarberBlock.start_at
                < end_at,

                BarberBlock.end_at
                > start_at
            )
            .order_by(
                BarberBlock.start_at.asc()
            )
        )

        return list(
            db.scalars(
                statement
            ).all()
        )


    @staticmethod
    def has_overlapping_block(
        db: Session,
        barber_id: int,
        start_at: datetime,
        end_at: datetime
    ) -> bool:

        statement = (
            select(
                BarberBlock.id
            )
            .where(
                BarberBlock.barber_id
                == barber_id,

                BarberBlock.start_at
                < end_at,

                BarberBlock.end_at
                > start_at
            )
            .limit(
                1
            )
        )

        return (
            db.scalar(
                statement
            )
            is not None
        )


    @staticmethod
    def delete_block(
        db: Session,
        block: BarberBlock
    ):

        db.delete(
            block
        )

        db.flush()


    # =====================================================
    # DESCANSOS DE BARBERÍA
    # =====================================================

    @staticmethod
    def create_barbershop_break(
        db: Session,
        break_item: BarbershopBreak
    ) -> BarbershopBreak:

        db.add(
            break_item
        )

        db.flush()

        return break_item


    @staticmethod
    def get_barbershop_break_by_id(
        db: Session,
        break_id: int
    ) -> BarbershopBreak | None:

        statement = (
            select(BarbershopBreak)
            .where(
                BarbershopBreak.id
                == break_id
            )
        )

        return db.scalar(
            statement
        )


    @staticmethod
    def list_barbershop_breaks(
        db: Session,
        barbershop_id: int
    ) -> list[BarbershopBreak]:

        statement = (
            select(BarbershopBreak)
            .where(
                BarbershopBreak.barbershop_id
                == barbershop_id
            )
            .order_by(
                BarbershopBreak.day_of_week.asc(),
                BarbershopBreak.start_time.asc()
            )
        )

        return list(
            db.scalars(
                statement
            ).all()
        )


    # =====================================================
    # DESCANSOS ACTIVOS DE BARBERÍA
    # =====================================================

    @staticmethod
    def list_active_barbershop_breaks(
        db: Session,
        barbershop_id: int
    ) -> list[BarbershopBreak]:

        statement = (
            select(BarbershopBreak)
            .where(
                BarbershopBreak.barbershop_id
                == barbershop_id,

                BarbershopBreak.is_active.is_(
                    True
                )
            )
            .order_by(
                BarbershopBreak.day_of_week.asc(),
                BarbershopBreak.start_time.asc()
            )
        )

        return list(
            db.scalars(
                statement
            ).all()
        )


    @staticmethod
    def has_overlapping_barbershop_break(
        db: Session,
        barbershop_id: int,
        day_of_week: int,
        start_time,
        end_time,
        exclude_break_id: int | None = None
    ) -> bool:

        statement = (
            select(
                BarbershopBreak.id
            )
            .where(
                BarbershopBreak.barbershop_id
                == barbershop_id,

                BarbershopBreak.day_of_week
                == day_of_week,

                BarbershopBreak.is_active.is_(
                    True
                ),

                BarbershopBreak.start_time
                < end_time,

                BarbershopBreak.end_time
                > start_time
            )
        )


        if (
            exclude_break_id
            is not None
        ):

            statement = (
                statement
                .where(
                    BarbershopBreak.id
                    != exclude_break_id
                )
            )


        statement = (
            statement
            .limit(
                1
            )
        )


        return (
            db.scalar(
                statement
            )
            is not None
        )


    @staticmethod
    def delete_barbershop_break(
        db: Session,
        break_item: BarbershopBreak
    ):

        db.delete(
            break_item
        )

        db.flush()