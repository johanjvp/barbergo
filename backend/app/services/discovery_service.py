from decimal import Decimal
from math import (
    asin,
    cos,
    radians,
    sin,
    sqrt
)

from sqlalchemy.orm import Session

from app.core.exceptions import (
    InvalidBarbershopSearchError
)

from app.repositories.barbershop_repository import (
    BarbershopRepository
)


class DiscoveryService:

    # =====================================================
    # RADIO MEDIO DE LA TIERRA
    # =====================================================

    EARTH_RADIUS_KM = 6371.0


    # =====================================================
    # CALCULAR DISTANCIA ENTRE DOS COORDENADAS
    # =====================================================

    @staticmethod
    def _distance_km(
        latitude_a: float,
        longitude_a: float,
        latitude_b: float,
        longitude_b: float
    ) -> float:

        lat1 = radians(
            latitude_a
        )

        lon1 = radians(
            longitude_a
        )

        lat2 = radians(
            latitude_b
        )

        lon2 = radians(
            longitude_b
        )


        delta_lat = (
            lat2 - lat1
        )

        delta_lon = (
            lon2 - lon1
        )


        haversine = (
            sin(
                delta_lat / 2
            ) ** 2

            +

            cos(lat1)
            * cos(lat2)
            * sin(
                delta_lon / 2
            ) ** 2
        )


        distance = (
            2
            * DiscoveryService.EARTH_RADIUS_KM
            * asin(
                sqrt(haversine)
            )
        )


        return round(
            distance,
            2
        )


    # =====================================================
    # DESCUBRIR BARBERÍAS
    # =====================================================

    @staticmethod
    def discover(
        db: Session,
        q: str | None = None,
        neighborhood: str | None = None,
        service_name: str | None = None,
        max_price: Decimal | None = None,
        only_men: bool | None = None,
        offers_vip: bool | None = None,
        offers_home_service: bool | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        max_distance_km: float | None = None,
        sort: str = "name",
        skip: int = 0,
        limit: int = 20
    ):

        # -------------------------------------------------
        # LATITUD Y LONGITUD DEBEN LLEGAR JUNTAS
        # -------------------------------------------------

        if (
            (latitude is None)
            !=
            (longitude is None)
        ):

            raise InvalidBarbershopSearchError(
                "Debes enviar latitude y longitude "
                "juntas."
            )


        # -------------------------------------------------
        # FILTRAR POR DISTANCIA REQUIERE UBICACIÓN
        # -------------------------------------------------

        if (
            max_distance_km is not None
            and latitude is None
        ):

            raise InvalidBarbershopSearchError(
                "Para filtrar por distancia debes "
                "enviar latitude y longitude."
            )


        # -------------------------------------------------
        # ORDENAR POR DISTANCIA REQUIERE UBICACIÓN
        # -------------------------------------------------

        if (
            sort == "distance"
            and latitude is None
        ):

            raise InvalidBarbershopSearchError(
                "Para ordenar por distancia debes "
                "enviar latitude y longitude."
            )


        # -------------------------------------------------
        # CONSULTAR BARBERÍAS
        # -------------------------------------------------

        rows = (
            BarbershopRepository.discover(
                db=db,
                q=q,
                neighborhood=neighborhood,
                service_name=service_name,
                max_price=max_price,
                only_men=only_men,
                offers_vip=offers_vip,
                offers_home_service=
                    offers_home_service
            )
        )


        items = []


        # -------------------------------------------------
        # CONSTRUIR RESPUESTA
        # -------------------------------------------------

        for row in rows:

            shop = row[
                "barbershop"
            ]


            starting_price = row[
                "starting_price"
            ]


            distance_km = None


            # ---------------------------------------------
            # CALCULAR DISTANCIA SI TENEMOS:
            #
            # - UBICACIÓN DEL USUARIO
            # - COORDENADAS DE LA BARBERÍA
            #
            # IMPORTANTE:
            #
            # El modelo Barbershop utiliza:
            #
            # shop.latitude
            # shop.longitude
            # ---------------------------------------------

            if (
                latitude is not None
                and longitude is not None
                and shop.latitude is not None
                and shop.longitude is not None
            ):

                distance_km = (
                    DiscoveryService._distance_km(
                        latitude,
                        longitude,
                        float(
                            shop.latitude
                        ),
                        float(
                            shop.longitude
                        )
                    )
                )


            # ---------------------------------------------
            # FILTRAR POR RADIO
            # ---------------------------------------------

            if max_distance_km is not None:

                if (
                    distance_km is None
                    or distance_km
                    > max_distance_km
                ):

                    continue


            # ---------------------------------------------
            # AGREGAR BARBERÍA
            #
            # En SQLAlchemy:
            #
            # shop.latitude
            # shop.longitude
            #
            # En JSON para Angular:
            #
            # latitude
            # longitude
            # ---------------------------------------------

            items.append(
                {
                    "id":
                        shop.id,

                    "name":
                        shop.name,

                    "description":
                        shop.description,

                    "address":
                        shop.address,

                    "neighborhood":
                        shop.neighborhood,

                    "city":
                        shop.city,

                    "department":
                        shop.department,

                    "latitude":
                        shop.latitude,

                    "longitude":
                        shop.longitude,

                    "phone":
                        shop.phone,

                    "email":
                        shop.email,

                    "only_men":
                        shop.only_men,

                    "offers_vip":
                        shop.offers_vip,

                    "offers_home_service":
                        shop.offers_home_service,

                    "starting_price":
                        starting_price,

                    "distance_km":
                        distance_km
                }
            )


        # -------------------------------------------------
        # ORDENAR POR DISTANCIA
        # -------------------------------------------------

        if sort == "distance":

            items.sort(
                key=lambda item: (
                    item["distance_km"] is None,

                    item["distance_km"]
                    if item["distance_km"] is not None
                    else float("inf")
                )
            )


        # -------------------------------------------------
        # ORDENAR POR PRECIO
        # -------------------------------------------------

        elif sort == "price":

            items.sort(
                key=lambda item: (
                    item["starting_price"] is None,

                    item["starting_price"]
                    if item["starting_price"] is not None
                    else Decimal(
                        "999999999"
                    )
                )
            )


        # -------------------------------------------------
        # ORDENAR POR NOMBRE
        # -------------------------------------------------

        else:

            items.sort(
                key=lambda item:
                    item["name"].lower()
            )


        # -------------------------------------------------
        # PAGINACIÓN
        # -------------------------------------------------

        total = len(
            items
        )


        paginated_items = (
            items[
                skip:
                skip + limit
            ]
        )


        # -------------------------------------------------
        # RESPUESTA
        # -------------------------------------------------

        return {
            "total":
                total,

            "skip":
                skip,

            "limit":
                limit,

            "items":
                paginated_items
        }