"""
Migraciones aditivas e idempotentes (MySQL y PostgreSQL).

El proyecto no usa Alembic: el esquema lo gestiona la base de datos.
Este módulo añade, al arrancar, las columnas y tablas nuevas de:

  * reservas sin cuenta (invitados)
  * servicio a domicilio
  * pago directo
  * recordatorios por correo

Es seguro ejecutarlo varias veces: solo crea lo que falta.
"""

from sqlalchemy import (
    Column,
    DateTime,
    MetaData,
    Numeric,
    SmallInteger,
    String,
    Table,
    Text,
    inspect,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateColumn


def _c(name, type_, nullable=True, default=None) -> Column:
    return Column(name, type_, nullable=nullable, server_default=default)


# Se agrupan en tablas "de paso" (solo para generar el SQL de cada dialecto).
_BOOKINGS = Table(
    "bookings",
    MetaData(),
    _c("guest_name", String(150)),
    _c("guest_phone", String(30)),
    _c("guest_email", String(190)),
    _c("manage_token", String(64)),
    _c("contact_verified_at", DateTime),
    _c("booking_type", String(12), False, text("'IN_SHOP'")),
    _c("home_address", String(300)),
    _c("home_latitude", Numeric(10, 7)),
    _c("home_longitude", Numeric(10, 7)),
    _c("home_access_notes", String(300)),
    _c("home_fee", Numeric(12, 2), False, text("0")),
    _c("reminder_24h_sent_at", DateTime),
    _c("reminder_2h_sent_at", DateTime),
    _c("payment_method", String(20)),
    _c("payment_status", String(10), False, text("'PENDING'")),
    _c("payment_reference", String(80)),
    _c("payment_reported_at", DateTime),
    _c("payment_confirmed_at", DateTime),
)

_BARBERSHOPS = Table(
    "barbershops",
    MetaData(),
    _c("home_service_status", String(12), False, text("'NONE'")),
    _c("home_service_radius_km", Numeric(5, 1)),
    _c("home_service_fee", Numeric(12, 2), False, text("0")),
    _c("home_service_min_notice_hours", SmallInteger, False, text("3")),
    _c("home_service_zones", String(500)),
    _c("home_service_requirements", Text),
    _c("home_service_rejection_reason", String(300)),
    _c("home_service_requested_at", DateTime),
    _c("home_service_reviewed_at", DateTime),
)

# nombre -> Column (iterar devuelve los nombres)
BOOKING_COLUMNS = {c.name: c for c in _BOOKINGS.columns}
BARBERSHOP_COLUMNS = {c.name: c for c in _BARBERSHOPS.columns}


def _existing_columns(conn, table: str) -> set[str]:
    # Se inspecciona con la MISMA conexión: en PostgreSQL el DDL es transaccional y otra
    # conexión se quedaría esperando el bloqueo de la tabla que acabamos de modificar.
    return {c["name"] for c in inspect(conn).get_columns(table)}


def _add_missing(conn, engine: Engine, table: str, columns: dict[str, Column]) -> list[str]:
    present = _existing_columns(conn, table)
    added = []
    for name, column in columns.items():
        if name not in present:
            ddl = CreateColumn(column).compile(dialect=engine.dialect)
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))
            added.append(f"{table}.{name}")
    return added


def _has_unique(engine: Engine, table: str, column: str) -> bool:
    inspector = inspect(engine)
    for uc in inspector.get_unique_constraints(table):
        if uc["column_names"] == [column]:
            return True
    for ix in inspector.get_indexes(table):
        if ix.get("unique") and ix["column_names"] == [column]:
            return True
    return False


def ensure_schema(engine: Engine) -> list[str]:
    """Aplica los cambios pendientes y devuelve lo que se modificó."""
    from app.db.base import Base
    from app.db.extra_tables import EXTRA_TABLES  # noqa: F401  (registra las tablas)

    changes: list[str] = []

    # Tablas nuevas (verificaciones, métodos de pago, ajustes) si faltan.
    existing = set(inspect(engine).get_table_names())
    missing = [t for t in EXTRA_TABLES if t.name not in existing and "barbershops" in existing]
    if missing:
        Base.metadata.create_all(engine, tables=missing)
        changes += [f"{t.name} (tabla)" for t in missing]

    with engine.begin() as conn:
        changes += _add_missing(conn, engine, "bookings", BOOKING_COLUMNS)
        changes += _add_missing(conn, engine, "barbershops", BARBERSHOP_COLUMNS)

        # Reserva de invitado: client_user_id deja de ser obligatorio.
        col = next(c for c in inspect(conn).get_columns("bookings") if c["name"] == "client_user_id")
        if not col["nullable"]:
            if engine.dialect.name == "postgresql":
                conn.execute(text("ALTER TABLE bookings ALTER COLUMN client_user_id DROP NOT NULL"))
            else:
                conn.execute(text("ALTER TABLE bookings MODIFY client_user_id INT UNSIGNED NULL"))
            changes.append("bookings.client_user_id -> NULL")

    # Token de gestión único.
    if not _has_unique(engine, "bookings", "manage_token"):
        with engine.begin() as conn:
            conn.execute(text("CREATE UNIQUE INDEX uq_bookings_manage_token ON bookings (manage_token)"))
        changes.append("bookings.uq_bookings_manage_token")

    # Las barberías que ya ofrecían domicilio quedan aprobadas.
    with engine.begin() as conn:
        conn.execute(text(
            "UPDATE barbershops SET home_service_status = 'APPROVED' "
            "WHERE offers_home_service = TRUE AND home_service_status = 'NONE'"
        ))

    return changes
