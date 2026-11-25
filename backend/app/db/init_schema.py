"""
Inicialización de una base de datos NUEVA (p. ej. en la nube).

Crea todas las tablas, la de ajustes de barbería (que no está en los modelos ORM),
aplica las migraciones aditivas y carga los datos base (roles y estados de reserva).
Es idempotente: se puede ejecutar varias veces.

Uso:  python init_db.py            (ver backend/init_db.py)
"""

import importlib
import pkgutil

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

BARBERSHOP_SETTINGS_DDL = """
CREATE TABLE IF NOT EXISTS barbershop_settings (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    barbershop_id INT UNSIGNED NOT NULL UNIQUE,
    bookings_enabled TINYINT(1) NOT NULL DEFAULT 1,
    auto_confirm_bookings TINYINT(1) NOT NULL DEFAULT 0,
    allow_same_day_booking TINYINT(1) NOT NULL DEFAULT 1,
    allow_overbooking TINYINT(1) NOT NULL DEFAULT 0,
    allow_any_available_barber TINYINT(1) NOT NULL DEFAULT 1,
    allow_customer_notes TINYINT(1) NOT NULL DEFAULT 1,
    allow_customer_cancellation TINYINT(1) NOT NULL DEFAULT 1,
    allow_reschedule TINYINT(1) NOT NULL DEFAULT 1,
    customer_can_choose_barber TINYINT(1) NOT NULL DEFAULT 1,
    require_customer_account TINYINT(1) NOT NULL DEFAULT 0,
    require_customer_phone TINYINT(1) NOT NULL DEFAULT 0,
    booking_interval_minutes INT NOT NULL DEFAULT 15,
    max_booking_days_ahead INT NOT NULL DEFAULT 60,
    min_booking_notice_minutes INT NOT NULL DEFAULT 0,
    buffer_between_bookings_minutes INT NOT NULL DEFAULT 0,
    cancellation_limit_minutes INT NOT NULL DEFAULT 120,
    reschedule_limit_minutes INT NOT NULL DEFAULT 120,
    tolerance_minutes INT NOT NULL DEFAULT 10,
    barber_can_confirm_bookings TINYINT(1) NOT NULL DEFAULT 1,
    barber_can_cancel_bookings TINYINT(1) NOT NULL DEFAULT 1,
    barber_can_start_service TINYINT(1) NOT NULL DEFAULT 1,
    barber_can_complete_service TINYINT(1) NOT NULL DEFAULT 1,
    barber_can_edit_schedule TINYINT(1) NOT NULL DEFAULT 0,
    barber_can_block_schedule TINYINT(1) NOT NULL DEFAULT 1,
    send_booking_reminders TINYINT(1) NOT NULL DEFAULT 1,
    reminder_minutes_before INT NOT NULL DEFAULT 60,
    notify_customer_confirmation TINYINT(1) NOT NULL DEFAULT 1,
    notify_customer_cancellation TINYINT(1) NOT NULL DEFAULT 1,
    notify_barber_new_booking TINYINT(1) NOT NULL DEFAULT 1,
    notify_barber_cancellation TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""

ROLES = ("CLIENT", "BARBER", "BARBERSHOP_ADMIN", "PLATFORM_ADMIN")

BOOKING_STATUSES = (
    ("PENDING", "Pendiente"),
    ("CONFIRMED", "Confirmada"),
    ("IN_PROGRESS", "En curso"),
    ("COMPLETED", "Completada"),
    ("REJECTED", "Rechazada"),
    ("CANCELLED_BY_CUSTOMER", "Cancelada por el cliente"),
    ("CANCELLED_BY_BARBER", "Cancelada por el barbero"),
    ("CANCELLED_BY_ADMIN", "Cancelada por la barbería"),
    ("NO_SHOW", "No asistió"),
)


def _import_models() -> None:
    import app.models as models_pkg

    for module in pkgutil.iter_modules(models_pkg.__path__):
        importlib.import_module(f"app.models.{module.name}")


def init_schema(engine: Engine) -> list[str]:
    """Crea tablas, ajustes, migraciones y datos base. Devuelve un resumen de lo hecho."""
    from app.db.base import Base
    from app.db.migrations import ensure_schema

    done: list[str] = []
    _import_models()

    before = set(inspect(engine).get_table_names())
    Base.metadata.create_all(engine)
    created = set(inspect(engine).get_table_names()) - before
    if created:
        done.append(f"tablas creadas: {', '.join(sorted(created))}")

    with engine.begin() as conn:
        conn.execute(text(BARBERSHOP_SETTINGS_DDL))

    done += [f"migración: {c}" for c in ensure_schema(engine)]

    with engine.begin() as conn:
        for role in ROLES:
            conn.execute(
                text("INSERT INTO roles (name) SELECT :n WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = :n)"),
                {"n": role},
            )
        for code, name in BOOKING_STATUSES:
            conn.execute(
                text(
                    "INSERT INTO booking_statuses (code, name) "
                    "SELECT :c, :n FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM booking_statuses WHERE code = :c)"
                ),
                {"c": code, "n": name},
            )
    done.append("datos base: roles y estados de reserva")
    return done


def create_platform_admin(engine: Engine, email: str, password: str, first_name: str = "Admin", last_name: str = "BarberGo") -> str:
    """Crea (o promueve) un usuario PLATFORM_ADMIN. Devuelve un mensaje."""
    from app.core.security import hash_password

    with engine.begin() as conn:
        user_id = conn.execute(text("SELECT id FROM users WHERE email = :e"), {"e": email}).scalar()
        if user_id is None:
            conn.execute(
                text(
                    "INSERT INTO users (first_name, last_name, email, password_hash, is_active) "
                    "VALUES (:f, :l, :e, :p, 1)"
                ),
                {"f": first_name, "l": last_name, "e": email, "p": hash_password(password)},
            )
            user_id = conn.execute(text("SELECT id FROM users WHERE email = :e"), {"e": email}).scalar()
            msg = f"usuario creado: {email}"
        else:
            msg = f"usuario existente promovido: {email}"

        conn.execute(
            text(
                "INSERT INTO user_roles (user_id, role_id) "
                "SELECT :u, r.id FROM roles r WHERE r.name = 'PLATFORM_ADMIN' "
                "AND NOT EXISTS (SELECT 1 FROM user_roles ur WHERE ur.user_id = :u AND ur.role_id = r.id)"
            ),
            {"u": user_id},
        )
    return msg + " con rol PLATFORM_ADMIN"
