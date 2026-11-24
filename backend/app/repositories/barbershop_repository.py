from sqlalchemy import select
from sqlalchemy.orm import Session
from decimal import Decimal

from sqlalchemy import (
    exists,
    func,
    or_,
    select
)   

from app.models.service_model import Service
from app.models.barbershop_model import Barbershop


class BarbershopRepository:

    @staticmethod
    def create(
        db: Session,
        barbershop: Barbershop
    ) -> Barbershop:

        db.add(barbershop)
        db.flush()

        return barbershop


    @staticmethod
    def get_by_id(
        db: Session,
        barbershop_id: int
    ) -> Barbershop | None:

        statement = select(
            Barbershop
        ).where(
            Barbershop.id == barbershop_id
        )

        return db.scalar(statement)


    @staticmethod
    def list_active(
        db: Session,
        skip: int = 0,
        limit: int = 50
    ) -> list[Barbershop]:

        statement = (
            select(Barbershop)
            .where(
                Barbershop.is_active == True
            )
            .offset(skip)
            .limit(limit)
            .order_by(Barbershop.id.desc())
        )

        return list(
            db.scalars(statement).all()
        )


    @staticmethod
    def update(
        db: Session,
        barbershop: Barbershop,
        values: dict
    ) -> Barbershop:

        for field, value in values.items():
            setattr(
                barbershop,
                field,
                value
            )

        db.flush()

        return barbershop
    
        # =====================================================
    # DESCUBRIR / BUSCAR BARBERÍAS
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
        offers_home_service: bool | None = None
    ):

        # -------------------------------------------------
        # PRECIO MÁS BAJO DE CADA BARBERÍA
        # -------------------------------------------------

        starting_price = (
            select(
                func.min(
                    Service.price
                )
            )
            .where(
                Service.barbershop_id
                == Barbershop.id,

                Service.is_active.is_(True)
            )
            .correlate(
                Barbershop
            )
            .scalar_subquery()
        )


        statement = (
            select(
                Barbershop,
                starting_price.label(
                    "starting_price"
                )
            )
            .where(
                Barbershop.is_active.is_(True)
            )
        )


        # -------------------------------------------------
        # BÚSQUEDA GENERAL
        #
        # Busca en:
        # - nombre barbería
        # - barrio
        # - dirección
        # - nombre de servicio
        # -------------------------------------------------

        if q:

            pattern = f"%{q.strip()}%"

            service_exists = (
                exists()
                .where(
                    Service.barbershop_id
                    == Barbershop.id,

                    Service.is_active.is_(True),

                    Service.name.ilike(
                        pattern
                    )
                )
            )

            statement = statement.where(
                or_(
                    Barbershop.name.ilike(
                        pattern
                    ),

                    Barbershop.neighborhood.ilike(
                        pattern
                    ),

                    Barbershop.address.ilike(
                        pattern
                    ),

                    service_exists
                )
            )


        # -------------------------------------------------
        # BARRIO
        # -------------------------------------------------

        if neighborhood:

            statement = statement.where(
                Barbershop.neighborhood.ilike(
                    f"%{neighborhood.strip()}%"
                )
            )


        # -------------------------------------------------
        # SOLO HOMBRES
        # -------------------------------------------------

        if only_men is not None:

            statement = statement.where(
                Barbershop.only_men
                == only_men
            )


        # -------------------------------------------------
        # VIP
        # -------------------------------------------------

        if offers_vip is not None:

            statement = statement.where(
                Barbershop.offers_vip
                == offers_vip
            )


        # -------------------------------------------------
        # SERVICIO A DOMICILIO
        # -------------------------------------------------

        if offers_home_service is not None:

            statement = statement.where(
                Barbershop.offers_home_service
                == offers_home_service
            )


        # -------------------------------------------------
        # FILTROS SOBRE SERVICIOS
        # -------------------------------------------------

        if (
            service_name is not None
            or max_price is not None
        ):

            service_filters = [
                Service.barbershop_id
                == Barbershop.id,

                Service.is_active.is_(True)
            ]


            if service_name:

                service_filters.append(
                    Service.name.ilike(
                        f"%{service_name.strip()}%"
                    )
                )


            if max_price is not None:

                service_filters.append(
                    Service.price
                    <= max_price
                )


            service_match = (
                exists()
                .where(
                    *service_filters
                )
            )

            statement = statement.where(
                service_match
            )


        # -------------------------------------------------
        # ORDEN BASE
        # -------------------------------------------------

        statement = statement.order_by(
            Barbershop.name.asc()
        )


        rows = db.execute(
            statement
        ).all()


        return [
            {
                "barbershop": row[0],
                "starting_price": row[1]
            }
            for row in rows
        ]