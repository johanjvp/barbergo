from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.barbershop_admin_model import (
    BarbershopAdmin
)

from app.models.user_model import (
    User
)


class BarbershopAdminRepository:

    @staticmethod
    def create(
        db: Session,
        assignment: BarbershopAdmin
    ) -> BarbershopAdmin:

        db.add(assignment)
        db.flush()

        return assignment


    @staticmethod
    def get_assignment(
        db: Session,
        user_id: int,
        barbershop_id: int
    ) -> BarbershopAdmin | None:

        statement = (
            select(BarbershopAdmin)
            .where(
                BarbershopAdmin.user_id
                == user_id,

                BarbershopAdmin.barbershop_id
                == barbershop_id
            )
        )

        return db.scalar(statement)


    @staticmethod
    def has_active_access(
        db: Session,
        user_id: int,
        barbershop_id: int
    ) -> bool:

        statement = (
            select(BarbershopAdmin.id)
            .where(
                BarbershopAdmin.user_id
                == user_id,

                BarbershopAdmin.barbershop_id
                == barbershop_id,

                BarbershopAdmin.is_active
                == True
            )
            .limit(1)
        )

        return (
            db.scalar(statement)
            is not None
        )


    @staticmethod
    def list_by_user(
        db: Session,
        user_id: int
    ) -> list[BarbershopAdmin]:

        statement = (
            select(BarbershopAdmin)
            .where(
                BarbershopAdmin.user_id
                == user_id,

                BarbershopAdmin.is_active
                == True
            )
            .order_by(
                BarbershopAdmin.barbershop_id.asc()
            )
        )

        return list(
            db.scalars(statement).all()
        )


    @staticmethod
    def list_by_barbershop(
        db: Session,
        barbershop_id: int
    ) -> list[dict]:

        statement = (
            select(
                BarbershopAdmin.id,
                BarbershopAdmin.user_id,
                BarbershopAdmin.barbershop_id,
                BarbershopAdmin.is_active,
                User.first_name,
                User.last_name,
                User.email
            )
            .join(
                User,
                User.id
                == BarbershopAdmin.user_id
            )
            .where(
                BarbershopAdmin.barbershop_id
                == barbershop_id,

                BarbershopAdmin.is_active
                == True
            )
            .order_by(
                User.first_name.asc(),
                User.last_name.asc()
            )
        )

        rows = (
            db.execute(
                statement
            )
            .mappings()
            .all()
        )

        return [
            {
                "id":
                    int(
                        row["id"]
                    ),

                "user_id":
                    int(
                        row["user_id"]
                    ),

                "barbershop_id":
                    int(
                        row["barbershop_id"]
                    ),

                "first_name":
                    row["first_name"],

                "last_name":
                    row["last_name"],

                "email":
                    row["email"],

                "is_active":
                    bool(
                        row["is_active"]
                    )
            }

            for row in rows
        ]


    @staticmethod
    def deactivate(
        db: Session,
        assignment: BarbershopAdmin
    ) -> BarbershopAdmin:

        assignment.is_active = False

        db.flush()

        return assignment


    @staticmethod
    def activate(
        db: Session,
        assignment: BarbershopAdmin
    ) -> BarbershopAdmin:

        assignment.is_active = True

        db.flush()

        return assignment