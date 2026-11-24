from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BarbershopNotFoundError,
    BarbershopForbiddenError
)

from app.models.barbershop_model import Barbershop
from app.models.user_model import User

from app.repositories.barbershop_repository import (
    BarbershopRepository
)

from app.repositories.barbershop_admin_repository import (
    BarbershopAdminRepository
)

from app.schemas.barbershop_schema import (
    BarbershopCreate,
    BarbershopUpdate
)


class BarbershopService:

    @staticmethod
    def create(
        db: Session,
        data: BarbershopCreate,
        current_user: User
    ) -> Barbershop:

        try:

            barbershop = Barbershop(
                owner_user_id=current_user.id,
                **data.model_dump()
            )

            BarbershopRepository.create(
                db,
                barbershop
            )

            db.commit()
            db.refresh(barbershop)

            return barbershop

        except SQLAlchemyError:

            db.rollback()
            raise


    @staticmethod
    def list_active(
        db: Session,
        skip: int,
        limit: int
    ):

        return BarbershopRepository.list_active(
            db,
            skip,
            limit
        )


    @staticmethod
    def get_by_id(
        db: Session,
        barbershop_id: int
    ):

        barbershop = (
            BarbershopRepository.get_by_id(
                db,
                barbershop_id
            )
        )

        if not barbershop:
            raise BarbershopNotFoundError()

        return barbershop


    @staticmethod
    def update(
        db: Session,
        barbershop_id: int,
        data: BarbershopUpdate,
        current_user: User
    ):

        # =====================================================
        # OBTENER BARBERÍA
        # =====================================================

        barbershop = (
            BarbershopRepository.get_by_id(
                db,
                barbershop_id
            )
        )

        if not barbershop:
            raise BarbershopNotFoundError()


        # =====================================================
        # OBTENER ROLES DEL USUARIO
        # =====================================================

        user_roles = {
            role.name.strip().upper()
            for role in current_user.roles
            if role.name
        }


        # =====================================================
        # PLATFORM ADMIN
        # =====================================================
        #
        # Puede administrar cualquier barbería.
        # =====================================================

        is_platform_admin = (
            "PLATFORM_ADMIN"
            in user_roles
        )


        # =====================================================
        # PROPIETARIO DE LA BARBERÍA
        # =====================================================
        #
        # El propietario siempre puede administrar
        # su propia barbería.
        # =====================================================

        is_owner = (
            barbershop.owner_user_id
            == current_user.id
        )


        # =====================================================
        # BARBERSHOP ADMIN
        # =====================================================

        is_barbershop_admin = (
            "BARBERSHOP_ADMIN"
            in user_roles
        )


        # =====================================================
        # VALIDAR ASIGNACIÓN DEL ADMINISTRADOR
        # =====================================================
        #
        # Tener el rol BARBERSHOP_ADMIN no es suficiente.
        #
        # El usuario también debe estar vinculado
        # específicamente con esta barbería mediante
        # la tabla barbershop_admins.
        # =====================================================

        has_admin_assignment = False

        if is_barbershop_admin:

            has_admin_assignment = (
                BarbershopAdminRepository
                .has_active_access(
                    db=db,
                    user_id=current_user.id,
                    barbershop_id=barbershop_id
                )
            )


        # =====================================================
        # VALIDAR AUTORIZACIÓN
        # =====================================================

        has_access = (
            is_platform_admin
            or is_owner
            or has_admin_assignment
        )

        if not has_access:

            raise BarbershopForbiddenError()


        # =====================================================
        # CAMPOS A ACTUALIZAR
        # =====================================================

        values = data.model_dump(
            exclude_unset=True
        )


        # =====================================================
        # ACTUALIZAR BARBERÍA
        # =====================================================

        try:

            BarbershopRepository.update(
                db,
                barbershop,
                values
            )

            db.commit()

            db.refresh(
                barbershop
            )

            return barbershop

        except SQLAlchemyError:

            db.rollback()

            raise