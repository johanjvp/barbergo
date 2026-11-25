import os

from sqlalchemy import URL, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


def _build_url() -> URL:
    """MySQL con DB_* (por defecto) o cualquier base con DATABASE_URL (Neon/PostgreSQL, etc.)."""
    raw = (settings.DATABASE_URL or "").strip()

    if raw:
        # Los proveedores entregan "postgres://" o "postgresql://": se elige el controlador instalado.
        for prefix in ("postgres://", "postgresql://"):
            if raw.startswith(prefix):
                raw = "postgresql+psycopg://" + raw[len(prefix):]
        if raw.startswith("mysql://"):
            raw = "mysql+pymysql://" + raw[len("mysql://"):]
        return make_url(raw)

    return URL.create(
        drivername="mysql+pymysql",
        username=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        query={"charset": "utf8mb4"}
    )


DATABASE_URL = _build_url()
IS_POSTGRES = DATABASE_URL.get_backend_name() == "postgresql"

# En Vercel cada petición puede ser una instancia nueva: pocas conexiones y recicladas.
IS_SERVERLESS = bool(os.getenv("VERCEL"))

connect_args: dict = {}

if IS_POSTGRES:
    # Neon (y PgBouncer en modo transacción) no admite sentencias preparadas en el servidor.
    connect_args["prepare_threshold"] = None

    if settings.DB_SSL and "sslmode" not in DATABASE_URL.query:
        connect_args["sslmode"] = "require"
elif settings.DB_SSL:
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