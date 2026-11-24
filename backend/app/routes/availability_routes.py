from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    Query
)

from sqlalchemy.orm import Session

from app.controllers.availability_controller import (
    AvailabilityController
)

from app.db.session import get_db

from app.schemas.availability_schema import (
    AvailabilityResponse
)


router = APIRouter(
    tags=["Disponibilidad"]
)


@router.get(
    "/barbers/{barber_id}/availability",
    response_model=AvailabilityResponse
)
def get_availability(
    barber_id: int,

    service_id: int = Query(
        ...,
        gt=0
    ),

    requested_date: date = Query(
        ...,
        alias="date"
    ),

    db: Session = Depends(get_db)
):

    return (
        AvailabilityController
        .get_availability(
            db,
            barber_id,
            service_id,
            requested_date
        )
    )