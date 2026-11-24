from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from app.controllers.barber_controller import (
    BarberController
)

from app.db.session import get_db

from app.dependencies.role_dependencies import (
    require_roles
)

from app.models.user_model import User

from app.schemas.barber_schema import (
    BarberCreate,
    BarberResponse,
    BarberUpdate
)


router = APIRouter(
    tags=["Barberos"]
)


@router.post(
    "/barbershops/{barbershop_id}/barbers",
    response_model=BarberResponse,
    status_code=status.HTTP_201_CREATED
)
def create_barber(
    barbershop_id: int,
    data: BarberCreate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return BarberController.create(
        db,
        barbershop_id,
        data,
        current_user
    )


@router.get(
    "/barbershops/{barbershop_id}/barbers",
    response_model=list[BarberResponse]
)
def list_barbers(
    barbershop_id: int,
    db: Session = Depends(get_db)
):

    return BarberController.list_by_barbershop(
        db,
        barbershop_id
    )


@router.get(
    "/barbers/{barber_id}",
    response_model=BarberResponse
)
def get_barber(
    barber_id: int,
    db: Session = Depends(get_db)
):

    return BarberController.get_by_id(
        db,
        barber_id
    )


@router.patch(
    "/barbers/{barber_id}",
    response_model=BarberResponse
)
def update_barber(
    barber_id: int,
    data: BarberUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_roles(
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return BarberController.update(
        db,
        barber_id,
        data,
        current_user
    )