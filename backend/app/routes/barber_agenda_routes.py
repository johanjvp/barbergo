from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    Query
)

from sqlalchemy.orm import Session

from app.controllers.barber_agenda_controller import (
    BarberAgendaController
)

from app.db.session import (
    get_db
)

from app.dependencies.role_dependencies import (
    require_roles
)

from app.models.user_model import (
    User
)

from app.schemas.barber_agenda_schema import (
    BarberAgendaResponse
)


router = APIRouter(
    prefix="/barber-agenda",
    tags=["Agenda del barbero"]
)


# =========================================================
# MI AGENDA
# =========================================================

@router.get(
    "/me",
    response_model=BarberAgendaResponse
)
def get_my_agenda(

    date_from: date | None = Query(
        default=None,
        description=
            "Fecha inicial de la agenda."
    ),

    date_to: date | None = Query(
        default=None,
        description=
            "Fecha final de la agenda."
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_roles(
            "BARBER"
        )
    )

):

    return (
        BarberAgendaController
        .get_my_agenda(
            db=db,
            current_user=current_user,
            date_from=date_from,
            date_to=date_to
        )
    )