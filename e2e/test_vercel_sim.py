"""
Simulación local del despliegue en Vercel (sin cuenta ni internet):

  * la API arranca desde api/index.py (el mismo archivo que usa Vercel) con VERCEL=1
  * el frontend COMPILADO (frontend/dist/frontend/browser) se sirve con la misma regla que vercel.json:
        /api/*  -> función de Python        cualquier otra ruta -> /index.html
  * el navegador entra por un dominio que no es localhost, así la app usa la ruta relativa /api/v1

Requisitos: MySQL de pruebas activo (puerto 3399), `ng build` hecho, e2e/db_setup.py ejecutado.
Uso: python e2e/test_vercel_sim.py        (Python del sistema con playwright)
"""

import http.client
import json
import mimetypes
import os
import re
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "frontend" / "dist" / "frontend" / "browser"
API_PORT, WEB_PORT = 8011, 5055
HOST = "barbergo.test"
LOG = Path(__file__).with_name("vercel_sim_api.log")

passed, failed = [], []


def check(name, cond, detail=""):
    (passed if cond else failed).append(name)
    print(("  [OK]    " if cond else "  [FALLO] ") + name + (f"  -> {detail}" if detail and not cond else ""))


assert (DIST / "index.html").exists(), "falta el build: cd frontend && npm run build"

# ------------------------------------------------------------------ API (api/index.py, VERCEL=1)
env = dict(os.environ)
env.update({
    "VERCEL": "1", "DB_HOST": "127.0.0.1", "DB_PORT": "3399", "DB_USER": "root", "DB_PASSWORD": "test",
    "DB_NAME": "barbergo_test", "JWT_SECRET_KEY": "sim-secret-0123456789", "RESEND_API_KEY": "", "SMTP_HOST": "",
    "FRONTEND_URL": f"http://{HOST}:{WEB_PORT}", "CRON_SECRET": "secreto-de-cron", "RATE_LIMIT_MULTIPLIER": "100",
    "TRUST_PROXY": "1", "PYTHONIOENCODING": "utf-8",
})
api = subprocess.Popen(
    [str(ROOT / "backend" / ".venv" / "Scripts" / "python.exe"), "-m", "uvicorn", "api.index:app", "--port", str(API_PORT)],
    cwd=str(ROOT), env=env, stdout=LOG.open("w", encoding="utf-8"), stderr=subprocess.STDOUT,
)

