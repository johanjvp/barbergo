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


engine = create_engine(
    DATABASE_URL,

    # Verifica conexiones muertas antes de utilizarlas.
    pool_pre_ping=True,

    # Más adelante podemos poner True para estudiar
    # las consultas SQL generadas por SQLAlchemy.
    echo=False
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