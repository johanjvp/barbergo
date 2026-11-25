"""
Tareas programadas disparadas desde fuera (Vercel Cron, GitHub Actions, cron-job.org...).

En un servidor tradicional los recordatorios corren en un bucle interno. En Vercel no hay
procesos permanentes, así que un programador externo llama a este endpoint cada ~5-10 min:

    curl -H "Authorization: Bearer $CRON_SECRET" https://tu-sitio.vercel.app/api/v1/cron/reminders

Requiere la variable de entorno CRON_SECRET (si no existe, el endpoint queda deshabilitado).
"""

import os
import secrets

from fastapi import APIRouter, Header, HTTPException, status

from app.services.reminder_service import run_once

router = APIRouter(prefix="/cron", tags=["Tareas programadas"])


def _authorize(authorization: str | None) -> None:
    expected = os.getenv("CRON_SECRET")

    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Las tareas programadas no están habilitadas (falta CRON_SECRET).",
        )

    supplied = (authorization or "").removeprefix("Bearer ").strip()

    if not secrets.compare_digest(supplied.encode(), expected.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado.")


@router.api_route("/reminders", methods=["GET", "POST"])
def send_reminders(authorization: str | None = Header(default=None)):
    _authorize(authorization)
    return {"sent": run_once()}
