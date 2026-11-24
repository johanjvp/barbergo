from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Response,
    status
)

from sqlalchemy.orm import Session

from app.controllers.schedule_controller import (
    ScheduleController
)

from app.db.session import get_db

from app.dependencies.role_dependencies import (
    require_roles
)

from app.models.user_model import User

from app.schemas.schedule_schema import (
    BarbershopScheduleUpsert,
    BarbershopScheduleResponse,
    BarberScheduleUpsert,
    BarberScheduleResponse,
    BarberBlockCreate,
    BarberBlockResponse,
    BarberWeeklyAgendaResponse
)


router = APIRouter(
    tags=["Horarios"]
)


# =========================================================
# HORARIOS BARBERÍA
# =========================================================

@router.put(
    "/barbershops/{barbershop_id}/schedules/{day_of_week}",
    response_model=BarbershopScheduleResponse
)
def set_barbershop_schedule(
    barbershop_id: int,
    data: BarbershopScheduleUpsert,

    day_of_week: int = Path(
        ge=1,
        le=7
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_roles(
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return (
        ScheduleController
        .set_barbershop_schedule(
            db,
            barbershop_id,
            day_of_week,
            data,
            current_user
        )
    )


# =========================================================
# LISTAR HORARIO BARBERÍA
# =========================================================

@router.get(
    "/barbershops/{barbershop_id}/schedules",
    response_model=list[
        BarbershopScheduleResponse
    ]
)
def list_barbershop_schedule(
    barbershop_id: int,

    db: Session = Depends(
        get_db
    )
):

    return (
        ScheduleController
        .list_barbershop_schedule(
            db,
            barbershop_id
        )
    )


# =========================================================
# HORARIOS BARBERO
# =========================================================

@router.put(
    "/barbers/{barber_id}/schedules/{day_of_week}",
    response_model=BarberScheduleResponse
)
def set_barber_schedule(
    barber_id: int,
    data: BarberScheduleUpsert,

    day_of_week: int = Path(
        ge=1,
        le=7
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_roles(
            "BARBER",
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return (
        ScheduleController
        .set_barber_schedule(
            db,
            barber_id,
            day_of_week,
            data,
            current_user
        )
    )


# =========================================================
# LISTAR HORARIO BARBERO
# =========================================================

@router.get(
    "/barbers/{barber_id}/schedules",
    response_model=list[
        BarberScheduleResponse
    ]
)
def list_barber_schedule(
    barber_id: int,

    db: Session = Depends(
        get_db
    )
):

    return (
        ScheduleController
        .list_barber_schedule(
            db,
            barber_id
        )
    )


# =========================================================
# AGENDA SEMANAL BARBERO
# =========================================================

@router.get(
    "/barbers/{barber_id}/weekly-agenda",
    response_model=BarberWeeklyAgendaResponse
)
def get_barber_weekly_agenda(
    barber_id: int,

    week_start: date = Query(
        description=(
            "Fecha de referencia para consultar "
            "la semana del barbero."
        )
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_roles(
            "BARBER",
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return (
        ScheduleController
        .get_barber_weekly_agenda(
            db=db,
            barber_id=barber_id,
            week_start=week_start
        )
    )


# =========================================================
# BLOQUEOS
# =========================================================

@router.post(
    "/barbers/{barber_id}/blocks",
    response_model=BarberBlockResponse,
    status_code=status.HTTP_201_CREATED
)
def create_block(
    barber_id: int,
    data: BarberBlockCreate,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_roles(
            "BARBER",
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    return (
        ScheduleController
        .create_block(
            db,
            barber_id,
            data,
            current_user
        )
    )


# =========================================================
# LISTAR BLOQUEOS
# =========================================================

@router.get(
    "/barbers/{barber_id}/blocks",
    response_model=list[
        BarberBlockResponse
    ]
)
def list_blocks(
    barber_id: int,

    db: Session = Depends(
        get_db
    )
):

    return (
        ScheduleController
        .list_blocks(
            db,
            barber_id
        )
    )


# =========================================================
# ELIMINAR BLOQUEO
# =========================================================

@router.delete(
    "/barber-blocks/{block_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_block(
    block_id: int,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_roles(
            "BARBER",
            "BARBERSHOP_ADMIN",
            "PLATFORM_ADMIN"
        )
    )
):

    ScheduleController.delete_block(
        db,
        block_id,
        current_user
    )


    return Response(
        status_code=
            status.HTTP_204_NO_CONTENT
    )