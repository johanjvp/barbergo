"""
Inicialización de una base de datos NUEVA (p. ej. en la nube).

Crea todas las tablas, la de ajustes de barbería (que no está en los modelos ORM),
aplica las migraciones aditivas y carga los datos base (roles y estados de reserva).
Es idempotente: se puede ejecutar varias veces.

Uso:  python init_db.py            (ver backend/init_db.py). Funciona en MySQL y PostgreSQL.
"""

import importlib
import pkgutil

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

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
    importlib.import_module("app.db.extra_tables")   # barbershop_settings, métodos de pago, verificaciones

    before = set(inspect(engine).get_table_names())
    Base.metadata.create_all(engine)
    created = set(inspect(engine).get_table_names()) - before
    if created:
        done.append(f"tablas creadas: {', '.join(sorted(created))}")

    done += [f"migración: {c}" for c in ensure_schema(engine)]

    # Consultar y luego insertar (en dos pasos) funciona igual en MySQL y PostgreSQL.
    with engine.begin() as conn:
        for role in ROLES:
            if conn.execute(text("SELECT 1 FROM roles WHERE name = :n"), {"n": role}).first() is None:
                conn.execute(text("INSERT INTO roles (name) VALUES (:n)"), {"n": role})

        for code, name in BOOKING_STATUSES:
            if conn.execute(text("SELECT 1 FROM booking_statuses WHERE code = :c"), {"c": code}).first() is None:
                conn.execute(text("INSERT INTO booking_statuses (code, name) VALUES (:c, :n)"), {"c": code, "n": name})
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
                    "VALUES (:f, :l, :e, :p, TRUE)"
                ),
                {"f": first_name, "l": last_name, "e": email, "p": hash_password(password)},
            )
            user_id = conn.execute(text("SELECT id FROM users WHERE email = :e"), {"e": email}).scalar()
            msg = f"usuario creado: {email}"
        else:
            msg = f"usuario existente promovido: {email}"

        role_id = conn.execute(text("SELECT id FROM roles WHERE name = 'PLATFORM_ADMIN'")).scalar()
        already = conn.execute(
            text("SELECT 1 FROM user_roles WHERE user_id = :u AND role_id = :r"), {"u": user_id, "r": role_id}
        ).first()
        if already is None:
            conn.execute(text("INSERT INTO user_roles (user_id, role_id) VALUES (:u, :r)"), {"u": user_id, "r": role_id})
    return msg + " con rol PLATFORM_ADMIN"
