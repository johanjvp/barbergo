from fastapi import HTTPException, status

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    DefaultRoleNotFoundError,
    InvalidCredentialsError,
    InactiveUserError
)

from app.schemas.user_schema import UserRegister
from app.schemas.auth_schema import LoginRequest

from app.services.auth_service import AuthService


class AuthController:

    # =====================================================
    # REGISTRO
    # =====================================================

    @staticmethod
    def register(
        db: Session,
        data: UserRegister
    ):

        try:

            return AuthService.register_client(
                db,
                data
            )

        except EmailAlreadyRegisteredError:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo ya está registrado."
            )

        except DefaultRoleNotFoundError:

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se encuentra configurado el rol CLIENT."
            )

        except SQLAlchemyError as error:

            print("ERROR SQL:", repr(error))

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No fue posible crear el usuario."
            )


    # =====================================================
    # LOGIN
    # =====================================================

    @staticmethod
    def login(
        db: Session,
        data: LoginRequest
    ):

        try:

            return AuthService.login(
                db,
                data
            )

        except InvalidCredentialsError:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos."
            )

        except InactiveUserError:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario se encuentra inactivo."
            )