from datetime import (
    date,
    datetime,
    time,
    timedelta
)

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BarbershopForbiddenError,
    BarbershopNotFoundError,
    BarberNotFoundError,
    BarberBlockNotFoundError,
    BarberScheduleForbiddenError,
    InvalidScheduleError,
    BarbershopBreakNotFoundError,
    InvalidBarbershopBreakError,
    BarbershopBreakConflictError,
)

from app.models.barber_block_model import BarberBlock
from app.models.barber_schedule_model import BarberSchedule
from app.models.barbershop_schedule_model import BarbershopSchedule
from app.models.barbershop_break_model import BarbershopBreak
from app.models.user_model import User

from app.repositories.barber_repository import BarberRepository
from app.repositories.barbershop_repository import BarbershopRepository
from app.repositories.schedule_repository import ScheduleRepository

from app.schemas.schedule_schema import (
    BarbershopScheduleUpsert,
    BarberScheduleUpsert,
    BarberBlockCreate,
    AgendaBreakResponse,
    AgendaBlockResponse,
    BarberAgendaDayResponse,
    BarberWeeklyAgendaResponse
)


class ScheduleService:

    # =====================================================
    # PERMISOS BARBERÍA
    # =====================================================

    @staticmethod
    def _validate_barbershop_management(
        db: Session,
        barbershop_id: int,
        current_user: User
    ):

        barbershop = BarbershopRepository.get_by_id(
            db,
            barbershop_id
        )

        if not barbershop:
            raise BarbershopNotFoundError()

        roles = {
            role.name
            for role in current_user.roles
        }

        is_platform_admin = (
            "PLATFORM_ADMIN" in roles
        )

        is_owner = (
            barbershop.owner_user_id
            == current_user.id
        )

        if (
            not is_platform_admin
            and
            not is_owner
        ):
            raise BarbershopForbiddenError()

        return barbershop


    # =====================================================
    # PERMISOS BARBERO
    # =====================================================

    @staticmethod
    def _validate_barber_management(
        db: Session,
        barber_id: int,
        current_user: User
    ):

        barber = BarberRepository.get_by_id(
            db,
            barber_id
        )

        if not barber:
            raise BarberNotFoundError()

        roles = {
            role.name
            for role in current_user.roles
        }

        # -------------------------------------------------
        # PLATFORM ADMIN
        # -------------------------------------------------

        if (
            "PLATFORM_ADMIN"
            in roles
        ):

            return barber


        # -------------------------------------------------
        # EL MISMO BARBERO
        # -------------------------------------------------

        if (
            barber.user_id
            ==
            current_user.id
        ):

            return barber


        # -------------------------------------------------
        # PROPIETARIO DE LA BARBERÍA
        # -------------------------------------------------

        barbershop = BarbershopRepository.get_by_id(
            db,
            barber.barbershop_id
        )

        if (
            barbershop
            and
            barbershop.owner_user_id
            ==
            current_user.id
        ):

            return barber


        raise BarberScheduleForbiddenError()


    # =====================================================
    # HORARIO BARBERÍA
    # =====================================================

    @staticmethod
    def set_barbershop_schedule(
        db: Session,
        barbershop_id: int,
        day_of_week: int,
        data: BarbershopScheduleUpsert,
        current_user: User
    ):

        ScheduleService._validate_barbershop_management(
            db,
            barbershop_id,
            current_user
        )


        schedule = (
            ScheduleRepository
            .get_barbershop_day(
                db,
                barbershop_id,
                day_of_week
            )
        )


        try:

            if schedule is None:

                schedule = BarbershopSchedule(
                    barbershop_id=barbershop_id,
                    day_of_week=day_of_week
                )

                db.add(
                    schedule
                )


            schedule.open_time = (
                data.open_time
            )

            schedule.close_time = (
                data.close_time
            )

            schedule.is_open = (
                data.is_open
            )


            db.commit()

            db.refresh(
                schedule
            )


            return schedule


        except SQLAlchemyError:

            db.rollback()

            raise


    # =====================================================
    # LISTAR HORARIO BARBERÍA
    # =====================================================

    @staticmethod
    def list_barbershop_schedule(
        db: Session,
        barbershop_id: int
    ):

        barbershop = (
            BarbershopRepository
            .get_by_id(
                db,
                barbershop_id
            )
        )


        if not barbershop:

            raise BarbershopNotFoundError()


        return (
            ScheduleRepository
            .list_barbershop(
                db,
                barbershop_id
            )
        )


    # =====================================================
    # HORARIO BARBERO
    # =====================================================

    @staticmethod
    def set_barber_schedule(
        db: Session,
        barber_id: int,
        day_of_week: int,
        data: BarberScheduleUpsert,
        current_user: User
    ):

        barber = (
            ScheduleService
            ._validate_barber_management(
                db,
                barber_id,
                current_user
            )
        )


        shop_schedule = (
            ScheduleRepository
            .get_barbershop_day(
                db,
                barber.barbershop_id,
                day_of_week
            )
        )


        # -------------------------------------------------
        # VALIDAR JORNADA DEL BARBERO
        # -------------------------------------------------

        if data.is_working:

            if (
                not shop_schedule
                or
                not shop_schedule.is_open
            ):

                raise InvalidScheduleError(
                    "La barbería está cerrada ese día."
                )


            if (
                data.start_time
                <
                shop_schedule.open_time
                or
                data.end_time
                >
                shop_schedule.close_time
            ):

                raise InvalidScheduleError(
                    "El horario del barbero debe estar "
                    "dentro del horario de la barbería."
                )


        schedule = (
            ScheduleRepository
            .get_barber_day(
                db,
                barber_id,
                day_of_week
            )
        )


        try:

            if schedule is None:

                schedule = BarberSchedule(
                    barber_id=barber_id,
                    day_of_week=day_of_week
                )

                db.add(
                    schedule
                )


            schedule.start_time = (
                data.start_time
            )

            schedule.end_time = (
                data.end_time
            )

            schedule.is_working = (
                data.is_working
            )


            db.commit()

            db.refresh(
                schedule
            )


            return schedule


        except SQLAlchemyError:

            db.rollback()

            raise


    # =====================================================
    # LISTAR HORARIO BARBERO
    # =====================================================

    @staticmethod
    def list_barber_schedule(
        db: Session,
        barber_id: int
    ):

        barber = (
            BarberRepository
            .get_by_id(
                db,
                barber_id
            )
        )


        if not barber:

            raise BarberNotFoundError()


        return (
            ScheduleRepository
            .list_barber(
                db,
                barber_id
            )
        )


    # =====================================================
    # AGENDA SEMANAL DEL BARBERO
    # =====================================================

    @staticmethod
    def get_barber_weekly_agenda(
        db: Session,
        barber_id: int,
        week_start: date
    ) -> BarberWeeklyAgendaResponse:

        # -------------------------------------------------
        # OBTENER BARBERO
        # -------------------------------------------------

        barber = (
            BarberRepository
            .get_by_id(
                db,
                barber_id
            )
        )


        if not barber:

            raise BarberNotFoundError()


        # -------------------------------------------------
        # NORMALIZAR LA SEMANA AL LUNES
        # -------------------------------------------------
        #
        # Python:
        # lunes = 0
        # martes = 1
        # ...
        #
        # BarberGo:
        # lunes = 1
        # martes = 2
        # ...
        # domingo = 7
        # -------------------------------------------------

        monday = (
            week_start
            -
            timedelta(
                days=
                    week_start.weekday()
            )
        )


        sunday = (
            monday
            +
            timedelta(
                days=6
            )
        )


        # -------------------------------------------------
        # RANGO DE CONSULTA PARA BLOQUEOS
        # -------------------------------------------------

        range_start = (
            datetime.combine(
                monday,
                time.min
            )
        )


        range_end = (
            datetime.combine(
                sunday
                +
                timedelta(
                    days=1
                ),
                time.min
            )
        )


        # -------------------------------------------------
        # HORARIO DE LA BARBERÍA
        # -------------------------------------------------

        barbershop_schedules = (
            ScheduleRepository
            .list_barbershop(
                db,
                barber.barbershop_id
            )
        )


        barbershop_schedule_map = {

            item.day_of_week:
                item

            for item
            in barbershop_schedules

        }


        # -------------------------------------------------
        # HORARIO DEL BARBERO
        # -------------------------------------------------

        barber_schedules = (
            ScheduleRepository
            .list_barber(
                db,
                barber_id
            )
        )


        barber_schedule_map = {

            item.day_of_week:
                item

            for item
            in barber_schedules

        }


        # -------------------------------------------------
        # DESCANSOS ACTIVOS DE LA BARBERÍA
        # -------------------------------------------------

        break_items = (
            ScheduleRepository
            .list_active_barbershop_breaks(
                db,
                barber.barbershop_id
            )
        )


        breaks_by_day: dict[
            int,
            list[BarbershopBreak]
        ] = {}


        for break_item in break_items:

            breaks_by_day.setdefault(
                break_item.day_of_week,
                []
            ).append(
                break_item
            )


        # -------------------------------------------------
        # BLOQUEOS DEL BARBERO EN LA SEMANA
        # -------------------------------------------------

        block_items = (
            ScheduleRepository
            .list_blocks_in_range(
                db=db,
                barber_id=barber_id,
                start_at=range_start,
                end_at=range_end
            )
        )


        # -------------------------------------------------
        # CONSTRUIR LOS 7 DÍAS
        # -------------------------------------------------

        days: list[
            BarberAgendaDayResponse
        ] = []


        for index in range(
            7
        ):

            current_date = (
                monday
                +
                timedelta(
                    days=index
                )
            )


            day_of_week = (
                current_date.weekday()
                +
                1
            )


            # ---------------------------------------------
            # HORARIO BARBERÍA DEL DÍA
            # ---------------------------------------------

            shop_schedule = (
                barbershop_schedule_map
                .get(
                    day_of_week
                )
            )


            # ---------------------------------------------
            # HORARIO BARBERO DEL DÍA
            # ---------------------------------------------

            barber_schedule = (
                barber_schedule_map
                .get(
                    day_of_week
                )
            )


            # ---------------------------------------------
            # BARBERÍA ABIERTA
            # ---------------------------------------------

            is_barbershop_open = bool(
                shop_schedule
                and
                shop_schedule.is_open
            )


            # ---------------------------------------------
            # BARBERO TRABAJA
            # ---------------------------------------------

            is_working = bool(
                barber_schedule
                and
                barber_schedule.is_working
                and
                is_barbershop_open
            )


            # ---------------------------------------------
            # DESCANSOS DEL DÍA
            # ---------------------------------------------

            day_breaks = [

                AgendaBreakResponse(
                    id=item.id,
                    name=item.name,
                    start_time=item.start_time,
                    end_time=item.end_time
                )

                for item
                in breaks_by_day.get(
                    day_of_week,
                    []
                )

            ]


            # ---------------------------------------------
            # RANGO DATETIME DEL DÍA
            # ---------------------------------------------

            day_start = (
                datetime.combine(
                    current_date,
                    time.min
                )
            )


            day_end = (
                datetime.combine(
                    current_date
                    +
                    timedelta(
                        days=1
                    ),
                    time.min
                )
            )


            # ---------------------------------------------
            # BLOQUEOS DEL DÍA
            # ---------------------------------------------

            day_blocks: list[
                AgendaBlockResponse
            ] = []


            for block in block_items:

                overlaps_day = (
                    block.start_at
                    <
                    day_end
                    and
                    block.end_at
                    >
                    day_start
                )


                if not overlaps_day:

                    continue


                day_blocks.append(
                    AgendaBlockResponse(
                        id=block.id,
                        start_at=block.start_at,
                        end_at=block.end_at,
                        reason=block.reason
                    )
                )


            # ---------------------------------------------
            # AGREGAR DÍA A LA RESPUESTA
            # ---------------------------------------------

            days.append(
                BarberAgendaDayResponse(

                    date=
                        current_date
                        .isoformat(),

                    day_of_week=
                        day_of_week,

                    # -------------------------------------
                    # BARBERÍA
                    # -------------------------------------

                    is_barbershop_open=
                        is_barbershop_open,

                    barbershop_open_time=
                        (
                            shop_schedule.open_time
                            if shop_schedule
                            else None
                        ),

                    barbershop_close_time=
                        (
                            shop_schedule.close_time
                            if shop_schedule
                            else None
                        ),

                    # -------------------------------------
                    # BARBERO
                    # -------------------------------------

                    is_working=
                        is_working,

                    start_time=
                        (
                            barber_schedule.start_time
                            if barber_schedule
                            else None
                        ),

                    end_time=
                        (
                            barber_schedule.end_time
                            if barber_schedule
                            else None
                        ),

                    # -------------------------------------
                    # DESCANSOS
                    # -------------------------------------

                    breaks=
                        day_breaks,

                    # -------------------------------------
                    # BLOQUEOS
                    # -------------------------------------

                    blocks=
                        day_blocks
                )
            )


        # -------------------------------------------------
        # RESPUESTA FINAL
        # -------------------------------------------------

        return BarberWeeklyAgendaResponse(

            barber_id=
                barber.id,

            barbershop_id=
                barber.barbershop_id,

            week_start=
                monday.isoformat(),

            week_end=
                sunday.isoformat(),

            days=
                days
        )


    # =====================================================
    # BLOQUEOS
    # =====================================================

    @staticmethod
    def create_block(
        db: Session,
        barber_id: int,
        data: BarberBlockCreate,
        current_user: User
    ):

        ScheduleService._validate_barber_management(
            db,
            barber_id,
            current_user
        )


        overlapping = (
            ScheduleRepository
            .has_overlapping_block(
                db,
                barber_id,
                data.start_at,
                data.end_at
            )
        )


        if overlapping:

            raise InvalidScheduleError(
                "Ya existe un bloqueo que se cruza "
                "con este intervalo."
            )


        try:

            block = BarberBlock(
                barber_id=barber_id,
                start_at=data.start_at,
                end_at=data.end_at,
                reason=data.reason
            )


            ScheduleRepository.create_block(
                db,
                block
            )


            db.commit()

            db.refresh(
                block
            )


            return block


        except SQLAlchemyError:

            db.rollback()

            raise


    # =====================================================
    # LISTAR BLOQUEOS
    # =====================================================

    @staticmethod
    def list_blocks(
        db: Session,
        barber_id: int
    ):

        barber = (
            BarberRepository
            .get_by_id(
                db,
                barber_id
            )
        )


        if not barber:

            raise BarberNotFoundError()


        return (
            ScheduleRepository
            .list_blocks(
                db,
                barber_id
            )
        )


    # =====================================================
    # ELIMINAR BLOQUEO
    # =====================================================

    @staticmethod
    def delete_block(
        db: Session,
        block_id: int,
        current_user: User
    ):

        block = (
            ScheduleRepository
            .get_block_by_id(
                db,
                block_id
            )
        )


        if not block:

            raise BarberBlockNotFoundError()


        ScheduleService._validate_barber_management(
            db,
            block.barber_id,
            current_user
        )


        try:

            ScheduleRepository.delete_block(
                db,
                block
            )


            db.commit()


        except SQLAlchemyError:

            db.rollback()

            raise