"""
Paridad MySQL <-> PostgreSQL.

Carga los MISMOS datos en las dos bases, llama a todos los endpoints de lectura de la API
(incluidas las ~3.500 líneas de estadísticas del panel de administración) y compara las respuestas.
Un 500, o una respuesta distinta entre las dos bases, es un fallo.

Requisitos: contenedores barbergo-test-db (MySQL, :3399) y barbergo-test-pg (PostgreSQL, :3398).
Uso: python e2e/test_parity.py
"""

import json
import os
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / "backend" / ".venv" / "Scripts" / "python.exe")
sys.path.insert(0, str(Path(__file__).parent))
import env as e2e_env  # noqa: E402

PASSWORD = e2e_env.PASSWORD
DBS = {"mysql": 8101, "postgres": 8102}
SKIP_KEYS = ("_at", "generated", "token", "updated", "created")


def run_setup(db: str):
    e = dict(os.environ, E2E_DB=db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([PY, str(ROOT / "e2e" / "db_setup.py")], env=e, capture_output=True, text=True, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-800:] + r.stderr[-800:]


def start_api(db: str, port: int):
    e = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1", RATE_LIMIT_MULTIPLIER="100")
    e.update(e2e_env.DB_MYSQL if db == "mysql" else e2e_env.DB_POSTGRES)
    e.update({"JWT_SECRET_KEY": "parity-secret-0123456789", "RESEND_API_KEY": "", "SMTP_HOST": ""})
    log = (ROOT / "e2e" / f"parity_{db}.log").open("w", encoding="utf-8")
    p = subprocess.Popen([PY, "-m", "uvicorn", "app.main:app", "--port", str(port)], cwd=str(ROOT / "backend"), env=e, stdout=log, stderr=subprocess.STDOUT)
    for _ in range(40):
        try:
            if httpx.get(f"http://127.0.0.1:{port}/", timeout=2).status_code == 200:
                return p
        except Exception:
            time.sleep(1)
    p.terminate()
    raise SystemExit(f"la API {db} no arrancó")


def login(c: httpx.Client, email: str) -> dict:
    r = c.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def populate(c: httpx.Client):
    """Mismos datos en las dos bases: reservas en varios estados, domicilio pendiente y pagos."""
    owner, admin, barber, client = (login(c, f"{n}@test.co") for n in ("owner", "admin", "barber", "client"))
    base_day = date.today() + timedelta(days=5)

    def slot(i):
        return datetime.combine(base_day + timedelta(days=i // 6), datetime.min.time()).replace(hour=9 + (i % 6)).strftime("%Y-%m-%dT%H:%M:%S")

    c.put("/api/v1/barbershop-settings/1/payment-methods", headers=owner, json={"methods": [{"method": "CASH"}]})
    ids = []
    for i in range(5):
        r = c.post("/api/v1/bookings", headers=client, json={
            "barber_id": 1, "service_id": 1 if i % 2 == 0 else 2, "start_at": slot(i), "customer_notes": f"nota {i}", "payment_method": "CASH"})
        assert r.status_code == 201, r.text
        ids.append(r.json()["id"])
    c.patch(f"/api/v1/bookings/{ids[1]}/cancel", headers=client)
    c.patch(f"/api/v1/bookings/{ids[2]}/start", headers=barber)
    c.patch(f"/api/v1/bookings/{ids[2]}/complete", headers=barber)
    c.patch(f"/api/v1/bookings/{ids[3]}/no-show", headers=barber)
    c.post("/api/v1/barbershop-settings/1/home-service/request", headers=owner, json={
        "radius_km": 6, "fee": 7000, "min_notice_hours": 2, "zones": "Z", "hygiene_kit": True,
        "barbers_verified": True, "accepts_policy": True, "notes": None})
    return {"admin": admin, "owner": owner, "barber": barber, "client": client}


def normalize(x):
    if isinstance(x, dict):
        return {k: normalize(v) for k, v in sorted(x.items()) if not any(s in k.lower() for s in SKIP_KEYS)}
    if isinstance(x, list):
        return [normalize(v) for v in x]
    if isinstance(x, float):
        return round(x, 4)
    if isinstance(x, str):
        try:
            return round(float(x), 4) if x.replace(".", "", 1).replace("-", "", 1).isdigit() and "." in x else x
        except ValueError:
            return x
    return x


def endpoints(c: httpx.Client) -> list[tuple[str, str]]:
    spec = c.get("/openapi.json").json()
    subs = {"barbershop_id": "1", "booking_id": "1", "user_id": "4", "barber_id": "1", "service_id": "1", "id": "1", "day_of_week": "1"}
    out = []
    for path, ops in spec["paths"].items():
        if "get" not in ops or "{token}" in path or path.endswith("/cron/reminders"):
            continue
        p = path
        for k, v in subs.items():
            p = p.replace("{" + k + "}", v)
        if "{" in p:
            continue
        out.append((p, ops["get"].get("summary", "")))
    extra = [
        "/api/v1/admin/barbershops?search=test", "/api/v1/admin/barbershops?status=active", "/api/v1/admin/barbershops?status=inactive",
        "/api/v1/admin/users?search=ada", "/api/v1/admin/users?role=BARBER", "/api/v1/admin/users?status=active",
        "/api/v1/admin/bookings?status=CONFIRMED", "/api/v1/admin/bookings?search=carla",
        "/api/v1/admin/home-service/requests?status_filter=PENDING",
        f"/api/v1/barbershops/discover?q=test", "/api/v1/barbershops/discover?q=TEST",
        f"/api/v1/barbershop-settings/1/payments?state=ALL",
        f"/api/v1/availability/barbers/1?date={(date.today() + timedelta(days=9)).isoformat()}&service_id=1",
    ]
    return out + [(e, "extra") for e in extra]


def collect(db: str, port: int) -> dict:
    run_setup(db)
    api = start_api(db, port)
    try:
        c = httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=60)
        tokens = populate(c)
        results = {}
        for path, _ in endpoints(c):
            got = None
            r = None
            for who in ("admin", "owner", "barber", "client", None):
                try:
                    r = c.get(path, headers=tokens.get(who, {}) if who else {})
                except Exception as error:      # la conexión se cortó: se anota y se sigue
                    got = (599, f"{type(error).__name__}")
                    break
                if r.status_code not in (401, 403):
                    got = (r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text[:80])
                    break
            results[path] = got if got else (r.status_code if r else 0, None)
        return results
    finally:
        api.terminate()
        time.sleep(1)


def main():
    data = {db: collect(db, port) for db, port in DBS.items()}
    my, pg = data["mysql"], data["postgres"]
    ok = bad = 0
    print(f"{len(my)} endpoints comparados\n")
    for path in sorted(my):
        a, b = my[path], pg.get(path)
        if a[0] >= 500 or b[0] >= 500:
            print(f"  [FALLO] 5xx   {path}   mysql={a[0]} postgres={b[0]}")
            bad += 1
        elif a[0] != b[0]:
            print(f"  [FALLO] estado distinto {path}   mysql={a[0]} postgres={b[0]}")
            bad += 1
        elif path.endswith("/health"):
            ok += 1          # la versión del motor es distinta por definición: basta con que ambos respondan 200
        elif json.dumps(normalize(a[1]), sort_keys=True, default=str) != json.dumps(normalize(b[1]), sort_keys=True, default=str):
            print(f"  [FALLO] respuesta distinta {path}")
            na, nb = normalize(a[1]), normalize(b[1])
            sa, sb = json.dumps(na, sort_keys=True, default=str, indent=1).splitlines(), json.dumps(nb, sort_keys=True, default=str, indent=1).splitlines()
            shown = 0
            for x, y in zip(sa, sb):
                if x != y and shown < 4:
                    print(f"          mysql:    {x.strip()[:110]}\n          postgres: {y.strip()[:110]}")
                    shown += 1
            bad += 1
        else:
            ok += 1
    print(f"\nRESULTADO PARIDAD: {ok} idénticos, {bad} con diferencias o errores")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
