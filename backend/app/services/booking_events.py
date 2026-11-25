"""
Envía un correo cada vez que cambia el estado de una reserva,
sin importar desde dónde se cambió (cliente, barbero, administrador,
invitado por enlace...).

Se engancha a SQLAlchemy:
  * after_flush  -> detecta reservas cuyo status_id cambió
  * after_commit -> con la transacción ya confirmada, notifica en un hilo
                    con su propia sesión (nunca bloquea ni rompe la petición)

Importar este módulo una vez al arrancar la aplicación.
"""

import os
import threading

from sqlalchemy import event, inspect, text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.booking_model import Booking
from app.services.notification_service import NotificationService

_KEY = "booking_status_changed_ids"


def _event_for(code: str) -> str | None:
    if code == "CONFIRMED":
        return "CONFIRMED"
    if code == "REJECTED":
        return "REJECTED"
    if code.startswith("CANCELLED"):
        return "CANCELLED"
    return None


def _notify(booking_ids: list[int]) -> None:
    db = SessionLocal()
    try:
        for booking_id in booking_ids:
            code = db.execute(text("""
                SELECT st.code FROM bookings b
                JOIN booking_statuses st ON st.id = b.status_id
                WHERE b.id = :id
            """), {"id": booking_id}).scalar()
            kind = _event_for(code or "")
            if kind:
                NotificationService.booking_event(db, booking_id, kind)
    except Exception as error:
        print("ERROR NOTIFICANDO CAMBIO DE ESTADO:", repr(error))
    finally:
        db.close()


@event.listens_for(Session, "after_flush")
def _collect(session: Session, _ctx) -> None:
    for obj in session.dirty:
        if isinstance(obj, Booking) and inspect(obj).attrs.status_id.history.has_changes():
            session.info.setdefault(_KEY, set()).add(obj.id)


@event.listens_for(Session, "after_commit")
def _after_commit(session: Session) -> None:
    ids = session.info.pop(_KEY, None)
    if not ids:
        return

    if os.getenv("VERCEL"):
        _notify(sorted(ids))   # serverless: se envía antes de responder
    else:
        threading.Thread(target=_notify, args=(sorted(ids),), daemon=True).start()


@event.listens_for(Session, "after_rollback")
def _after_rollback(session: Session) -> None:
    session.info.pop(_KEY, None)
