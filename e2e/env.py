"""
Entorno de pruebas e2e: apunta el backend a una base de datos descartable.

Se elige con la variable E2E_DB (por defecto mysql):

    E2E_DB=mysql      docker run -d --name barbergo-test-db -e MYSQL_ROOT_PASSWORD=test \
                          -e MYSQL_DATABASE=barbergo_test -p 3399:3306 mysql:8.0 \
                          --character-set-server=utf8mb4 --default-time-zone=-05:00

    E2E_DB=postgres   docker run -d --name barbergo-test-pg -e POSTGRES_PASSWORD=test \
                          -e POSTGRES_DB=barbergo_test -p 3398:5432 postgres:16
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

E2E_DB = os.getenv("E2E_DB", "mysql").lower()

DB_MYSQL = {
    "DATABASE_URL": "",
    "DB_HOST": "127.0.0.1",
    "DB_PORT": "3399",
    "DB_USER": "root",
    "DB_PASSWORD": "test",
    "DB_NAME": "barbergo_test",
}

DB_POSTGRES = {
    "DATABASE_URL": "postgresql://postgres:test@127.0.0.1:3398/barbergo_test",
}

DB_ENV = DB_POSTGRES if E2E_DB.startswith("postgres") else DB_MYSQL

TEST_ENV = {
    **DB_ENV,
    "JWT_SECRET_KEY": "e2e-secret-key-not-for-production-0123456789",
    "RESEND_API_KEY": "",          # sin proveedor: los correos se imprimen en consola
    "SMTP_HOST": "",               # IMPORTANTE: evita enviar correos reales desde las pruebas
    "FRONTEND_URL": "http://localhost:4200",
    "ADMIN_NOTIFY_EMAIL": "plataforma@test.co",
}

API = "http://127.0.0.1:8000/api/v1"
PASSWORD = "Password123!"


def apply() -> None:
    os.environ.update(TEST_ENV)
    backend = str(ROOT / "backend")
    if backend not in sys.path:
        sys.path.insert(0, backend)
    os.chdir(backend)
