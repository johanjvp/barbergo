from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.barbershop_admin_model import (
    BarbershopAdmin
)

from app.models.user_model import User

from app.repositories.barbershop_admin_repository import (
    BarbershopAdminRepository
)

from app.repositories.barbershop_repository import (
    BarbershopRepository
)

from app.repositories.user_repository import (
    UserRepository
)


class BarbershopAdminService:

    # =====================================================
    # ASIGNAR ADMINISTRADOR
    # =====================================================

    @staticmethod
    def assign_admin(
        db: Session,
        barbershop_id: int,
        user_id: int,
        current_user: User
    ):

        # =================================================
        # VALIDAR BARBERÍA
        # =================================================

        barbershop = (
            BarbershopRepository.get_by_id(
                db=db,
                barbershop_id=barbershop_id
            )
        )

        if not barbershop:

            raise ValueError(
                "BARBERSHOP_NOT_FOUND"
            )


        # =================================================
        # VALIDAR PERMISOS DEL USUARIO ACTUAL
        # =================================================

        current_roles = {
            role.name.strip().upper()
            for role in current_user.roles
            if role.name
        }

        is_platform_admin = (
            "PLATFORM_ADMIN"
            in current_roles
        )

        is_owner = (
            barbershop.owner_user_id
            == current_user.id
        )

        if not (
            is_platform_admin
            or is_owner
        ):

            raise PermissionError(
                "FORBIDDEN"
            )


        # =================================================
        # OBTENER USUARIO A ASIGNAR
        # =================================================

        target_user = (
            UserRepository.get_by_id(
                db=db,
                user_id=user_id
            )
        )

        if not target_user:

            raise ValueError(
                "USER_NOT_FOUND"
            )


        # =================================================
        # VALIDAR USUARIO ACTIVO
        # =================================================

        if not target_user.is_active:

            raise ValueError(
                "USER_INACTIVE"
            )


        # =================================================
        # EVITAR ASIGNAR AL PROPIETARIO
        # =================================================
        #
        # El propietario ya tiene permisos sobre
        # su barbería mediante owner_user_id.
        # =================================================

        if (
            barbershop.owner_user_id
            == target_user.id
        ):

            raise ValueError(
                "USER_IS_OWNER"
            )


        # =================================================
        # OBTENER ROL BARBERSHOP_ADMIN
        # =================================================

        admin_role = (
            UserRepository.get_role_by_name(
                db=db,
                role_name="BARBERSHOP_ADMIN"
            )
        )

        if not admin_role:

            raise ValueError(
                "BARBERSHOP_ADMIN_ROLE_NOT_FOUND"
            )


        # =================================================
        # BUSCAR ASIGNACIÓN EXISTENTE
        # =================================================

        existing_assignment = (
            BarbershopAdminRepository
            .get_assignment(
                db=db,
                user_id=user_id,
                barbershop_id=barbershop_id
            )
        )


        # =================================================
        # ASIGNAR ROL + BARBERÍA
        # =================================================

        try:

            # ---------------------------------------------
            # ASIGNAR ROL SI TODAVÍA NO LO TIENE
            # ---------------------------------------------

            UserRepository.add_role(
                db=db,
                user=target_user,
                role=admin_role
            )


            # ---------------------------------------------
            # REACTIVAR ASIGNACIÓN EXISTENTE
            # ---------------------------------------------

            if existing_assignment:

                if not existing_assignment.is_active:

                    (
                        BarbershopAdminRepository
                        .activate(
                            db=db,
                            assignment=
                                existing_assignment
                        )
                    )

                db.commit()

                db.refresh(
                    existing_assignment
                )

                return existing_assignment


            # ---------------------------------------------
            # CREAR NUEVA ASIGNACIÓN
            # ---------------------------------------------

            assignment = BarbershopAdmin(
                user_id=user_id,
                barbershop_id=barbershop_id,
                is_active=True
            )

            BarbershopAdminRepository.create(
                db=db,
                assignment=assignment
            )

            db.commit()

            db.refresh(
                assignment
            )

            return assignment

        except SQLAlchemyError:

            db.rollback()

            raise


    # =====================================================
    # LISTAR ADMINISTRADORES
    # =====================================================

    @staticmethod
    def list_admins(
        db: Session,
        barbershop_id: int,
        current_user: User
    ):

        barbershop = (
            BarbershopRepository.get_by_id(
                db=db,
                barbershop_id=barbershop_id
            )
        )

        if not barbershop:

            raise ValueError(
                "BARBERSHOP_NOT_FOUND"
            )


        # =================================================
        # VALIDAR PERMISOS
        # =================================================

        current_roles = {
            role.name.strip().upper()
            for role in current_user.roles
            if role.name
        }

        is_platform_admin = (
            "PLATFORM_ADMIN"
            in current_roles
        )

        is_owner = (
            barbershop.owner_user_id
            == current_user.id
        )

        if not (
            is_platform_admin
            or is_owner
        ):

            raise PermissionError(
                "FORBIDDEN"
            )


        # =================================================
        # LISTAR ADMINISTRADORES ACTIVOS
        # =================================================

        return (
            BarbershopAdminRepository
            .list_by_barbershop(
                db=db,
                barbershop_id=barbershop_id
            )
        )


    # =====================================================
    # DESASIGNAR ADMINISTRADOR
    # =====================================================

    @staticmethod
    def remove_admin(
        db: Session,
        barbershop_id: int,
        user_id: int,
        current_user: User
    ):

        # =================================================
        # VALIDAR BARBERÍA
        # =================================================

        barbershop = (
            BarbershopRepository.get_by_id(
                db=db,
                barbershop_id=barbershop_id
            )
        )

        if not barbershop:

            raise ValueError(
                "BARBERSHOP_NOT_FOUND"
            )


        # =================================================
        # VALIDAR PERMISOS
        # =================================================

        current_roles = {
            role.name.strip().upper()
            for role in current_user.roles
            if role.name
        }

        is_platform_admin = (
            "PLATFORM_ADMIN"
            in current_roles
        )

        is_owner = (
            barbershop.owner_user_id
            == current_user.id
        )

        if not (
            is_platform_admin
            or is_owner
        ):

            raise PermissionError(
                "FORBIDDEN"
            )


        # =================================================
        # OBTENER ASIGNACIÓN
        # =================================================

        assignment = (
            BarbershopAdminRepository
            .get_assignment(
                db=db,
                user_id=user_id,
                barbershop_id=barbershop_id
            )
        )

        if not assignment:

            raise ValueError(
                "ADMIN_NOT_FOUND"
            )

        if not assignment.is_active:

            raise ValueError(
                "ADMIN_ALREADY_INACTIVE"
            )


        # =================================================
        # DESACTIVAR ASIGNACIÓN
        # =================================================

        try:

            (
                BarbershopAdminRepository
                .deactivate(
                    db=db,
                    assignment=assignment
                )
            )

            db.commit()

            db.refresh(
                assignment
            )

            return assignment

        except SQLAlchemyError:

            db.rollback()

            raise