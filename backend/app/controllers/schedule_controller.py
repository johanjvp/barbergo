from datetime import date

from fastapi import HTTPException

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BarbershopForbiddenError,
    BarbershopNotFoundError,
    BarberNotFoundError,
    BarberBlockNotFoundError,
    BarberScheduleForbiddenError,
    InvalidScheduleError
)

from app.models.user_model import User

from app.schemas.schedule_schema import (
    BarbershopScheduleUpsert,
    BarberScheduleUpsert,
    BarberBlockCreate
)

from app.services.schedule_service import ScheduleService


class ScheduleController:

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

        try:

            return ScheduleService.set_barbershop_schedule(
                db,
                barbershop_id,
                day_of_week,
                data,
                current_user
            )

        except BarbershopNotFoundError:

            raise HTTPException(
                status_code=404,
                detail="Barbería no encontrada."
            )

        except BarbershopForbiddenError:

            raise HTTPException(
                status_code=403,
                detail=(
                    "No tienes permisos para "
                    "administrar esta barbería."
                )
            )

        except SQLAlchemyError as error:

            print(
                "ERROR SQL SCHEDULE:",
                repr(error)
            )

            raise HTTPException(
                status_code=500,
                detail="No fue posible guardar el horario."
            )


    # =====================================================
    # LISTAR HORARIO BARBERÍA
    # =====================================================

    @staticmethod
    def list_barbershop_schedule(
        db: Session,
        barbershop_id: int
    ):

        try:

            return ScheduleService.list_barbershop_schedule(
                db,
                barbershop_id
            )

        except BarbershopNotFoundError:

            raise HTTPException(
                status_code=404,
                detail="Barbería no encontrada."
            )

        except SQLAlchemyError as error:

            print(
                "ERROR SQL BARBERSHOP SCHEDULE LIST:",
                repr(error)
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "No fue posible consultar "
                    "el horario de la barbería."
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

        try:

            return ScheduleService.set_barber_schedule(
                db,
                barber_id,
                day_of_week,
                data,
                current_user
            )

        except BarberNotFoundError:

            raise HTTPException(
                status_code=404,
                detail="Barbero no encontrado."
            )

        except BarberScheduleForbiddenError:

            raise HTTPException(
                status_code=403,
                detail=(
                    "No tienes permisos para "
                    "administrar este horario."
                )
            )

        except InvalidScheduleError as error:

            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

        except SQLAlchemyError as error:

            print(
                "ERROR SQL SCHEDULE:",
                repr(error)
            )

            raise HTTPException(
                status_code=500,
                detail="No fue posible guardar el horario."
            )


    # =====================================================
    # LISTAR HORARIO BARBERO
    # =====================================================

    @staticmethod
    def list_barber_schedule(
        db: Session,
        barber_id: int
    ):

        try:

            return ScheduleService.list_barber_schedule(
                db,
                barber_id
            )

        except BarberNotFoundError:

            raise HTTPException(
                status_code=404,
                detail="Barbero no encontrado."
            )

        except SQLAlchemyError as error:

            print(
                "ERROR SQL BARBER SCHEDULE LIST:",
                repr(error)
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "No fue posible consultar "
                    "el horario del barbero."
                )
            )


    # =====================================================
    # AGENDA SEMANAL BARBERO
    # =====================================================

    @staticmethod
    def get_barber_weekly_agenda(
        db: Session,
        barber_id: int,
        week_start: date
    ):

        try:

            return (
                ScheduleService
                .get_barber_weekly_agenda(
                    db=db,
                    barber_id=barber_id,
                    week_start=week_start
                )
            )

        except BarberNotFoundError:

            raise HTTPException(
                status_code=404,
                detail="Barbero no encontrado."
            )

        except InvalidScheduleError as error:

            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

        except SQLAlchemyError as error:

            print(
                "ERROR SQL WEEKLY AGENDA:",
                repr(error)
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "No fue posible consultar "
                    "la agenda semanal del barbero."
                )
            )


    # =====================================================
    # CREAR BLOQUEO
    # =====================================================

    @staticmethod
    def create_block(
        db: Session,
        barber_id: int,
        data: BarberBlockCreate,
        current_user: User
    ):

        try:

            return ScheduleService.create_block(
                db,
                barber_id,
                data,
                current_user
            )

        except BarberNotFoundError:

            raise HTTPException(
                status_code=404,
                detail="Barbero no encontrado."
            )

        except BarberScheduleForbiddenError:

            raise HTTPException(
                status_code=403,
                detail=(
                    "No tienes permisos para "
                    "bloquear este horario."
                )
            )

        except InvalidScheduleError as error:

            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

        except SQLAlchemyError as error:

            print(
                "ERROR SQL BLOCK:",
                repr(error)
            )

            raise HTTPException(
                status_code=500,
                detail="No fue posible crear el bloqueo."
            )


    # =====================================================
    # LISTAR BLOQUEOS
    # =====================================================

    @staticmethod
    def list_blocks(
        db: Session,
        barber_id: int
    ):

        try:

            return ScheduleService.list_blocks(
                db,
                barber_id
            )

        except BarberNotFoundError:

            raise HTTPException(
                status_code=404,
                detail="Barbero no encontrado."
            )

        except SQLAlchemyError as error:

            print(
                "ERROR SQL BLOCK LIST:",
                repr(error)
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "No fue posible consultar "
                    "los bloqueos del barbero."
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

        try:

            ScheduleService.delete_block(
                db,
                block_id,
                current_user
            )

        except BarberBlockNotFoundError:

            raise HTTPException(
                status_code=404,
                detail="Bloqueo no encontrado."
            )

        except BarberScheduleForbiddenError:

            raise HTTPException(
                status_code=403,
                detail=(
                    "No tienes permisos para "
                    "eliminar este bloqueo."
                )
            )

        except SQLAlchemyError as error:

            print(
                "ERROR SQL DELETE BLOCK:",
                repr(error)
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "No fue posible eliminar "
                    "el bloqueo."
                )
            )