from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine


router = APIRouter(
    tags=["Sistema"]
)


@router.get("/health")
def health():

    try:

        with engine.connect() as connection:

            row = connection.execute(
                text(
                    """
                    SELECT
                        DATABASE() AS database_name,
                        VERSION() AS mysql_version
                    """
                )
            ).mappings().one()

        return {
            "api": "ok",
            "database": "ok",
            "database_name":
                row["database_name"],
            "mysql_version":
                row["mysql_version"]
        }

    except SQLAlchemyError:

        raise HTTPException(
            status_code=503,
            detail="No fue posible conectar con MySQL."
        )