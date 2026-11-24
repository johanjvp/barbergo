from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    DefaultRoleNotFoundError,
    InvalidCredentialsError,
    InactiveUserError
)

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.repositories.user_repository import (
    UserRepository
)

from app.schemas.user_schema import UserRegister
from app.schemas.auth_schema import LoginRequest


class AuthService:

    # =====================================================
    # REGISTRO
    # =====================================================

    @staticmethod
    def register_client(
        db: Session,
        data: UserRegister
    ):

        email = data.email.lower()

        existing_user = UserRepository.get_by_email(
            db,
            email
        )

        if existing_user:
            raise EmailAlreadyRegisteredError()

        client_role = UserRepository.get_role_by_name(
            db,
            "CLIENT"
        )

        if not client_role:
            raise DefaultRoleNotFoundError()

        try:

            hashed_password = hash_password(
                data.password
            )

            user = UserRepository.create(
                db,
                first_name=data.first_name,
                last_name=data.last_name,
                email=email,
                password_hash=hashed_password,
                phone=data.phone
            )

            user.roles.append(client_role)

            db.commit()

            db.refresh(user)

            return user

        except SQLAlchemyError:

            db.rollback()

            raise


    # =====================================================
    # LOGIN
    # =====================================================

    @staticmethod
    def login(
        db: Session,
        data: LoginRequest
    ):

        email = data.email.lower()

        user = UserRepository.get_by_email(
            db,
            email
        )

        # No decimos si falló el correo
        # o la contraseña.
        if not user:
            raise InvalidCredentialsError()

        if not verify_password(
            data.password,
            user.password_hash
        ):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        access_token = create_access_token(
            user.id
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in":
                settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }