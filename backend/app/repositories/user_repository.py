from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.models.role_model import Role


class UserRepository:

    # =====================================================
    # OBTENER USUARIO POR EMAIL
    # =====================================================

    @staticmethod
    def get_by_email(
        db: Session,
        email: str
    ) -> User | None:

        statement = select(
            User
        ).where(
            func.lower(User.email) == email.strip().lower()
        )

        return db.scalar(
            statement
        )


    # =====================================================
    # OBTENER USUARIO POR ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int
    ) -> User | None:

        statement = select(
            User
        ).where(
            User.id == user_id
        )

        return db.scalar(
            statement
        )


    # =====================================================
    # OBTENER ROL POR NOMBRE
    # =====================================================

    @staticmethod
    def get_role_by_name(
        db: Session,
        role_name: str
    ) -> Role | None:

        normalized_role = (
            role_name
            .strip()
            .upper()
        )

        statement = select(
            Role
        ).where(
            Role.name == normalized_role
        )

        return db.scalar(
            statement
        )


    # =====================================================
    # CREAR USUARIO
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        *,
        first_name: str,
        last_name: str,
        email: str,
        password_hash: str,
        phone: str | None
    ) -> User:

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            phone=phone
        )

        db.add(
            user
        )

        db.flush()

        return user


    # =====================================================
    # VALIDAR SI USUARIO TIENE ROL
    # =====================================================

    @staticmethod
    def has_role(
        user: User,
        role_name: str
    ) -> bool:

        normalized_role = (
            role_name
            .strip()
            .upper()
        )

        return any(
            role.name
            and
            role.name.strip().upper()
            == normalized_role

            for role in user.roles
        )


    # =====================================================
    # ASIGNAR ROL
    # =====================================================

    @staticmethod
    def add_role(
        db: Session,
        user: User,
        role: Role
    ) -> User:

        already_has_role = any(
            existing_role.id
            == role.id

            for existing_role
            in user.roles
        )

        if not already_has_role:

            user.roles.append(
                role
            )

            db.flush()

        return user


    # =====================================================
    # QUITAR ROL
    # =====================================================

    @staticmethod
    def remove_role(
        db: Session,
        user: User,
        role: Role
    ) -> User:

        role_to_remove = next(
            (
                existing_role

                for existing_role
                in user.roles

                if existing_role.id
                == role.id
            ),
            None
        )

        if role_to_remove:

            user.roles.remove(
                role_to_remove
            )

            db.flush()

        return user