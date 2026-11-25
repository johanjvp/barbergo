# Pruebas e2e de BarberGo

Prueban, contra servicios reales, las funciones de **reserva sin cuenta**, **servicio a domicilio**,
**pago directo** y **correos** (códigos, confirmaciones, cancelaciones, recordatorios).

| Archivo | Qué hace |
|---|---|
| `db_setup.py` | Crea un esquema "antiguo", comprueba que la migración lo actualiza (y es idempotente) y carga datos de prueba |
| `test_api.py` | 80 pruebas de API (backend real + MySQL real) |
| `test_ui.py`  | 61 pruebas de interfaz con Chromium (Playwright): invitado, domicilio con mapa, pagos, calendario, paneles, móvil, modo oscuro |
| `test_parity.py` | carga los mismos datos en MySQL y PostgreSQL y compara las respuestas de todos los endpoints de lectura (incluido el panel de administración) |
| `run_all.py` | lanza todo lo anterior en las dos bases |
| `test_smtp.py` | envío de correo por SMTP contra un servidor falso local |
| `test_vercel_sim.py` | simula el despliegue en Vercel (api/index.py con `VERCEL=1`, frontend compilado y reglas de `vercel.json`) |
| `audit_contrast.py` | auditoría de contraste WCAG por pantalla, en claro u oscuro (`python e2e/audit_contrast.py dark admin@test.co /admin`) |

## Preparación

```bash
# 1) Bases descartables (no tocan tu base real). MySQL en el 3399 y PostgreSQL en el 3398
docker run -d --name barbergo-test-db -e MYSQL_ROOT_PASSWORD=test -e MYSQL_DATABASE=barbergo_test \
  -p 3399:3306 mysql:8.0 --character-set-server=utf8mb4 --default-time-zone=-05:00
docker run -d --name barbergo-test-pg -e POSTGRES_PASSWORD=test -e POSTGRES_DB=barbergo_test -p 3398:5432 postgres:16

# 2) Backend apuntando a esa base. RESEND_API_KEY= y SMTP_HOST= (vacíos) hacen que los correos se
#    impriman en el log en vez de enviarse de verdad (si no, las pruebas escribirían a correos falsos)
cd backend
RATE_LIMIT_MULTIPLIER=100 DB_PORT=3399 DB_PASSWORD=test DB_NAME=barbergo_test \
JWT_SECRET_KEY=e2e-secret-key-not-for-production-0123456789 RESEND_API_KEY= SMTP_HOST= \
FRONTEND_URL=http://localhost:4200 ADMIN_NOTIFY_EMAIL=plataforma@test.co PYTHONIOENCODING=utf-8 \
.venv/Scripts/python -m uvicorn app.main:app --port 8000 > ../e2e/backend.log 2>&1 &

# 3) Frontend
cd ../frontend && npm start
```

## Todo de una vez (MySQL y PostgreSQL)

```bash
python e2e/run_all.py     # arranca/para el backend solo; el frontend debe estar en :4200
```

Corre API, interfaz y simulación de Vercel en **las dos bases**, la paridad de respuestas MySQL <-> PostgreSQL y el SMTP.

## Ejecución por partes (elige la base con `E2E_DB=mysql|postgres`)

```bash
backend/.venv/Scripts/python e2e/db_setup.py     # reinicia datos (repetir antes de cada corrida de UI)
backend/.venv/Scripts/python e2e/test_api.py
python e2e/test_ui.py                            # Python del sistema con `pip install playwright`
```

Capturas de la corrida de UI: `e2e/out/`. Usuarios de prueba (clave `Password123!`):
`admin@test.co` (plataforma), `owner@test.co` (dueño), `barber@test.co`, `client@test.co`.