# ------------------------------------------------------------------ "Vercel": estáticos + rewrites
class Edge(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _proxy(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0) or 0)) if self.command != "GET" else None
        conn = http.client.HTTPConnection("127.0.0.1", API_PORT, timeout=30)
        headers = {k: v for k, v in self.headers.items() if k.lower() not in ("host", "connection")}
        headers["X-Forwarded-For"] = "203.0.113.7"
        conn.request(self.command, self.path, body=body, headers=headers)
        r = conn.getresponse()
        data = r.read()
        self.send_response(r.status)
        for k, v in r.getheaders():
            if k.lower() not in ("transfer-encoding", "connection", "content-length"):
                self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _static(self):
        path = self.path.split("?")[0].lstrip("/")
        f = DIST / path
        if not path or not f.is_file():            # regla de vercel.json: todo lo demás -> /index.html
            f = DIST / "index.html"
        data = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(str(f))[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_ALL(self):
        (self._proxy if self.path.startswith("/api/") else self._static)()

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = do_ALL


edge = ThreadingHTTPServer(("127.0.0.1", WEB_PORT), Edge)
threading.Thread(target=edge.serve_forever, daemon=True).start()

try:
    for _ in range(40):
        try:
            if httpx.get(f"http://127.0.0.1:{API_PORT}/", timeout=2).status_code == 200:
                break
        except Exception:
            time.sleep(1)
    else:
        raise SystemExit("la API no arrancó:\n" + LOG.read_text(encoding="utf-8", errors="replace")[-1500:])

    base = f"http://127.0.0.1:{WEB_PORT}"

    print("\n== 1. API servida desde api/index.py (como en Vercel)")
    r = httpx.get(f"{base}/api/v1/barbershops/discover")
    check("GET /api/v1/barbershops/discover a través de la regla /api/*", r.status_code == 200 and r.json()["total"] >= 1, r.text[:120])
    check("la documentación /docs responde desde la función", httpx.get(f"http://127.0.0.1:{API_PORT}/docs").status_code == 200)

    print("\n== 2. Tareas programadas (/api/v1/cron/reminders)")
    r = httpx.get(f"{base}/api/v1/cron/reminders")
    check("sin credenciales -> 401", r.status_code == 401, r.text)
    r = httpx.get(f"{base}/api/v1/cron/reminders", headers={"Authorization": "Bearer incorrecto"})
    check("secreto incorrecto -> 401", r.status_code == 401)
    r = httpx.get(f"{base}/api/v1/cron/reminders", headers={"Authorization": "Bearer secreto-de-cron"})
    check("secreto correcto -> 200 con conteo", r.status_code == 200 and "sent" in r.json(), r.text)
    r = httpx.post(f"{base}/api/v1/cron/reminders", headers={"Authorization": "Bearer secreto-de-cron"})
    check("también acepta POST (GitHub Actions)", r.status_code == 200)

    print("\n== 3. Correos en línea (serverless no puede usar hilos)")
    t0 = time.time()
    r = httpx.post(f"{base}/api/v1/guest/verification-code", json={"email": "sim@test.co"})
    log = LOG.read_text(encoding="utf-8", errors="replace")
    check("el código se envía antes de responder (sin esperar a un hilo)", r.status_code == 200 and "Para: sim@test.co" in log, log[-300:])

    print("\n== 4. Navegador en un dominio de producción (ruta relativa /api/v1)")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=[f"--host-resolver-rules=MAP {HOST} 127.0.0.1"])
        page = browser.new_page(viewport={"width": 1366, "height": 900})
        errs, api_calls = [], []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" and "favicon" not in m.text else None)
        page.on("request", lambda rq: api_calls.append(rq.url) if "/api/" in rq.url or ":8000" in rq.url else None)

        page.goto(f"http://{HOST}:{WEB_PORT}/", wait_until="networkidle")
        page.wait_for_selector("app-barbershop-card", timeout=15000)
        check("la portada carga las barberías reales desde /api/v1", page.locator("app-barbershop-card").count() >= 1)
        check("las llamadas van al mismo dominio (nunca a 127.0.0.1:8000)",
              api_calls and all(u.startswith(f"http://{HOST}:{WEB_PORT}/api/v1") for u in api_calls), str(api_calls[:3]))

        page.goto(f"http://{HOST}:{WEB_PORT}/barberias/1", wait_until="networkidle")
        page.wait_for_selector("h1", timeout=15000)
        check("enlace directo /barberias/1 funciona (regla -> index.html)", "Test Barber Club" in page.inner_text("h1"))

        page.goto(f"http://{HOST}:{WEB_PORT}/reserva/ruta-inexistente-123", wait_until="networkidle")
        page.wait_for_selector("text=No encontramos esta reserva", timeout=15000)
        check("enlace directo /reserva/<token> inválido muestra su error (no 404 de Vercel)", True)

        page.goto(f"http://{HOST}:{WEB_PORT}/login", wait_until="networkidle")
        page.fill("#email", "admin@test.co")
        page.fill("#password", "Password123!")
        page.click("button.auth-submit")
        page.wait_for_function("() => !location.pathname.startsWith('/login')", timeout=15000)
        page.goto(f"http://{HOST}:{WEB_PORT}/admin/domicilio", wait_until="networkidle")
        page.wait_for_selector(".head h1", timeout=15000)
        check("inicio de sesión y panel de administración por enlace directo", "Solicitudes de domicilio" in page.inner_text(".head h1"))

        # reserva de invitado de punta a punta contra la función
        email = "sim.invitada@test.co"
        page.evaluate("() => localStorage.clear()")
        page.goto(f"http://{HOST}:{WEB_PORT}/barberias/1", wait_until="networkidle")
        r = httpx.post(f"{base}/api/v1/guest/verification-code", json={"email": email})
        code = None
        for _ in range(20):
            blocks = re.split(r"(?=\[EMAIL-DEV\] Para: )", LOG.read_text(encoding="utf-8", errors="replace"))
            for b in reversed(blocks):
                if f"Para: {email}" in b and (m := re.search(r"código: (\d{6})", b)):
                    code = m.group(1)
                    break
            if code:
                break
            time.sleep(0.3)
        from datetime import datetime, timedelta
        start = (datetime.now() + timedelta(days=12)).replace(hour=9, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")
        r = httpx.post(f"{base}/api/v1/guest/bookings", json={
            "barber_id": 1, "service_id": 1, "start_at": start, "customer_notes": None, "name": "Sim Invitada",
            "email": email, "phone": "3001112222", "code": code, "accept_terms": True,
            "payment_method": None, "booking_type": "IN_SHOP"})
        token = r.json().get("manage_token", "") if r.status_code == 201 else ""
        check("reserva de invitado por la función serverless (201)", r.status_code in (201, 400) and (r.status_code == 201 or "pagar" in r.text), r.text[:160])
        if token:
            time.sleep(0.5)
            check("el correo de confirmación sale en la misma petición (inline)", "Tu reserva" in LOG.read_text(encoding="utf-8", errors="replace"))
            page.goto(f"http://{HOST}:{WEB_PORT}/reserva/{token}", wait_until="networkidle")
            page.wait_for_selector("article.card h1", timeout=15000)
            check("la gestión por enlace funciona en producción", "Corte" in page.inner_text("article.card"))

        ignorar = ("Failed to load resource", "tile.openstreetmap", "ERR_", "net::", "401", "404")
        reales = [e for e in errs if not any(k in e for k in ignorar)]
        check("sin errores de JavaScript", not reales, " | ".join(reales[:2]))
        browser.close()
finally:
    api.terminate()
    edge.shutdown()

print("\n" + "=" * 60)
print(f"RESULTADO SIMULACIÓN VERCEL: {len(passed)} OK, {len(failed)} con fallo")
for f in failed:
    print("  -", f)
sys.exit(1 if failed else 0)
