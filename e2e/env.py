"""
Entorno de pruebas e2e: apunta el backend a un MySQL descartable.

    docker run -d --name barbergo-test-db -e MYSQL_ROOT_PASSWORD=test \
        -e MYSQL_DATABASE=barbergo_test -p 3399:3306 mysql:8.0 \
        --character-set-server=utf8mb4 --default-time-zone=-05:00
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TEST_ENV = {
    "DB_HOST": "127.0.0.1",
    "DB_PORT": "3399",
    "DB_USER": "root",
    "DB_PASSWORD": "test",
    "DB_NAME": "barbergo_test",
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
