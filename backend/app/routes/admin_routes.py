from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Body,
    status
)

from sqlalchemy.orm import Session

from app.controllers.admin_controller import (
    AdminController
)

from app.db.session import (
    get_db
)

from app.dependencies.admin_dependencies import (
    require_platform_admin
)

from app.models.user_model import (
    User
)

from app.schemas.admin_barbershop_schema import (
    AdminBarbershopStatusUpdate
)


router = APIRouter(
    prefix="/admin",
    tags=[
        "Admin"
    ]
)


# =========================================================
# DASHBOARD GENERAL
# =========================================================

@router.get(
    "/dashboard"
)
def get_admin_dashboard(

    db: Session = Depends(
        get_db
    ),

    current_admin: User = Depends(
        require_platform_admin
    )

):

    return (
        AdminController
        .dashboard(
            db
        )
    )


# =========================================================
# BARBERÍAS
# =========================================================

@router.get(
    "/barbershops"
)
def get_admin_barbershops(

    search: str | None =
        Query(
            default=None
        ),

    status_filter: str =
        Query(
            default="all"
        ),

    limit: int =
        Query(
            default=50,
            ge=1,
            le=100
        ),

    offset: int =
        Query(
            default=0,
            ge=0
        ),

    db: Session =
        Depends(
            get_db
        ),

    current_admin: User =
        Depends(
            require_platform_admin
        )

):

    return (
        AdminController
        .barbershops(
            db=db,
            search=search,
            status_filter=
                status_filter,
            limit=limit,
            offset=offset
        )
    )
    
    
# =========================================================
# DETALLE ADMINISTRATIVO DE BARBERÍA
# =========================================================

@router.get(
    "/barbershops/{barbershop_id}"
)
def get_admin_barbershop_detail(

    barbershop_id: int,

    db: Session =
        Depends(
            get_db
        ),

    current_admin: User =
        Depends(
            require_platform_admin
        )

):

    result = (
        AdminController
        .barbershop_detail(
            db=db,
            barbershop_id=
                barbershop_id
        )
    )


    if not result:

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "La barbería no existe."
        )


    return result


# =========================================================
# ACTIVAR / DESACTIVAR BARBERÍA
# =========================================================

@router.patch(
    "/barbershops/{barbershop_id}/status"
)
def update_admin_barbershop_status(

    barbershop_id: int,

    data:
        AdminBarbershopStatusUpdate,

    db: Session =
        Depends(
            get_db
        ),

    current_admin: User =
        Depends(
            require_platform_admin
        )

):

    result = (
        AdminController
        .update_barbershop_status(
            db=db,
            barbershop_id=
                barbershop_id,
            is_active=
                data.is_active
        )
    )


    if not result:

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "La barbería no existe."
        )


    return result


# =========================================================
# USUARIOS
# =========================================================

@router.get(
    "/users"
)
def get_admin_users(

    search: str | None =
        Query(
            default=None
        ),

    role_filter: str =
        Query(
            default="all"
        ),

    status_filter: str =
        Query(
            default="all"
        ),

    limit: int =
        Query(
            default=100,
            ge=1,
            le=100
        ),

    offset: int =
        Query(
            default=0,
            ge=0
        ),

    db: Session =
        Depends(
            get_db
        ),

    current_admin: User =
        Depends(
            require_platform_admin
        )

):

    return (
        AdminController
        .users(
            db=db,
            search=search,
            role_filter=
                role_filter,
            status_filter=
                status_filter,
            limit=limit,
            offset=offset
        )
    )


# =========================================================
# ACTIVAR / INHABILITAR USUARIO
# =========================================================

@router.patch(
    "/users/{user_id}/status"
)
def update_user_status(

    user_id: int,

    is_active: bool =
        Body(
            ...,
            embed=True
        ),

    db: Session =
        Depends(
            get_db
        ),

    current_admin: User =
        Depends(
            require_platform_admin
        )

):

    return (
        AdminController
        .update_user_status(
            db=db,
            user_id=
                user_id,
            is_active=
                is_active,
            current_admin_id=
                current_admin.id
        )
    )


# =========================================================
# RESERVAS
# =========================================================

@router.get(
    "/bookings"
)
def get_admin_bookings(

    search: str | None =
        Query(
            default=None
        ),

    status_filter: str =
        Query(
            default="all"
        ),

    barbershop_id: int | None =
        Query(
            default=None,
            ge=1
        ),

    barber_id: int | None =
        Query(
            default=None,
            ge=1
        ),

    date_from: str | None =
        Query(
            default=None
        ),

    date_to: str | None =
        Query(
            default=None
        ),

    limit: int =
        Query(
            default=20,
            ge=1,
            le=100
        ),

    offset: int =
        Query(
            default=0,
            ge=0
        ),

    db: Session =
        Depends(
            get_db
        ),

    current_admin: User =
        Depends(
            require_platform_admin
        )

):

    return (
        AdminController
        .bookings(
            db=db,

            search=
                search,

            status_filter=
                status_filter,

            barbershop_id=
                barbershop_id,

            barber_id=
                barber_id,

            date_from=
                date_from,

            date_to=
                date_to,

            limit=
                limit,

            offset=
                offset
        )
    )


# =========================================================
# CANCELAR RESERVA COMO ADMINISTRADOR
# =========================================================

@router.patch(
    "/bookings/{booking_id}/cancel"
)
def cancel_admin_booking(

    booking_id: int,

    db: Session =
        Depends(
            get_db
        ),

    current_admin: User =
        Depends(
            require_platform_admin
        )

):

    return (
        AdminController
        .cancel_booking(
            db=db,
            booking_id=
                booking_id
        )
    )


# =========================================================
# CONFIRMAR RESERVA COMO ADMINISTRADOR
# =========================================================

@router.patch(
    "/bookings/{booking_id}/confirm"
)
def confirm_admin_booking(

    booking_id: int,

    db: Session =
        Depends(
            get_db
        ),

    current_admin: User =
        Depends(
            require_platform_admin
        )

):

    return (
        AdminController
        .confirm_booking(
            db=db,
            booking_id=
                booking_id
        )
    )


# =========================================================
# COMPLETAR RESERVA COMO ADMINISTRADOR
# =========================================================

@router.patch(
    "/bookings/{booking_id}/complete"
)
def complete_admin_booking(

    booking_id: int,

    db: Session =
        Depends(
            get_db
        ),

    current_admin: User =
        Depends(
            require_platform_admin
        )

):

    return (
        AdminController
        .complete_booking(
            db=db,
            booking_id=
                booking_id
        )
    )