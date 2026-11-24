from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service_model import Service


class ServiceRepository:

    @staticmethod
    def create(
        db: Session,
        service: Service
    ) -> Service:

        db.add(service)

        db.flush()

        return service


    @staticmethod
    def get_by_id(
        db: Session,
        service_id: int
    ) -> Service | None:

        statement = select(
            Service
        ).where(
            Service.id == service_id
        )

        return db.scalar(statement)


    @staticmethod
    def list_by_barbershop(
        db: Session,
        barbershop_id: int
    ) -> list[Service]:

        statement = (
            select(Service)
            .where(
                Service.barbershop_id == barbershop_id,
                Service.is_active == True
            )
            .order_by(Service.name.asc())
        )

        return list(
            db.scalars(statement).all()
        )


    @staticmethod
    def update(
        db: Session,
        service: Service,
        values: dict
    ) -> Service:

        for field, value in values.items():

            setattr(
                service,
                field,
                value
            )

        db.flush()

        return service