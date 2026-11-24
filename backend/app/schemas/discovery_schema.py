from decimal import Decimal

from pydantic import BaseModel


class BarbershopDiscoveryItem(BaseModel):

    id: int

    name: str
    description: str | None

    address: str
    neighborhood: str | None

    city: str
    department: str

    latitude: Decimal | None
    longitude: Decimal | None

    phone: str | None
    email: str | None

    only_men: bool
    offers_vip: bool
    offers_home_service: bool

    starting_price: Decimal | None

    distance_km: float | None


class BarbershopDiscoveryResponse(BaseModel):

    total: int

    skip: int
    limit: int

    items: list[BarbershopDiscoveryItem]