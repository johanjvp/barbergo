from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BarbershopNotFoundError,
    BarbershopForbiddenError,
    ServiceNotFoundError
)

from app.models.service_model import Service
from app.models.user_model import User

from app.repositories.barbershop_repository import (
    BarbershopRepository
)

from app.repositories.service_repository import (
    ServiceRepository
)

from app.schemas.service_schema import (
    ServiceCreate,
    ServiceUpdate
)


class ServiceService:

    # =====================================================
    # VERIFICAR PERMISOS SOBRE BARBERÍA
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

        user_roles = {
            role.name
            for role in current_user.roles
        }

        is_platform_admin = (
            "PLATFORM_ADMIN" in user_roles
        )

        is_owner = (
            barbershop.owner_user_id
            == current_user.id
        )

        if not is_platform_admin and not is_owner:
            raise BarbershopForbiddenError()

        return barbershop


    # =====================================================
    # CREAR
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        barbershop_id: int,
        data: ServiceCreate,
        current_user: User
    ) -> Service:

        ServiceService._validate_barbershop_management(
            db,
            barbershop_id,
            current_user
        )

        try:

            service = Service(
                barbershop_id=barbershop_id,
                **data.model_dump()
            )

            ServiceRepository.create(
                db,
                service
            )

            db.commit()

            db.refresh(service)

            return service

        except SQLAlchemyError:

            db.rollback()

            raise


    # =====================================================
    # LISTAR POR BARBERÍA
    # =====================================================

    @staticmethod
    def list_by_barbershop(
        db: Session,
        barbershop_id: int
    ):

        barbershop = BarbershopRepository.get_by_id(
            db,
            barbershop_id
        )

        if not barbershop:
            raise BarbershopNotFoundError()

        return ServiceRepository.list_by_barbershop(
            db,
            barbershop_id
        )


    # =====================================================
    # OBTENER POR ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        service_id: int
    ):

        service = ServiceRepository.get_by_id(
            db,
            service_id
        )

        if not service:
            raise ServiceNotFoundError()

        return service


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

        service = ServiceRepository.get_by_id(
            db,
            service_id
        )

        if not service:
            raise ServiceNotFoundError()

        ServiceService._validate_barbershop_management(
            db,
            service.barbershop_id,
            current_user
        )

        values = data.model_dump(
            exclude_unset=True
        )

        try:

            ServiceRepository.update(
                db,
                service,
                values
            )

            db.commit()

            db.refresh(service)

            return service

        except SQLAlchemyError:

            db.rollback()

            raise