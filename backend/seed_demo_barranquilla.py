"""
Datos de EJEMPLO: barberías ficticias en Barranquilla (con barberos, servicios, horarios y descansos).

  * Los nombres son inventados. No llevan teléfonos ni correos reales.
  * Las coordenadas son aproximadas (barrios de Barranquilla con un pequeño desplazamiento aleatorio).
  * Los barberos son usuarios de demostración con una clave aleatoria que nadie conoce (no se puede iniciar sesión con ellos).
  * Todas las barberías pertenecen al usuario administrador que indiques con --owner-email.
  * Es idempotente: si una barbería con el mismo nombre ya existe, se omite.

Uso (desde la carpeta backend, con la base elegida por DATABASE_URL o DB_*):
    .venv/Scripts/python seed_demo_barranquilla.py --owner-email admin@tu-dominio.com --count 10
"""

import argparse
import importlib
import json
import pkgutil
import random
import secrets
import sys
from datetime import datetime, time

from sqlalchemy import text

import app.models as models_pkg
from app.core.security import hash_password
from app.db.session import SessionLocal, engine

for module in pkgutil.iter_modules(models_pkg.__path__):
    importlib.import_module(f"app.models.{module.name}")

from app.models.barber_model import Barber  # noqa: E402
from app.models.barber_schedule_model import BarberSchedule  # noqa: E402
from app.models.barbershop_break_model import BarbershopBreak  # noqa: E402
from app.models.barbershop_model import Barbershop  # noqa: E402
from app.models.barbershop_schedule_model import BarbershopSchedule  # noqa: E402
from app.models.role_model import Role  # noqa: E402
from app.models.service_model import Service  # noqa: E402
from app.models.user_model import User  # noqa: E402

parser = argparse.ArgumentParser(description="Barberías de ejemplo en Barranquilla")
parser.add_argument("--owner-email", required=True, help="correo de un usuario existente (será el dueño de todas)")
parser.add_argument("--count", type=int, default=8, help="cuántas barberías crear (máx. 14)")
parser.add_argument("--seed", type=int, default=None, help="semilla aleatoria para repetir el mismo resultado")
args = parser.parse_args()

rng = random.Random(args.seed)

# (barrio, latitud, longitud) aproximadas del centro del barrio
NEIGHBORHOODS = [
    ("Alto Prado", 10.9965, -74.8060), ("El Prado", 10.9905, -74.7985), ("Riomar", 11.0105, -74.8250),
    ("Villa Country", 11.0035, -74.8165), ("Ciudad Jardín", 10.9835, -74.8135), ("Boston", 10.9870, -74.7885),
    ("Paraíso", 10.9885, -74.8215), ("Villa Santos", 11.0000, -74.8090), ("Las Delicias", 10.9770, -74.8040),
    ("La Concepción", 10.9930, -74.8180), ("Granadillo", 10.9990, -74.8110), ("El Golf", 11.0075, -74.8110),
    ("Altos del Limón", 10.9700, -74.8190), ("Nuevo Horizonte", 10.9650, -74.8060),
]

NAMES = [
    "Corte & Navaja Costeña", "La Arenosa Barber Club", "Sabana Fade Studio", "Costa Barber House",
    "Malecón Cut Lab", "Don Gato Barbería", "El Rey del Fade", "Cumbia Barber Shop", "Gran Carnaval Barbers",
    "Barbería Puerta de Oro", "Caribe Fino Barbers", "Navaja de Plata", "El Hueco Barber Lab", "Brisa del Río Barbería",
]

SERVICES = [  # nombre, (precio mín, precio máx), minutos, vip, permite domicilio
    ("Corte clásico", (20000, 30000), 30, False, True),
    ("Corte fade", (25000, 38000), 40, False, True),
    ("Barba", (12000, 20000), 20, False, True),
    ("Corte + barba", (35000, 50000), 50, False, True),
    ("Perfilado de cejas", (8000, 12000), 15, False, False),
    ("Corte infantil", (18000, 25000), 30, False, False),
    ("Tratamiento capilar", (30000, 55000), 45, True, False),
    ("Afeitado con toalla caliente", (25000, 35000), 30, True, False),
]

FIRST = ["Andrés", "Camilo", "Carlos", "David", "Éver", "Fabián", "Jorge", "Julián", "Luis", "Mateo", "Nicolás", "Óscar", "Sebastián", "Yeison"]
LAST = ["Acosta", "Barraza", "Caro", "De la Hoz", "Escorcia", "Fontalvo", "Gutiérrez", "Herrera", "Mendoza", "Ortega", "Pacheco", "Rojas", "Sarmiento", "Vargas"]
BIOS = [
    "Especialista en degradados y cortes modernos.", "Barbero clásico: navaja, toalla caliente y detalle.",
    "Cortes para toda la familia con atención personalizada.", "Fan del fade y del perfilado de barba.",
]
STREETS = ["Carrera", "Calle"]


def slug(value: str) -> str:
    table = str.maketrans("áéíóúñÁÉÍÓÚÑ&", "aeiounaeioun-")
    return "".join(c if c.isalnum() else "-" for c in value.translate(table).lower()).strip("-")[:40]


def address() -> str:
    street = rng.choice(STREETS)
    return f"{street} {rng.randint(43, 59)} # {rng.randint(70, 98)}-{rng.randint(10, 99)}"


db = SessionLocal()
owner = db.query(User).filter(User.email == args.owner_email.strip().lower()).first()
if not owner:
    sys.exit(f"[FALLO] no existe el usuario {args.owner_email}: créalo antes (init_db.py --admin-email ...)")

barber_role = db.query(Role).filter(Role.name == "BARBER").first()
if not barber_role:
    sys.exit("[FALLO] faltan los roles base: ejecuta antes init_db.py")

