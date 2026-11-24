from fastapi import (
    Depends,
    HTTPException,
    status
)

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth_dependencies import get_current_user
from app.models.user_model import User


def require_platform_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:

    # =====================================================
    # VERIFICAR ROL DIRECTAMENTE EN BASE DE DATOS
    # =====================================================

    is_admin = (
        db.execute(
            text(
                """
                SELECT 1
                FROM user_roles ur

                INNER JOIN roles r
                    ON r.id = ur.role_id

                WHERE
                    ur.user_id = :user_id
                    AND UPPER(r.name) = 'PLATFORM_ADMIN'

                LIMIT 1
                """
            ),
            {
                "user_id":
                    current_user.id
            }
        )
        .first()
    )


    if not is_admin:

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "No tienes permisos para acceder "
                "al panel administrativo."
        )


    return current_user