"""
Recordatorios por correo de citas confirmadas:

  * 24 h antes (solo si la cita se creó con más de 25 h de anticipación)
  * 2 h antes  (solo si la cita se creó con más de 2 h 30 min de anticipación)

Se ejecuta como tarea en segundo plano cada 5 minutos.
"""

import asyncio
from datetime import datetime, timedelta

from sqlalchemy import text

from app.db.session import SessionLocal
from app.services.notification_service import NotificationService

INTERVAL_SECONDS = 300


def run_once() -> int:
    now = datetime.now()
    sent = 0
    db = SessionLocal()
    try:
        for column, kind, lower, upper, min_lead_minutes in (
            ("reminder_24h_sent_at", "REMINDER_24H", now + timedelta(hours=2, minutes=30), now + timedelta(hours=24), 25 * 60),
            ("reminder_2h_sent_at", "REMINDER_2H", now, now + timedelta(hours=2), 150),
        ):
            rows = db.execute(text(f"""
                SELECT b.id
                FROM bookings b
                JOIN booking_statuses st ON st.id = b.status_id
                WHERE st.code = 'CONFIRMED'
                  AND b.{column} IS NULL
                  AND b.start_at > :lower AND b.start_at <= :upper
                  AND TIMESTAMPDIFF(MINUTE, b.created_at, b.start_at) >= :lead
                LIMIT 200
            """), {"lower": lower, "upper": upper, "lead": min_lead_minutes}).fetchall()

            for (booking_id,) in rows:
                # Se marca primero: si el envío falla no se reintenta en bucle.
                db.execute(text(f"UPDATE bookings SET {column} = :now WHERE id = :id"),
                           {"now": now, "id": booking_id})
                db.commit()
                NotificationService.booking_event(db, booking_id, kind)
                sent += 1
    except Exception as error:
        db.rollback()
        print("ERROR RECORDATORIOS:", repr(error))
    finally:
        db.close()
    return sent


async def reminder_loop() -> None:
    # Pequeña espera para no competir con el arranque.
    await asyncio.sleep(20)
    while True:
        try:
            await asyncio.to_thread(run_once)
        except Exception as error:
            print("ERROR EN BUCLE DE RECORDATORIOS:", repr(error))
        await asyncio.sleep(INTERVAL_SECONDS)
