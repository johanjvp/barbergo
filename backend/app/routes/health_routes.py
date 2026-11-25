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
            if engine.dialect.name == "postgresql":
                query = "SELECT current_database() AS database_name, version() AS database_version"
            else:
                query = "SELECT DATABASE() AS database_name, VERSION() AS database_version"

            row = connection.execute(text(query)).mappings().one()

        return {
            "api": "ok",
            "database": "ok",
            "engine": engine.dialect.name,
            "database_name": row["database_name"],
            "database_version": row["database_version"]
        }
    except SQLAlchemyError:

        raise HTTPException(
            status_code=503,
            detail="No fue posible conectar con la base de datos."
        )