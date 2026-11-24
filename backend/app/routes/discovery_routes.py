from decimal import Decimal
from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    Query
)

from sqlalchemy.orm import Session

from app.controllers.discovery_controller import (
    DiscoveryController
)

from app.db.session import (
    get_db
)

from app.schemas.discovery_schema import (
    BarbershopDiscoveryResponse
)


router = APIRouter(
    prefix="/barbershops",
    tags=["Descubrir barberías"]
)


@router.get(
    "/discover",
    response_model=BarbershopDiscoveryResponse
)
def discover_barbershops(

    q: str | None = Query(
        default=None,
        max_length=100
    ),

    neighborhood: str | None = Query(
        default=None,
        max_length=100
    ),

    service: str | None = Query(
        default=None,
        max_length=120
    ),

    max_price: Decimal | None = Query(
        default=None,
        gt=0
    ),

    only_men: bool | None = Query(
        default=None
    ),

    offers_vip: bool | None = Query(
        default=None
    ),

    offers_home_service: bool | None = Query(
        default=None
    ),

    latitude: float | None = Query(
        default=None,
        ge=-90,
        le=90
    ),

    longitude: float | None = Query(
        default=None,
        ge=-180,
        le=180
    ),

    max_distance_km: float | None = Query(
        default=None,
        gt=0,
        le=100
    ),

    sort: Literal[
        "name",
        "price",
        "distance"
    ] = Query(
        default="name"
    ),

    skip: int = Query(
        default=0,
        ge=0
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100
    ),

    db: Session = Depends(
        get_db
    )
):

    return (
        DiscoveryController.discover(
            db=db,
            q=q,
            neighborhood=neighborhood,
            service_name=service,
            max_price=max_price,
            only_men=only_men,
            offers_vip=offers_vip,
            offers_home_service=
                offers_home_service,
            latitude=latitude,
            longitude=longitude,
            max_distance_km=
                max_distance_km,
            sort=sort,
            skip=skip,
            limit=limit
        )
    )