count = max(1, min(args.count, len(NAMES)))
names = rng.sample(NAMES, count)
hoods = rng.sample(NEIGHBORHOODS, min(count, len(NEIGHBORHOODS)))
created = skipped = 0

for index, name in enumerate(names):
    if db.query(Barbershop).filter(Barbershop.name == name).first():
        print(f"  [omitida] {name}: ya existe")
        skipped += 1
        continue

    hood, lat, lng = hoods[index % len(hoods)]
    with_home = index < 2          # las dos primeras ya ofrecen domicilio (aprobado)
    chosen = rng.sample(SERVICES, rng.randint(5, 7))
    # siempre incluimos el corte clásico
    if not any(s[0] == "Corte clásico" for s in chosen):
        chosen[0] = SERVICES[0]
    has_vip = any(s[3] for s in chosen)

    shop = Barbershop(
        owner_user_id=owner.id,
        name=name,
        description=f"Barbería en {hood}, Barranquilla. Cortes, barba y cuidado personal con barberos con experiencia.",
        address=address(),
        neighborhood=hood,
        city="Barranquilla",
        department="Atlántico",
        latitude=round(lat + rng.uniform(-0.004, 0.004), 7),
        longitude=round(lng + rng.uniform(-0.004, 0.004), 7),
        phone=None,
        email=None,
        only_men=rng.random() < 0.3,
        offers_vip=has_vip,
        offers_home_service=with_home,
        requires_manual_confirmation=rng.random() < 0.2,
        cancellation_hours_before=rng.choice([1, 2, 4]),
        tolerance_minutes=10,
        is_active=True,
    )
    if with_home:
        shop.home_service_status = "APPROVED"
        shop.home_service_radius_km = 8
        shop.home_service_fee = 8000
        shop.home_service_min_notice_hours = 3
        shop.home_service_zones = f"{hood}, " + ", ".join(h[0] for h in rng.sample(NEIGHBORHOODS, 2))
        shop.home_service_requirements = json.dumps(
            {"hygiene_kit": True, "barbers_verified": True, "accepts_policy": True, "notes": "Datos de ejemplo"},
            ensure_ascii=False,
        )
        shop.home_service_requested_at = datetime.now()
        shop.home_service_reviewed_at = datetime.now()
    db.add(shop)
    db.flush()

    # servicios
    services = []
    for s_name, (lo, hi), minutes, vip, home_ok in chosen:
        price = round(rng.randint(lo, hi) / 500) * 500
        svc = Service(
            barbershop_id=shop.id, name=s_name, price=price, duration_minutes=minutes,
            is_vip=vip, home_service_allowed=home_ok and with_home, is_active=True,
        )
        db.add(svc)
        services.append(svc)
    db.flush()

    # horarios de la barbería
    opens_sunday = rng.random() < 0.3
    open_t, close_t = rng.choice([(time(8, 0), time(19, 0)), (time(9, 0), time(20, 0)), (time(8, 30), time(19, 30))])
    for dow in range(1, 8):
        if dow <= 5:
            hours = (open_t, close_t)
        elif dow == 6:
            hours = (open_t, time(18, 0))
        else:
            hours = (time(9, 0), time(14, 0)) if opens_sunday else None
        db.add(BarbershopSchedule(
            barbershop_id=shop.id, day_of_week=dow,
            open_time=hours[0] if hours else None, close_time=hours[1] if hours else None, is_open=bool(hours),
        ))
        if hours and dow <= 6 and index % 5 != 0:
            db.add(BarbershopBreak(
                barbershop_id=shop.id, day_of_week=dow, start_time=time(12, 30), end_time=time(13, 30),
                name="Almuerzo", is_active=True,
            ))

    # barberos
    for n in range(rng.randint(2, 3)):
        first, last = rng.choice(FIRST), rng.choice(LAST)
        user = User(
            first_name=first, last_name=last,
            email=f"barbero.{slug(name)}.{n + 1}@demo.barbergo.invalid",
            password_hash=hash_password(secrets.token_urlsafe(32)),   # clave aleatoria que nadie conoce
            is_active=True,
        )
        user.roles.append(barber_role)
        db.add(user)
        db.flush()

        barber = Barber(
            user_id=user.id, barbershop_id=shop.id, bio=rng.choice(BIOS),
            years_experience=rng.randint(2, 15), accepts_home_service=with_home, is_active=True,
        )
        db.add(barber)
        db.flush()

        for svc in services:
            db.execute(text("INSERT INTO barber_services (barber_id, service_id) VALUES (:b, :s)"), {"b": barber.id, "s": svc.id})

        for dow in range(1, 8):
            works = dow <= 6 or opens_sunday
            if dow <= 5:
                hours = (open_t, close_t)
            elif dow == 6:
                hours = (open_t, time(18, 0))
            else:
                hours = (time(9, 0), time(14, 0))
            db.add(BarberSchedule(
                barber_id=barber.id, day_of_week=dow,
                start_time=hours[0] if works else None, end_time=hours[1] if works else None, is_working=works,
            ))

    # ajustes por defecto y pago en efectivo
    db.execute(text("INSERT INTO barbershop_settings (barbershop_id) VALUES (:s)"), {"s": shop.id})
    db.execute(
        text("INSERT INTO barbershop_payment_methods (barbershop_id, method, is_active) VALUES (:s, 'CASH', :a)"),
        {"s": shop.id, "a": True},
    )

    db.commit()
    created += 1
    print(f"  [creada]  {name} ({hood}) · {len(services)} servicios{' · domicilio' if with_home else ''}")

print(f"\nListo: {created} barberías creadas, {skipped} omitidas.")
