from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from app.controllers.auth_controller import AuthController
from app.db.session import get_db

from app.dependencies.auth_dependencies import (
    get_current_user
)

from app.models.user_model import User

from app.schemas.user_schema import (
    UserRegister,
    UserResponse,
    UserMeResponse
)

from app.schemas.auth_schema import (
    LoginRequest,
    TokenResponse
)


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)


# =========================================================
# REGISTRO
# =========================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: UserRegister,
    db: Session = Depends(get_db)
):

    return AuthController.register(
        db,
        data
    )


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    return AuthController.login(
        db,
        data
    )


# =========================================================
# USUARIO AUTENTICADO
# =========================================================

@router.get(
    "/me",
    response_model=UserMeResponse
)
def get_me(
    current_user: User = Depends(
        get_current_user
    )
):

    return current_user