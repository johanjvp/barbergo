from fastapi import Depends, HTTPException, status

from app.dependencies.auth_dependencies import get_current_user
from app.models.user_model import User


def require_roles(*allowed_roles: str):

    def dependency(
        current_user: User = Depends(get_current_user)
    ) -> User:

        user_roles = {
            role.name
            for role in current_user.roles
        }

        if not user_roles.intersection(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción."
            )

        return current_user

    return dependency