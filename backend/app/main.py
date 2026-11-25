import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.api_router import api_router

# Registra los oyentes que envían correo al cambiar el estado de una reserva.
import app.services.booking_events  # noqa: F401


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # 1) Esquema: añade columnas/tablas nuevas si faltan (idempotente).
    try:
        from app.db.migrations import ensure_schema
        from app.db.session import engine

        changes = await asyncio.to_thread(ensure_schema, engine)
        if changes:
            print("MIGRACIONES APLICADAS:", ", ".join(changes))
    except Exception as error:
        # La API arranca igual; las funciones nuevas fallarán hasta que la BD responda.
        print("AVISO: no se pudo verificar el esquema de la BD:", repr(error))

    # 2) Recordatorios de citas por correo.
    #    En Vercel (serverless) no existen procesos permanentes: los recordatorios se
    #    disparan llamando a /api/v1/cron/reminders (ver DEPLOY_VERCEL.md).
    if os.getenv("VERCEL"):
        yield
        return

    from app.services.reminder_service import reminder_loop

    task = asyncio.create_task(reminder_loop())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(
    title=settings.APP_NAME,
    version="0.2.0",
    description=(
        "API para la plataforma "
        "de reservas de barberías."
    ),
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(
    api_router,
    prefix="/api/v1"
)


@app.get("/")
def root():
    return {
        "application": settings.APP_NAME,
        "status": "online",
        "api_version": "v1",
        "docs": "/docs"
    }
