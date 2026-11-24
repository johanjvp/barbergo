from fastapi import HTTPException, status

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BarbershopNotFoundError,
    BarbershopForbiddenError,
    ServiceNotFoundError
)

from app.models.user_model import User

from app.schemas.service_schema import (
    ServiceCreate,
    ServiceUpdate
)

from app.services.service_service import (
    ServiceService
)


class ServiceController:

    # =====================================================
    # CREAR
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        barbershop_id: int,
        data: ServiceCreate,
        current_user: User
    ):

        try:

            return ServiceService.create(
                db,
                barbershop_id,
                data,
                current_user
            )

        except BarbershopNotFoundError:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Barbería no encontrada."
            )

        except BarbershopForbiddenError:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "No tienes permisos para "
                    "administrar esta barbería."
                )
            )

        except SQLAlchemyError as error:

            print(
                "ERROR SQL SERVICE:",
                repr(error)
            )

            raise HTTPException(
                status_code=500,
                detail="No fue posible crear el servicio."
            )


    # =====================================================
    # LISTAR
    # =====================================================

    @staticmethod
    def list_by_barbershop(
        db: Session,
        barbershop_id: int
    ):

        try:

            return ServiceService.list_by_barbershop(
                db,
                barbershop_id
            )

        except BarbershopNotFoundError:

            raise HTTPException(
                status_code=404,
                detail="Barbería no encontrada."
            )


    # =====================================================
    # OBTENER POR ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        service_id: int
    ):

        try:

            return ServiceService.get_by_id(
                db,
                service_id
            )

        except ServiceNotFoundError:

            raise HTTPException(
                status_code=404,
                detail="Servicio no encontrado."
            )


    # =====================================================
    # ACTUALIZAR
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        service_id: int,
        data: ServiceUpdate,
        current_user: User
    ):

        try:

            return ServiceService.update(
                db,
                service_id,
                data,
                current_user
            )

        except ServiceNotFoundError:

            raise HTTPException(
                status_code=404,
                detail="Servicio no encontrado."
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
                "ERROR SQL SERVICE:",
                repr(error)
            )

            raise HTTPException(
                status_code=500,
                detail="No fue posible actualizar el servicio."
            )