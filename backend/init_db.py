"""
Prepara una base de datos nueva (por ejemplo, la de la nube).

Lee la conexión de backend/.env (o de variables de entorno: DB_HOST, DB_PORT, DB_USER,
DB_PASSWORD, DB_NAME y, si tu proveedor lo exige, DB_SSL=true).

Uso (desde la carpeta backend):
    .venv/Scripts/python init_db.py
    .venv/Scripts/python init_db.py --admin-email tu@correo.com --admin-password "UnaClaveSegura123"
"""

import argparse
import sys

from app.db.init_schema import create_platform_admin, init_schema
from app.db.session import DATABASE_URL, engine

parser = argparse.ArgumentParser(description="Inicializa la base de datos de BarberGo")
parser.add_argument("--admin-email", help="crea (o promueve) un administrador de la plataforma")
parser.add_argument("--admin-password", help="clave del administrador (mínimo 8 caracteres)")
args = parser.parse_args()

print(f"Base de datos: {DATABASE_URL.host}:{DATABASE_URL.port}/{DATABASE_URL.database}")

try:
    for line in init_schema(engine):
        print("  [OK]", line)
    if args.admin_email:
        if not args.admin_password or len(args.admin_password) < 8:
            sys.exit("  [FALLO] --admin-password es obligatorio y debe tener al menos 8 caracteres")
        print("  [OK]", create_platform_admin(engine, args.admin_email.strip().lower(), args.admin_password))
except Exception as error:  # noqa: BLE001
    sys.exit(f"  [FALLO] {error!r}")

print("Listo.")
