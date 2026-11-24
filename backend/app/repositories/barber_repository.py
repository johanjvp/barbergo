from sqlalchemy import (
    delete,
    func,
    insert,
    select
)

from sqlalchemy.orm import Session

from app.models.barber_model import Barber

from app.models.barber_service_association import (
    barber_services
)

from app.models.service_model import Service


class BarberRepository:

    @staticmethod
    def create(
        db: Session,
        barber: Barber
    ) -> Barber:

        db.add(barber)
        db.flush()

        return barber


    @staticmethod
    def get_by_id(
        db: Session,
        barber_id: int
    ) -> Barber | None:

        statement = select(
            Barber
        ).where(
            Barber.id == barber_id
        )

        return db.scalar(statement)


    @staticmethod
    def get_by_user_id(
        db: Session,
        user_id: int
    ) -> Barber | None:

        statement = select(
            Barber
        ).where(
            Barber.user_id == user_id
        )

        return db.scalar(statement)


    @staticmethod
    def count_active_by_barbershop(
        db: Session,
        barbershop_id: int
    ) -> int:

        statement = select(
            func.count(Barber.id)
        ).where(
            Barber.barbershop_id == barbershop_id,
            Barber.is_active == True
        )

        return db.scalar(statement) or 0


    @staticmethod
    def list_by_barbershop(
        db: Session,
        barbershop_id: int
    ) -> list[Barber]:

        statement = (
            select(Barber)
            .where(
                Barber.barbershop_id == barbershop_id,
                Barber.is_active == True
            )
            .order_by(Barber.id.asc())
        )

        return list(
            db.scalars(statement).all()
        )


    @staticmethod
    def get_services_for_barber(
        db: Session,
        barber_id: int
    ) -> list[int]:

        statement = select(
            barber_services.c.service_id
        ).where(
            barber_services.c.barber_id
            == barber_id
        )

        return list(
            db.scalars(statement).all()
        )


    @staticmethod
    def get_valid_service_ids(
        db: Session,
        barbershop_id: int,
        service_ids: list[int]
    ) -> list[int]:

        if not service_ids:
            return []

        statement = select(
            Service.id
        ).where(
            Service.id.in_(service_ids),
            Service.barbershop_id == barbershop_id,
            Service.is_active == True
        )

        return list(
            db.scalars(statement).all()
        )


    @staticmethod
    def replace_services(
        db: Session,
        barber_id: int,
        service_ids: list[int]
    ):

        db.execute(
            delete(
                barber_services
            ).where(
                barber_services.c.barber_id
                == barber_id
            )
        )

        if service_ids:

            db.execute(
                insert(
                    barber_services
                ),
                [
                    {
                        "barber_id": barber_id,
                        "service_id": service_id
                    }
                    for service_id in service_ids
                ]
            )


    @staticmethod
    def update(
        db: Session,
        barber: Barber,
        values: dict
    ) -> Barber:

        for field, value in values.items():

            setattr(
                barber,
                field,
                value
            )

        db.flush()

        return barber