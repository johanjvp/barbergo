from fastapi import APIRouter, HTTPException

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine


router = APIRouter(
    tags=["Health"]
)


@router.get("/health")
def health_check():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text(
                    """
                    SELECT
                        DATABASE() AS database_name,
                        VERSION() AS mysql_version
                    """
                )
            )

            row = result.mappings().one()

        return {
            "api": "ok",
            "database": "ok",
            "database_name": row["database_name"],
            "mysql_version": row["mysql_version"]
        }

    except SQLAlchemyError as error:

        print(error)

        raise HTTPException(
            status_code=503,
            detail="La API está activa pero no fue posible conectar con MySQL"
        )