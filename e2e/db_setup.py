"""
Prepara la base de pruebas:

  1. Crea el esquema "antiguo" (sin las columnas nuevas), como lo tendría
     una base ya existente, y comprueba que ensure_schema() la migra
     (y que es idempotente).
  2. Carga datos mínimos: roles, estados, usuarios, barbería, servicios,
     barbero y horarios.

Uso:  python e2e/db_setup.py
"""

import importlib
import json
import pkgutil
import sys
from datetime import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import env  # noqa: E402

env.apply()

from sqlalchemy import inspect, text  # noqa: E402

import app.models as models_pkg  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.migrations import (  # noqa: E402
    BARBERSHOP_COLUMNS,
    BOOKING_COLUMNS,
    ensure_schema,
)
from app.db.session import SessionLocal, engine  # noqa: E402

for m in pkgutil.iter_modules(models_pkg.__path__):
    importlib.import_module("app.models." + m.name)

from app.models.barber_model import Barber  # noqa: E402
from app.models.barber_schedule_model import BarberSchedule  # noqa: E402
from app.models.barbershop_model import Barbershop  # noqa: E402
from app.models.barbershop_schedule_model import BarbershopSchedule  # noqa: E402
from app.models.booking_status_model import BookingStatus  # noqa: E402
from app.models.role_model import Role  # noqa: E402
from app.models.service_model import Service  # noqa: E402
from app.models.user_model import User  # noqa: E402

OK, BAD = "[OK]", "[FALLO]"


def step(msg):
    print(f"\n== {msg}")


# ---------------------------------------------------------------- esquema
step("1. Esquema legado + migración")
with engine.begin() as c:
    c.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    for t in ("email_verifications", "barbershop_payment_methods"):
        c.execute(text(f"DROP TABLE IF EXISTS {t}"))
    Base.metadata.drop_all(c)
    c.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

Base.metadata.create_all(engine)

# Dejamos las tablas como estaban ANTES de esta funcionalidad.
with engine.begin() as c:
    c.execute(text("ALTER TABLE bookings DROP INDEX manage_token"))
    for col in BOOKING_COLUMNS:
        c.execute(text(f"ALTER TABLE bookings DROP COLUMN {col}"))
    for col in BARBERSHOP_COLUMNS:
        c.execute(text(f"ALTER TABLE barbershops DROP COLUMN {col}"))
    c.execute(text("ALTER TABLE bookings MODIFY client_user_id INT UNSIGNED NOT NULL"))

legacy_cols = {c["name"] for c in inspect(engine).get_columns("bookings")}
assert "guest_email" not in legacy_cols and "payment_method" not in legacy_cols
print(f"{OK} esquema legado listo (bookings sin columnas nuevas, client_user_id NOT NULL)")

changes = ensure_schema(engine)
print(f"{OK} migración aplicó {len(changes)} cambios")

cols = {c["name"]: c for c in inspect(engine).get_columns("bookings")}
for name in BOOKING_COLUMNS:
    assert name in cols, f"falta bookings.{name}"
assert cols["client_user_id"]["nullable"], "client_user_id sigue NOT NULL"
bs_cols = {c["name"] for c in inspect(engine).get_columns("barbershops")}
for name in BARBERSHOP_COLUMNS:
    assert name in bs_cols, f"falta barbershops.{name}"
tables = set(inspect(engine).get_table_names())
assert {"email_verifications", "barbershop_payment_methods"} <= tables
print(f"{OK} columnas, nullability y tablas nuevas verificadas")

again = ensure_schema(engine)
assert again == [], f"no es idempotente: {again}"
print(f"{OK} segunda ejecución: sin cambios (idempotente)")

# La tabla barbershop_settings existe en la base real pero no en los modelos ORM
# (la consultan los endpoints de configuración con SQL directo).
from app.db.init_schema import BARBERSHOP_SETTINGS_DDL  # noqa: E402

