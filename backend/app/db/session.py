import os

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


DATABASE_URL = URL.create(
    drivername="mysql+pymysql",

    username=settings.DB_USER,
    password=settings.DB_PASSWORD,

    host=settings.DB_HOST,
    port=settings.DB_PORT,

    database=settings.DB_NAME,

    query={
        "charset": "utf8mb4"
    }
)


# En Vercel cada petición puede ser una instancia nueva: pocas conexiones y recicladas.
IS_SERVERLESS = bool(os.getenv("VERCEL"))

connect_args: dict = {}

if settings.DB_SSL:
    import certifi

    connect_args["ssl"] = {"ca": certifi.where()}

engine_options: dict = {
    # Verifica conexiones muertas antes de utilizarlas.
    "pool_pre_ping": True,
    "echo": False,
    "connect_args": connect_args,
}

if IS_SERVERLESS:
    engine_options.update(pool_size=1, max_overflow=2, pool_recycle=240)

engine = create_engine(
    DATABASE_URL,
    **engine_options
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()