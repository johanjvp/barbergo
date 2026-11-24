from fastapi import HTTPException, status

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BarbershopNotFoundError,
    BarbershopForbiddenError
)

from app.models.user_model import User

from app.schemas.barbershop_schema import (
    BarbershopCreate,
    BarbershopUpdate
)

from app.services.barbershop_service import (
    BarbershopService
)


class BarbershopController:

    @staticmethod
    def create(
        db: Session,
        data: BarbershopCreate,
        current_user: User
    ):

        try:

            return BarbershopService.create(
                db,
                data,
                current_user
            )

        except SQLAlchemyError as error:

            print(
                "ERROR SQL BARBERSHOP:",
                repr(error)
            )

            raise HTTPException(
                status_code=500,
                detail="No fue posible crear la barbería."
            )


    @staticmethod
    def list_active(
        db: Session,
        skip: int,
        limit: int
    ):

        return BarbershopService.list_active(
            db,
            skip,
            limit
        )


    @staticmethod
    def get_by_id(
        db: Session,
        barbershop_id: int
    ):

        try:

            return BarbershopService.get_by_id(
                db,
                barbershop_id
            )

        except BarbershopNotFoundError:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barbería no encontrada."
            )


    @staticmethod
    def update(
        db: Session,
        barbershop_id: int,
        data: BarbershopUpdate,
        current_user: User
    ):

        try:

            return BarbershopService.update(
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
                    "modificar esta barbería."
                )
            )

        except SQLAlchemyError as error:

            print(
                "ERROR SQL BARBERSHOP:",
                repr(error)
            )

            raise HTTPException(
                status_code=500,
                detail="No fue posible actualizar la barbería."
            )