with engine.begin() as c:
    c.execute(text("DROP TABLE IF EXISTS barbershop_settings"))
    c.execute(text(BARBERSHOP_SETTINGS_DDL))
    c.execute(text("INSERT INTO barbershop_settings (barbershop_id) VALUES (1)"))
print(f"{OK} tabla barbershop_settings (ajustes de la barbería) creada")

# ------------------------------------------------------------------ datos
step("2. Datos de prueba")
db = SessionLocal()

roles = {n: Role(name=n) for n in ("CLIENT", "BARBER", "BARBERSHOP_ADMIN", "PLATFORM_ADMIN")}
db.add_all(roles.values())

statuses = {}
for code in ("PENDING", "CONFIRMED", "IN_PROGRESS", "COMPLETED", "REJECTED",
             "CANCELLED_BY_CUSTOMER", "CANCELLED_BY_BARBER", "CANCELLED_BY_ADMIN", "NO_SHOW"):
    s = BookingStatus(code=code, name=code.replace("_", " ").title())
    statuses[code] = s
    db.add(s)
db.flush()


def user(first, last, email, role):
    u = User(first_name=first, last_name=last, email=email,
             password_hash=hash_password(env.PASSWORD), phone="3001112233", is_active=True)
    u.roles.append(roles[role])
    db.add(u)
    db.flush()
    return u


admin = user("Ada", "Admin", "admin@test.co", "PLATFORM_ADMIN")
owner = user("Olga", "Dueña", "owner@test.co", "BARBERSHOP_ADMIN")
barber_user = user("Beto", "Barbero", "barber@test.co", "BARBER")
client = user("Carla", "Cliente", "client@test.co", "CLIENT")

shop = Barbershop(
    owner_user_id=owner.id, name="Test Barber Club", address="Calle 84 # 50-20",
    neighborhood="Alto Prado", city="Barranquilla", department="Atlántico",
    latitude=10.9685, longitude=-74.7813, phone="3005550000", email="shop@test.co",
    cancellation_hours_before=2, requires_manual_confirmation=False, is_active=True,
)
db.add(shop)
db.flush()

cut = Service(barbershop_id=shop.id, name="Corte clásico", price=25000, duration_minutes=30,
              home_service_allowed=True, is_active=True)
beard = Service(barbershop_id=shop.id, name="Barba", price=15000, duration_minutes=20,
                home_service_allowed=False, is_active=True)
db.add_all([cut, beard])
db.flush()

barber = Barber(user_id=barber_user.id, barbershop_id=shop.id, accepts_home_service=True, is_active=True)
barber.services = [cut, beard] if hasattr(Barber, "services") else []
db.add(barber)
db.flush()

if not getattr(barber, "services", None):
    db.execute(text("INSERT INTO barber_services (barber_id, service_id) VALUES (:b,:s1),(:b,:s2)"),
               {"b": barber.id, "s1": cut.id, "s2": beard.id})

for dow in range(1, 8):
    db.add(BarbershopSchedule(barbershop_id=shop.id, day_of_week=dow,
                              open_time=time(8, 0), close_time=time(20, 0), is_open=True))
    db.add(BarberSchedule(barber_id=barber.id, day_of_week=dow,
                          start_time=time(8, 0), end_time=time(20, 0), is_working=True))

db.execute(text("INSERT INTO barbershop_admins (user_id, barbershop_id) VALUES (:u,:s)"),
           {"u": owner.id, "s": shop.id}) if "barbershop_admins" in inspect(engine).get_table_names() else None

db.commit()

ids = {
    "admin": admin.id, "owner": owner.id, "barber_user": barber_user.id, "client": client.id,
    "shop": shop.id, "barber": barber.id, "cut": cut.id, "beard": beard.id,
}
Path(__file__).with_name("ids.json").write_text(json.dumps(ids, indent=2))
print(f"{OK} datos cargados:", ids)
db.close()
