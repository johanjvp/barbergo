from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from app.controllers.barbershop_admin_controller import (
    BarbershopAdminController
)

from app.db.session import (
    get_db
)

from app.dependencies.auth_dependencies import (
    get_current_user
)

from app.models.user_model import User

from app.schemas.barbershop_admin_schema import (
    BarbershopAdminAssign,
    BarbershopAdminAssignmentResponse,
    BarbershopAdminResponse,
    BarbershopAdminActionResponse
)


router = APIRouter(
    prefix="/barbershops",
    tags=[
        "Barbershop Admins"
    ]
)


# =====================================================
# ASIGNAR ADMINISTRADOR
# =====================================================

@router.post(
    "/{barbershop_id}/admins",
    response_model=
        BarbershopAdminAssignmentResponse,
    status_code=
        status.HTTP_201_CREATED
)
def assign_barbershop_admin(
    barbershop_id: int,

    payload:
        BarbershopAdminAssign,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
):

    return (
        BarbershopAdminController
        .assign(
            db=db,
            barbershop_id=
                barbershop_id,
            user_id=
                payload.user_id,
            current_user=
                current_user
        )
    )


# =====================================================
# LISTAR ADMINISTRADORES
# =====================================================

@router.get(
    "/{barbershop_id}/admins",
    response_model=
        list[
            BarbershopAdminResponse
        ]
)
def list_barbershop_admins(
    barbershop_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
):

    return (
        BarbershopAdminController
        .list_admins(
            db=db,
            barbershop_id=
                barbershop_id,
            current_user=
                current_user
        )
    )


# =====================================================
# DESASIGNAR ADMINISTRADOR
# =====================================================

@router.delete(
    "/{barbershop_id}/admins/{user_id}",
    response_model=
        BarbershopAdminActionResponse
)
def remove_barbershop_admin(
    barbershop_id: int,
    user_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
):

    return (
        BarbershopAdminController
        .remove(
            db=db,
            barbershop_id=
                barbershop_id,
            user_id=
                user_id,
            current_user=
                current_user
        )
    )