"""
Pruebas e2e de la API contra el backend real y un MySQL real.

Requisitos: backend en :8000 apuntando a la base de pruebas, e2e/db_setup.py ejecutado.
Los correos se leen del log del backend (sin RESEND_API_KEY se imprimen como [EMAIL-DEV]).

Uso:  backend/.venv/Scripts/python e2e/test_api.py
"""

import json
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import env  # noqa: E402

env.apply()

import httpx  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402

API = env.API
LOG = Path(__file__).with_name("backend.log")
IDS = json.loads(Path(__file__).with_name("ids.json").read_text())
http = httpx.Client(base_url=API, timeout=30)

passed, failed = [], []


def check(name: str, cond: bool, detail: str = ""):
    (passed if cond else failed).append(name)
    print(("  [OK]    " if cond else "  [FALLO] ") + name + (f"  -> {detail}" if detail and not cond else ""))


def section(title: str):
    print(f"\n== {title}")


def login(email: str) -> dict:
    r = http.post("/auth/login", json={"email": email, "password": env.PASSWORD})
    assert r.status_code == 200, f"login {email}: {r.status_code} {r.text}"
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def log_text() -> str:
    time.sleep(0.8)  # los correos se envían en hilos
    return LOG.read_text(encoding="utf-8", errors="replace")


def last_code(email: str) -> str:
    """Último código [EMAIL-DEV] impreso para ese correo."""
    text_ = log_text()
    blocks = re.split(r"(?=\[EMAIL-DEV\] Para: )", text_)
    for b in reversed(blocks):
        if f"Para: {email}" in b:
            m = re.search(r"código: (\d{6})", b)
            if m:
                return m.group(1)
    raise AssertionError("no hay código para " + email)


def emails_to(email: str) -> str:
    return "\n".join(b for b in re.split(r"(?=\[EMAIL-DEV\] Para: )", log_text()) if f"Para: {email}" in b)


_slot = [0]


