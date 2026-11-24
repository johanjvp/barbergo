from fastapi import HTTPException

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BarbershopForbiddenError,
    BarbershopNotFoundError,
    BarberLimitReachedError,
    BarberNotFoundError,
    InvalidBarberServiceError,
    UserAlreadyBarberError,
    UserNotFoundError
)

from app.models.user_model import User

from app.schemas.barber_schema import (
    BarberCreate,
    BarberUpdate
)

from app.services.barber_service import (
    BarberService
)


class BarberController:

    @staticmethod
    def create(
        db: Session,
        barbershop_id: int,
        data: BarberCreate,
        current_user: User
    ):

        try:

            return BarberService.create(
                db,
                barbershop_id,
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

        except UserNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado."
            )

        except UserAlreadyBarberError:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Este usuario ya está "
                    "registrado como barbero."
                )
            )

        except BarberLimitReachedError:
            raise HTTPException(
                status_code=409,
                detail=(
                    "La barbería ya alcanzó "
                    "el máximo de 5 barberos activos."
                )
            )

        except InvalidBarberServiceError:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Uno o más servicios no "
                    "pertenecen a esta barbería."
                )
            )

        except SQLAlchemyError as error:

            print(
                "ERROR SQL BARBER:",
                repr(error)
            )

            raise HTTPException(
                status_code=500,
                detail="No fue posible crear el barbero."
            )


    @staticmethod
    def list_by_barbershop(
        db: Session,
        barbershop_id: int
    ):

        try:

            return BarberService.list_by_barbershop(
                db,
                barbershop_id
            )

        except BarbershopNotFoundError:

            raise HTTPException(
                status_code=404,
                detail="Barbería no encontrada."
            )


    @staticmethod
    def get_by_id(
        db: Session,
        barber_id: int
    ):

        try:

            return BarberService.get_by_id(
                db,
                barber_id
            )

        except BarberNotFoundError:

            raise HTTPException(
                status_code=404,
                detail="Barbero no encontrado."
            )


    @staticmethod
    def update(
        db: Session,
        barber_id: int,
        data: BarberUpdate,
        current_user: User
    ):

        try:

            return BarberService.update(
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

        except BarbershopForbiddenError:

            raise HTTPException(
                status_code=403,
                detail=(
                    "No tienes permisos para "
                    "administrar este barbero."
                )
            )

        except BarberLimitReachedError:

            raise HTTPException(
                status_code=409,
                detail=(
                    "La barbería ya alcanzó "
                    "el máximo de 5 barberos activos."
                )
            )

        except InvalidBarberServiceError:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Uno o más servicios no "
                    "pertenecen a esta barbería."
                )
            )

        except SQLAlchemyError as error:

            print(
                "ERROR SQL BARBER:",
                repr(error)
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "No fue posible actualizar "
                    "el barbero."
                )
            )