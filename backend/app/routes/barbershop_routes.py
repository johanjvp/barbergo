from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.controllers.barbershop_controller import (
    BarbershopController
)

from app.db.session import get_db

from app.dependencies.role_dependencies import (
    require_roles
)

from app.models.user_model import User

from app.schemas.barbershop_schema import (
    BarbershopCreate,
    BarbershopUpdate,
    BarbershopResponse
)


router = APIRouter(
    prefix="/barbershops",
    tags=["Barberías"]
)


# =========================================================
# CREAR BARBERÍA
# =========================================================

@router.post(
    "",
    response_model=BarbershopResponse,
    status_code=status.HTTP_201_CREATED
)
def create_barbershop(
    data: BarbershopCreate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return BarbershopController.create(
        db,
        data,
        current_user
    )


# =========================================================
# LISTAR
# =========================================================

@router.get(
    "",
    response_model=list[BarbershopResponse]
)
def list_barbershops(
    skip: int = Query(
        default=0,
        ge=0
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db)
):

    return BarbershopController.list_active(
        db,
        skip,
        limit
    )


# =========================================================
# OBTENER POR ID
# =========================================================

@router.get(
    "/{barbershop_id}",
    response_model=BarbershopResponse
)
def get_barbershop(
    barbershop_id: int,
    db: Session = Depends(get_db)
):

    return BarbershopController.get_by_id(
        db,
        barbershop_id
    )


# =========================================================
# ACTUALIZAR
# =========================================================

@router.patch(
    "/{barbershop_id}",
    response_model=BarbershopResponse
)
def update_barbershop(
    barbershop_id: int,

    data: BarbershopUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return BarbershopController.update(
        db,
        barbershop_id,
        data,
        current_user
    )