def slot(days=3, hour=10, minute=0) -> str:
    """Hueco futuro único dentro de la jornada (08:00-15:30), sin repetirse entre llamadas."""
    i = _slot[0]
    _slot[0] += 1
    d = datetime.now() + timedelta(days=3 + i // 16)
    d = d.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(minutes=30 * (i % 16))
    return d.strftime("%Y-%m-%dT%H:%M:%S")


def guest_body(email, start, code, **extra):
    body = {
        "barber_id": IDS["barber"], "service_id": IDS["cut"], "start_at": start,
        "customer_notes": None, "name": "Gina Invitada", "email": email,
        "phone": "3001234567", "code": code, "accept_terms": True,
    }
    body.update(extra)
    return body


def guest_book(email, start, **extra):
    http.post("/guest/verification-code", json={"email": email})
    code = last_code(email)
    return http.post("/guest/bookings", json=guest_body(email, start, code, **extra))


# =====================================================================
section("A. Reserva sin cuenta (invitado)")
# =====================================================================
email = "invitada@test.co"
r = http.post("/guest/verification-code", json={"email": email})
check("solicitar código -> 200", r.status_code == 200 and r.json()["expires_in_minutes"] == 10, r.text)
code = last_code(email)
check("el código llega por correo (6 dígitos)", len(code) == 6)

start = slot(3, 10)
r = http.post("/guest/bookings", json=guest_body(email, start, "000000" if code != "000000" else "111111"))
check("código incorrecto -> 400", r.status_code == 400, r.text)

r = http.post("/guest/bookings", json=guest_body(email, start, code, accept_terms=False))
check("sin aceptar datos -> 422", r.status_code == 422, r.text)

r = http.post("/guest/bookings", json=guest_body(email, start, "12ab56"))
check("código con formato inválido -> 422", r.status_code == 422, r.text)

r = http.post("/guest/bookings", json=guest_body(email, start, code))
check("reserva de invitado -> 201", r.status_code == 201, r.text)
g = r.json() if r.status_code == 201 else {}
token = g.get("manage_token", "")
check("estado CONFIRMED (la barbería no pide confirmación manual)", g.get("status_code") == "CONFIRMED", str(g.get("status_code")))
check("sin client_user_id y con guest_email", g.get("client_user_id") is None and g.get("guest_email") == email)
check("token de gestión largo", len(token) >= 40)

r = http.post("/guest/bookings", json=guest_body(email, slot(3, 12), code))
check("el código ya usado no sirve de nuevo -> 400", r.status_code == 400, r.text)

mail = emails_to(email)
check("correo de confirmación enviado", "Tu reserva está confirmada" in mail, mail[:200])
check("el correo trae el enlace /reserva/<token>", f"/reserva/{token}" in mail)

r = http.get(f"/guest/bookings/{token}")
v = r.json() if r.status_code == 200 else {}
check("consultar por token -> 200", r.status_code == 200, r.text)
check("puede cancelar y trae datos de la barbería", v.get("can_cancel") is True and v.get("barbershop_name") == "Test Barber Club")
check("token inválido -> 404", http.get("/guest/bookings/" + "x" * 43).status_code == 404)

r = guest_book("otra@test.co", start)
check("mismo horario ocupado -> 409", r.status_code == 409, r.text)

r = http.post(f"/guest/bookings/{token}/cancel")
check("cancelar por enlace -> 200", r.status_code == 200 and r.json()["status_code"] == "CANCELLED_BY_CUSTOMER", r.text)
check("correo de cancelación enviado", "Tu reserva fue cancelada" in emails_to(email))
check("cancelar dos veces -> 409", http.post(f"/guest/bookings/{token}/cancel").status_code == 409)

r = guest_book("otra@test.co", start)
check("el horario cancelado queda libre de nuevo", r.status_code == 201, r.text)

rl = "limite@test.co"
codes = [http.post("/guest/verification-code", json={"email": rl}).status_code for _ in range(4)]
check("límite de 3 códigos por correo (4.º -> 429)", codes == [200, 200, 200, 429], str(codes))

dbs = SessionLocal()
dbs.execute(text("UPDATE barbershop_settings SET require_customer_account = 1 WHERE barbershop_id = :s"), {"s": IDS["shop"]})
dbs.commit()
r = guest_book("exigecuenta@test.co", slot(3, 10))
check("si la barbería exige cuenta, el invitado recibe 403", r.status_code == 403 and "cuenta" in r.text, r.text)
dbs.execute(text("UPDATE barbershop_settings SET require_customer_account = 0, bookings_enabled = 0 WHERE barbershop_id = :s"), {"s": IDS["shop"]})
dbs.commit()
r = guest_book("sinreservas@test.co", slot(3, 10))
check("si la barbería pausó las reservas, el invitado recibe 409", r.status_code == 409, r.text)
dbs.execute(text("UPDATE barbershop_settings SET bookings_enabled = 1 WHERE barbershop_id = :s"), {"s": IDS["shop"]})
dbs.commit()
dbs.close()

# =====================================================================
section("B. Pago directo")
# =====================================================================
owner = login("owner@test.co")
client_h = login("client@test.co")

r = http.put(f"/barbershop-settings/{IDS['shop']}/payment-methods", headers=owner,
             json={"methods": [{"method": "NEQUI", "account_number": "123", "account_holder": "X"}]})
check("Nequi con número inválido -> 422", r.status_code == 422, r.text)

r = http.put(f"/barbershop-settings/{IDS['shop']}/payment-methods", headers=client_h,
             json={"methods": [{"method": "CASH"}]})
check("un cliente no puede configurar pagos -> 403", r.status_code in (401, 403), str(r.status_code))

methods = {"methods": [
    {"method": "CASH"},
    {"method": "NEQUI", "account_number": "3001234567", "account_holder": "Olga Dueña", "instructions": "Envía el comprobante"},
    {"method": "BANK_TRANSFER", "bank_name": "Bancolombia", "account_type": "Ahorros",
     "account_number": "123456789", "account_holder": "Olga Dueña", "holder_document": "CC 123"},
]}
r = http.put(f"/barbershop-settings/{IDS['shop']}/payment-methods", headers=owner, json=methods)
check("la barbería guarda sus métodos -> 200", r.status_code == 200 and len(r.json()) == 3, r.text)

r = http.get(f"/barbershops/{IDS['shop']}/payment-methods")
check("público ve los 3 métodos activos", r.status_code == 200 and {m["method"] for m in r.json()} == {"CASH", "NEQUI", "BANK_TRANSFER"}, r.text)

pe = "pagos@test.co"
r = guest_book(pe, slot(4, 10))
check("sin elegir método -> 400", r.status_code == 400 and "pagar" in r.text, r.text)
r = guest_book(pe, slot(4, 10), payment_method="DEPOSIT")
check("método no aceptado por la barbería -> 400", r.status_code == 400, r.text)

r = guest_book(pe, slot(4, 10), payment_method="NEQUI")
check("reserva con Nequi -> 201", r.status_code == 201 and r.json()["payment_method"] == "NEQUI", r.text)
pay_token = r.json().get("manage_token", "")
pay_id = r.json().get("id")
check("pago queda PENDING", r.json().get("payment_status") == "PENDING")

v = http.get(f"/guest/bookings/{pay_token}").json()
check("la vista del invitado trae los datos para pagar", (v.get("payment_details") or {}).get("account_number") == "3001234567", str(v.get("payment_details")))
check("el correo incluye los datos de pago (Nequi + número)", "Nequi" in emails_to(pe) and "3001234567" in emails_to(pe), emails_to(pe)[:300])

r = http.post(f"/guest/bookings/{pay_token}/payment-reference", json={"reference": "AB"})
check("referencia demasiado corta -> 422", r.status_code == 422)
r = http.post(f"/guest/bookings/{pay_token}/payment-reference", json={"reference": "NEQ-889900"})
check("invitado reporta su pago -> REPORTED", r.status_code == 200 and r.json()["payment_status"] == "REPORTED", r.text)

r = http.get(f"/barbershop-settings/{IDS['shop']}/payments", headers=owner, params={"state": "OPEN"})
rows = r.json() if r.status_code == 200 else []
check("la barbería ve el pago por verificar", any(x["id"] == pay_id and x["payment_reference"] == "NEQ-889900" for x in rows), r.text[:200])

r = http.patch(f"/barbershop-settings/{IDS['shop']}/payments/{pay_id}", headers=owner, json={"status": "PAID"})
check("la barbería confirma el pago -> PAID", r.status_code == 200 and r.json()["payment_status"] == "PAID", r.text)
check("ya no está en pendientes", all(x["id"] != pay_id for x in http.get(f"/barbershop-settings/{IDS['shop']}/payments", headers=owner).json()))
r = http.post(f"/guest/bookings/{pay_token}/payment-reference", json={"reference": "NEQ-1234"})
check("reportar un pago ya confirmado -> 409", r.status_code == 409, r.text)

r = http.post("/bookings", headers=client_h, json={
    "barber_id": IDS["barber"], "service_id": IDS["cut"], "start_at": slot(5, 10), "customer_notes": None,
})
check("usuario con cuenta sin método -> 400", r.status_code == 400, r.text)
r = http.post("/bookings", headers=client_h, json={
    "barber_id": IDS["barber"], "service_id": IDS["cut"], "start_at": slot(5, 10), "customer_notes": None,
    "payment_method": "CASH",
})
check("usuario con cuenta paga en efectivo -> 201", r.status_code == 201 and r.json()["payment_method"] == "CASH", r.text)
cash_id = r.json().get("id")
check("cliente con cuenta: client_user_id asignado", r.json().get("client_user_id") == IDS["client"])
r = http.post(f"/bookings/{cash_id}/payment-reference", headers=client_h, json={"reference": "efectivo"})
check("en efectivo no se reporta referencia -> 409", r.status_code == 409, r.text)
r = http.post(f"/bookings/{pay_id}/payment-reference", headers=client_h, json={"reference": "ajeno-1"})
check("no se puede reportar pago de una reserva ajena -> 404", r.status_code == 404, r.text)

# =====================================================================
section("C. Servicio a domicilio")
# =====================================================================
admin = login("admin@test.co")
SHOP = IDS["shop"]
# Los pagos ya están configurados: elegimos efectivo en cada reserva.
CASH = {"payment_method": "CASH"}
home = {"address": "Carrera 53 # 82-86, apto 301", "latitude": 10.9700, "longitude": -74.7800, "access_notes": "Torre B"}


def home_book(email, start, h=home, service=None, **extra):
    body = {"booking_type": "HOME", "home": h, **CASH, **extra}
    if service:
        body["service_id"] = service
    http.post("/guest/verification-code", json={"email": email})
    c = last_code(email)
    payload = guest_body(email, start, c, **body)
    return http.post("/guest/bookings", json=payload)


r = home_book("dom1@test.co", slot(4, 14))
check("domicilio sin estar aprobado -> 400", r.status_code == 400 and "no ofrece" in r.text, r.text)

req = {"radius_km": 8, "fee": 8000, "min_notice_hours": 3, "zones": "Alto Prado, Riomar",
       "hygiene_kit": True, "barbers_verified": True, "accepts_policy": True, "notes": "Equipo propio"}
r = http.post(f"/barbershop-settings/{SHOP}/home-service/request", headers=owner, json={**req, "hygiene_kit": False})
check("solicitud sin aceptar los requisitos -> 422", r.status_code == 422, r.text)
r = http.post(f"/barbershop-settings/{SHOP}/home-service/request", headers=client_h, json=req)
check("un cliente no puede solicitar domicilio -> 403", r.status_code in (401, 403), str(r.status_code))
r = http.post(f"/barbershop-settings/{SHOP}/home-service/request", headers=owner, json=req)
check("la barbería solicita -> PENDING", r.status_code == 200 and r.json()["status"] == "PENDING", r.text)
check("aviso al administrador de plataforma", "plataforma@test.co" in log_text())
r = http.post(f"/barbershop-settings/{SHOP}/home-service/request", headers=owner, json=req)
check("solicitar dos veces -> 409", r.status_code == 409, r.text)

r = home_book("dom2@test.co", slot(4, 14))
check("domicilio con solicitud pendiente -> 400", r.status_code == 400, r.text)

r = http.get("/admin/home-service/requests", headers=admin, params={"status_filter": "PENDING"})
check("el admin ve la solicitud pendiente", r.status_code == 200 and any(x["barbershop_id"] == SHOP for x in r.json()), r.text[:200])
r = http.post(f"/admin/barbershops/{SHOP}/home-service/approve", headers=owner)
check("el dueño no puede aprobar su propia solicitud -> 403", r.status_code in (401, 403), str(r.status_code))
r = http.post(f"/admin/barbershops/{SHOP}/home-service/reject", headers=admin, json={"reason": "no"})
check("rechazo sin motivo suficiente -> 422", r.status_code == 422)
r = http.post(f"/admin/barbershops/{SHOP}/home-service/approve", headers=admin)
check("el admin aprueba -> APPROVED", r.status_code == 200 and r.json()["status"] == "APPROVED" and r.json()["offers_home_service"] is True, r.text)
check("correo de aprobación a la barbería", "aprobado" in emails_to("shop@test.co").lower())

r = http.get(f"/barbershops/{SHOP}")
d = r.json() if r.status_code == 200 else {}
check("el detalle público expone tarifa y radio",
      (d.get("barbershop") or d).get("home_service_fee") in (8000, 8000.0) and (d.get("barbershop") or d).get("offers_home_service") is True, r.text[:240])

r = home_book("dom3@test.co", slot(4, 14))
check("domicilio dentro de cobertura -> 201", r.status_code == 201, r.text)
hb = r.json() if r.status_code == 201 else {}
check("queda PENDING (domicilio requiere confirmación)", hb.get("status_code") == "PENDING", str(hb.get("status_code")))
check("guarda dirección y recargo", hb.get("home_address") == home["address"] and float(hb.get("home_fee", 0)) == 8000, str(hb))
check("correo menciona domicilio y solicitud", "A domicilio" in emails_to("dom3@test.co") and "Solicitud recibida" in emails_to("dom3@test.co"))

far = {**home, "latitude": 11.2, "longitude": -74.7}
r = home_book("dom4@test.co", slot(4, 15), h=far)
check("fuera de la zona de cobertura -> 400", r.status_code == 400 and "cobertura" in r.text, r.text)

soon = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
r = home_book("dom5@test.co", soon.strftime("%Y-%m-%dT%H:%M:%S"))
check("sin la anticipación mínima -> 400", r.status_code == 400, r.text)

r = home_book("dom6@test.co", slot(4, 16), service=IDS["beard"])
check("servicio no habilitado para domicilio -> 400", r.status_code == 400 and "domicilio" in r.text, r.text)

r = home_book("dom7@test.co", slot(4, 16), h=None)
check("domicilio sin dirección -> 400/422", r.status_code in (400, 422), r.text)

barber_h = login("barber@test.co")
r = http.patch(f"/bookings/{hb['id']}/confirm", headers=barber_h)
check("el barbero confirma la reserva a domicilio", r.status_code == 200 and r.json()["status_code"] == "CONFIRMED", r.text)
check("correo 'reserva confirmada' por cambio de estado", "fue confirmada" in emails_to("dom3@test.co"))

r = http.post(f"/admin/barbershops/{SHOP}/home-service/suspend", headers=admin, json={"reason": "Quejas de clientes"})
check("el admin suspende el servicio", r.status_code == 200 and r.json()["status"] == "SUSPENDED" and r.json()["offers_home_service"] is False, r.text)
r = home_book("dom8@test.co", slot(4, 17))
check("domicilio suspendido -> 400", r.status_code == 400, r.text)
r = http.post(f"/admin/barbershops/{SHOP}/home-service/approve", headers=admin)
check("el admin puede reactivarlo", r.status_code == 200 and r.json()["status"] == "APPROVED", r.text)

r = http.patch(f"/barbershop-settings/{SHOP}/home-service/terms", headers=owner, json={"fee": 12000, "min_notice_hours": 2, "zones": "Todo"})
check("la barbería ajusta tarifa y anticipación", r.status_code == 200 and r.json()["fee"] == 12000, r.text)

# =====================================================================
section("D. Recordatorios por correo")
# =====================================================================
from app.services.reminder_service import run_once  # noqa: E402

db = SessionLocal()
now = datetime.now()
statuses = dict(db.execute(text("SELECT code, id FROM booking_statuses")).all())


def insert_booking(email, start, created_ago_h):
    db.execute(text("""
        INSERT INTO bookings (barbershop_id, barber_id, service_id, status_id, start_at, end_at, service_price,
                              guest_name, guest_email, manage_token, booking_type, created_at)
        VALUES (:shop, :barber, :svc, :st, :start, :end, 25000, 'Rita Recordada', :email, :tok, 'IN_SHOP', :created)
    """), {"shop": SHOP, "barber": IDS["barber"], "svc": IDS["cut"], "st": statuses["CONFIRMED"],
           "start": start, "end": start + timedelta(minutes=30), "email": email,
           "tok": "rem" + email.split("@")[0] + "x" * 40, "created": now - timedelta(hours=created_ago_h)})
    db.commit()
    return db.execute(text("SELECT id FROM bookings WHERE guest_email=:e"), {"e": email}).scalar()


id24 = insert_booking("rec24@test.co", now + timedelta(hours=20), 72)
id2 = insert_booking("rec2@test.co", now + timedelta(minutes=90), 72)
idnew = insert_booking("recnew@test.co", now + timedelta(minutes=90), 0.5)   # creada hace 30 min: no aplica
idfar = insert_booking("recfar@test.co", now + timedelta(days=3), 72)        # muy lejos: no aplica

import contextlib  # noqa: E402
import io  # noqa: E402

cap = io.StringIO()
with contextlib.redirect_stdout(cap):          # run_once corre en este proceso, no en el servidor
    sent = run_once()
    time.sleep(1.5)                            # los correos salen en hilos
out = cap.getvalue()


def sent_to(addr: str) -> str:
    return "\n".join(b for b in re.split(r"(?=\[EMAIL-DEV\] Para: )", out) if f"Para: {addr}" in b)


check("el proceso de recordatorios envía 2 correos", sent == 2, f"enviados={sent}")
check("recordatorio 'es mañana' a quien reservó con tiempo", "es mañana" in sent_to("rec24@test.co").lower())
check("recordatorio 'en 2 horas'", "2 horas" in sent_to("rec2@test.co"))
check("no recuerda una cita creada hace 30 min para dentro de 90", sent_to("recnew@test.co") == "")
check("no recuerda una cita de dentro de 3 días", sent_to("recfar@test.co") == "")
with contextlib.redirect_stdout(io.StringIO()):
    again = run_once()
check("segunda ejecución no repite recordatorios", again == 0)
db.commit()  # nueva transacción: ver lo que escribió run_once
marks = db.execute(text("SELECT reminder_24h_sent_at, reminder_2h_sent_at FROM bookings WHERE id IN (:a,:b)"), {"a": id24, "b": id2}).all()
check("se marcan como enviados en la base", marks[0][0] is not None and marks[1][1] is not None)
db.close()

# =====================================================================
section("E. Regresión")
# =====================================================================
r = http.get("/bookings/me", headers=client_h)
check("GET /bookings/me sigue funcionando", r.status_code == 200 and isinstance(r.json(), list), r.text[:100])
check("sin token no se puede reservar como usuario -> 401", http.post("/bookings", json={"barber_id": 1, "service_id": 1, "start_at": slot(6, 10)}).status_code in (401, 403))

print("\n" + "=" * 60)
print(f"RESULTADO API: {len(passed)} pruebas OK, {len(failed)} con fallo")
if failed:
    print("Fallos:")
    for f in failed:
        print("  -", f)
sys.exit(1 if failed else 0)
