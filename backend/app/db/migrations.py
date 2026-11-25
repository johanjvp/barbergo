"""
Migraciones aditivas e idempotentes.

El proyecto no usa Alembic: el esquema lo gestiona la base de datos.
Este módulo añade, al arrancar, las columnas y tablas nuevas de:

  * reservas sin cuenta (invitados)
  * servicio a domicilio
  * recordatorios por correo

Es seguro ejecutarlo varias veces: solo crea lo que falta.
"""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


BOOKING_COLUMNS = {
    "guest_name": "VARCHAR(150) NULL",
    "guest_phone": "VARCHAR(30) NULL",
    "guest_email": "VARCHAR(190) NULL",
    "manage_token": "VARCHAR(64) NULL",
    "contact_verified_at": "DATETIME NULL",
    "booking_type": "VARCHAR(12) NOT NULL DEFAULT 'IN_SHOP'",
    "home_address": "VARCHAR(300) NULL",
    "home_latitude": "DECIMAL(10,7) NULL",
    "home_longitude": "DECIMAL(10,7) NULL",
    "home_access_notes": "VARCHAR(300) NULL",
    "home_fee": "DECIMAL(12,2) NOT NULL DEFAULT 0",
    "reminder_24h_sent_at": "DATETIME NULL",
    "reminder_2h_sent_at": "DATETIME NULL",
    "payment_method": "VARCHAR(20) NULL",
    "payment_status": "VARCHAR(10) NOT NULL DEFAULT 'PENDING'",
    "payment_reference": "VARCHAR(80) NULL",
    "payment_reported_at": "DATETIME NULL",
    "payment_confirmed_at": "DATETIME NULL",
}

BARBERSHOP_COLUMNS = {
    "home_service_status": "VARCHAR(12) NOT NULL DEFAULT 'NONE'",
    "home_service_radius_km": "DECIMAL(5,1) NULL",
    "home_service_fee": "DECIMAL(12,2) NOT NULL DEFAULT 0",
    "home_service_min_notice_hours": "SMALLINT NOT NULL DEFAULT 3",
    "home_service_zones": "VARCHAR(500) NULL",
    "home_service_requirements": "TEXT NULL",
    "home_service_rejection_reason": "VARCHAR(300) NULL",
    "home_service_requested_at": "DATETIME NULL",
    "home_service_reviewed_at": "DATETIME NULL",
}

EMAIL_VERIFICATIONS_DDL = """
CREATE TABLE IF NOT EXISTS email_verifications (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(190) NOT NULL,
    code_hash CHAR(64) NOT NULL,
    purpose VARCHAR(20) NOT NULL DEFAULT 'GUEST_BOOKING',
    attempts SMALLINT NOT NULL DEFAULT 0,
    expires_at DATETIME NOT NULL,
    used_at DATETIME NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email_verifications_email (email, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""


PAYMENT_METHODS_DDL = """
CREATE TABLE IF NOT EXISTS barbershop_payment_methods (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    barbershop_id INT UNSIGNED NOT NULL,
    method VARCHAR(20) NOT NULL,
    bank_name VARCHAR(80) NULL,
    account_type VARCHAR(20) NULL,
    account_number VARCHAR(40) NULL,
    account_holder VARCHAR(120) NULL,
    holder_document VARCHAR(30) NULL,
    instructions VARCHAR(300) NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_shop_method (barbershop_id, method),
    CONSTRAINT fk_pm_barbershop FOREIGN KEY (barbershop_id)
        REFERENCES barbershops (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""


def _existing_columns(engine: Engine, table: str) -> set[str]:
    return {c["name"] for c in inspect(engine).get_columns(table)}


def _add_missing(conn, engine: Engine, table: str, columns: dict[str, str]) -> list[str]:
    present = _existing_columns(engine, table)
    added = []
    for name, ddl in columns.items():
        if name not in present:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
            added.append(f"{table}.{name}")
    return added


def ensure_schema(engine: Engine) -> list[str]:
    """Aplica los cambios pendientes y devuelve lo que se modificó."""
    changes: list[str] = []

    with engine.begin() as conn:
        changes += _add_missing(conn, engine, "bookings", BOOKING_COLUMNS)
        changes += _add_missing(conn, engine, "barbershops", BARBERSHOP_COLUMNS)

        # Reserva de invitado: client_user_id deja de ser obligatorio.
        col = next(
            c for c in inspect(engine).get_columns("bookings")
            if c["name"] == "client_user_id"
        )
        if not col["nullable"]:
            conn.execute(text(
                "ALTER TABLE bookings "
                "MODIFY client_user_id INT UNSIGNED NULL"
            ))
            changes.append("bookings.client_user_id -> NULL")

        # Índice único del token de gestión.
        indexes = {i["name"] for i in inspect(engine).get_indexes("bookings")}
        if "uq_bookings_manage_token" not in indexes:
            conn.execute(text(
                "ALTER TABLE bookings "
                "ADD UNIQUE INDEX uq_bookings_manage_token (manage_token)"
            ))
            changes.append("bookings.uq_bookings_manage_token")

        if "email_verifications" not in inspect(engine).get_table_names():
            conn.execute(text(EMAIL_VERIFICATIONS_DDL))
            changes.append("email_verifications (tabla)")

        if "barbershop_payment_methods" not in inspect(engine).get_table_names():
            conn.execute(text(PAYMENT_METHODS_DDL))
            changes.append("barbershop_payment_methods (tabla)")

        # Las barberías que ya ofrecían domicilio quedan aprobadas.
        conn.execute(text(
            "UPDATE barbershops SET home_service_status = 'APPROVED' "
            "WHERE offers_home_service = 1 AND home_service_status = 'NONE'"
        ))

    return changes
