from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.user_model import User

from app.services.barbershop_admin_service import (
    BarbershopAdminService
)


class BarbershopAdminController:

    # =====================================================
    # ASIGNAR ADMINISTRADOR
    # =====================================================

    @staticmethod
    def assign(
        db: Session,
        barbershop_id: int,
        user_id: int,
        current_user: User
    ):

        try:

            return (
                BarbershopAdminService
                .assign_admin(
                    db=db,
                    barbershop_id=
                        barbershop_id,
                    user_id=
                        user_id,
                    current_user=
                        current_user
                )
            )

        except ValueError as error:

            error_code = str(error)

            if (
                error_code
                == "BARBERSHOP_NOT_FOUND"
            ):

                raise HTTPException(
                    status_code=
                        status.HTTP_404_NOT_FOUND,
                    detail=
                        "La barbería no existe."
                )

            if (
                error_code
                == "USER_NOT_FOUND"
            ):

                raise HTTPException(
                    status_code=
                        status.HTTP_404_NOT_FOUND,
                    detail=(
                        "El usuario que intentas "
                        "asignar no existe."
                    )
                )

            if (
                error_code
                == "USER_INACTIVE"
            ):

                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "No se puede asignar como "
                        "administrador a un usuario "
                        "inactivo."
                    )
                )

            if (
                error_code
                ==
                "USER_NOT_BARBERSHOP_ADMIN"
            ):

                raise HTTPException(
                    status_code=
                        status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "El usuario debe tener el rol "
                        "BARBERSHOP_ADMIN antes de ser "
                        "asignado a una barbería."
                    )
                )

            if (
                error_code
                == "USER_IS_OWNER"
            ):

                raise HTTPException(
                    status_code=
                        status.HTTP_409_CONFLICT,
                    detail=(
                        "Este usuario ya es propietario "
                        "de la barbería y ya posee "
                        "permisos administrativos."
                    )
                )

            raise


        except PermissionError:

            raise HTTPException(
                status_code=
                    status.HTTP_403_FORBIDDEN,
                detail=(
                    "No tienes permisos para "
                    "asignar administradores "
                    "a esta barbería."
                )
            )


        except SQLAlchemyError:

            raise HTTPException(
                status_code=
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "No fue posible asignar "
                    "el administrador."
                )
            )


    # =====================================================
    # LISTAR ADMINISTRADORES
    # =====================================================

    @staticmethod
    def list_admins(
        db: Session,
        barbershop_id: int,
        current_user: User
    ):

        try:

            return (
                BarbershopAdminService
                .list_admins(
                    db=db,
                    barbershop_id=
                        barbershop_id,
                    current_user=
                        current_user
                )
            )

        except ValueError as error:

            if (
                str(error)
                == "BARBERSHOP_NOT_FOUND"
            ):

                raise HTTPException(
                    status_code=
                        status.HTTP_404_NOT_FOUND,
                    detail=
                        "La barbería no existe."
                )

            raise


        except PermissionError:

            raise HTTPException(
                status_code=
                    status.HTTP_403_FORBIDDEN,
                detail=(
                    "No tienes permisos para "
                    "consultar administradores "
                    "de esta barbería."
                )
            )


    # =====================================================
    # DESASIGNAR ADMINISTRADOR
    # =====================================================

    @staticmethod
    def remove(
        db: Session,
        barbershop_id: int,
        user_id: int,
        current_user: User
    ):

        try:

            (
                BarbershopAdminService
                .remove_admin(
                    db=db,
                    barbershop_id=
                        barbershop_id,
                    user_id=
                        user_id,
                    current_user=
                        current_user
                )
            )

            return {
                "message": (
                    "Administrador desasignado "
                    "correctamente."
                )
            }

        except ValueError as error:

            error_code = str(error)

            if (
                error_code
                == "BARBERSHOP_NOT_FOUND"
            ):

                raise HTTPException(
                    status_code=
                        status.HTTP_404_NOT_FOUND,
                    detail=
                        "La barbería no existe."
                )

            if (
                error_code
                == "ADMIN_NOT_FOUND"
            ):

                raise HTTPException(
                    status_code=
                        status.HTTP_404_NOT_FOUND,
                    detail=(
                        "El usuario no está asignado "
                        "como administrador de esta "
                        "barbería."
                    )
                )

            if (
                error_code
                == "ADMIN_ALREADY_INACTIVE"
            ):

                raise HTTPException(
                    status_code=
                        status.HTTP_409_CONFLICT,
                    detail=(
                        "Este administrador ya se "
                        "encuentra desactivado para "
                        "esta barbería."
                    )
                )

            raise


        except PermissionError:

            raise HTTPException(
                status_code=
                    status.HTTP_403_FORBIDDEN,
                detail=(
                    "No tienes permisos para "
                    "desasignar administradores "
                    "de esta barbería."
                )
            )


        except SQLAlchemyError:

            raise HTTPException(
                status_code=
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "No fue posible desasignar "
                    "el administrador."
                )
            )