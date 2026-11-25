"""
Pruebas e2e de interfaz (Playwright + Chromium) contra frontend :4200, backend :8000 y MySQL reales.

Antes:  python e2e/db_setup.py   y backend/frontend en marcha (ver README en e2e/).
Uso:    python e2e/test_ui.py     (con el Python del sistema, que tiene playwright)
"""

import json
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
API = "http://127.0.0.1:8000/api/v1"
WEB = "http://localhost:4200"
PASSWORD = "Password123!"
LOG = HERE / "backend.log"
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
IDS = json.loads((HERE / "ids.json").read_text())
SHOP = IDS["shop"]

passed, failed = [], []
page_errors: list[str] = []


def check(name, cond, detail=""):
    (passed if cond else failed).append(name)
    print(("  [OK]    " if cond else "  [FALLO] ") + name + (f"  -> {detail}" if detail and not cond else ""))


def section(t):
    print(f"\n== {t}")


def last_code(email):
    time.sleep(1.0)
    text = LOG.read_text(encoding="utf-8", errors="replace")
    for b in reversed(re.split(r"(?=\[EMAIL-DEV\] Para: )", text)):
        if f"Para: {email}" in b:
            m = re.search(r"código: (\d{6})", b)
            if m:
                return m.group(1)
    raise AssertionError("sin código para " + email)


def api_login(email):
    r = httpx.post(f"{API}/auth/login", json={"email": email, "password": PASSWORD})
    return {"Authorization": "Bearer " + r.json()["access_token"]}


# --------------------------------------------------------------------- setup por API
owner_h, admin_h = api_login("owner@test.co"), api_login("admin@test.co")
httpx.put(f"{API}/barbershop-settings/{SHOP}/payment-methods", headers=owner_h, json={"methods": [
    {"method": "CASH"},
    {"method": "NEQUI", "account_number": "3001234567", "account_holder": "Olga Dueña"},
]})
r = httpx.post(f"{API}/barbershop-settings/{SHOP}/home-service/request", headers=owner_h, json={
    "radius_km": 8, "fee": 8000, "min_notice_hours": 3, "zones": "Alto Prado",
    "hygiene_kit": True, "barbers_verified": True, "accepts_policy": True, "notes": "e2e"})
assert r.status_code == 200 and r.json()["status"] == "PENDING", r.text


def shot(page, name):
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)


def ui_login(page, email):
    page.goto(f"{WEB}/login", wait_until="networkidle")
    page.fill("#email", email)
    page.fill("#password", PASSWORD)
    page.click("button.auth-submit")
    page.wait_for_function("() => !location.pathname.startsWith('/login')", timeout=15000)


def pick_booking(page, day_offset, slot_index=8, service="Corte"):
    """Servicio -> barbero -> fecha -> hueco. Deja visible el resumen."""
    page.goto(f"{WEB}/barberias/{SHOP}", wait_until="networkidle")
    page.locator(".service-card", has_text=service).click()
    page.get_by_role("button", name="Elegir barbero").click()
    page.locator(".barber-card").first.click()
    page.get_by_role("button", name="Elegir fecha y hora").click()
    d = (date.today() + timedelta(days=day_offset)).isoformat()
    page.locator("input[type=date]").fill(d)
    page.wait_for_selector(".slot-button", timeout=15000)
    page.locator(".slot-button").nth(slot_index).click()
    page.wait_for_selector(".confirm-booking-button", timeout=10000)


def overflow_x(page) -> int:
    return page.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")


with sync_playwright() as pw:
    browser = pw.chromium.launch()
    ctx = browser.new_context(viewport={"width": 1366, "height": 900}, locale="es-CO")
    page = ctx.new_page()
    page.set_default_timeout(15000)
    page.on("pageerror", lambda e: page_errors.append(str(e)))
    page.on("console", lambda m: page_errors.append(f"[{page.url}] {m.text}") if m.type == "error" and "favicon" not in m.text else None)

    # ================================================================ 1. Admin aprueba (UI)
    section("1. Administrador de plataforma aprueba el domicilio (UI)")
    ui_login(page, "admin@test.co")
    page.goto(f"{WEB}/admin/domicilio", wait_until="networkidle")
    page.wait_for_selector("article.card", timeout=15000)
    check("la solicitud pendiente aparece en /admin/domicilio", "Test Barber Club" in page.inner_text("article.card"))
    check("muestra los requisitos declarados", page.locator(".decl li.ok").count() == 3, str(page.locator(".decl li.ok").count()))
    shot(page, "01_admin_solicitudes")
    page.get_by_role("button", name="Aprobar").click()
    page.wait_for_selector("text=Pendientes")
    time.sleep(1.2)
    st = httpx.get(f"{API}/barbershop-settings/{SHOP}/home-service", headers=owner_h).json()
    check("tras pulsar Aprobar el estado es APPROVED en la API", st["status"] == "APPROVED" and st["offers_home_service"] is True, str(st["status"]))
    ctx.clear_cookies()
    page.evaluate("() => localStorage.clear()")

    # ================================================================ 2. Invitado en barbería + pago
    section("2. Reserva de invitado en la barbería con pago Nequi")
    pick_booking(page, 6)
    check("sin sesión aparece el selector 'En la barbería / A domicilio'", page.locator(".where-options").is_visible())
    check("aparece el selector de método de pago", page.locator("app-payment-picker .opt").count() == 2)
    page.click(".confirm-booking-button")
    check("sin elegir pago muestra el error", "cómo vas a pagar" in page.inner_text(".booking-feedback.error"), page.inner_text(".booking-feedback"))
    page.locator("app-payment-picker .opt", has_text="Nequi").click()
    check("al elegir Nequi muestra los datos para pagar", "3001234567" in page.inner_text("app-payment-picker .details"))
    page.click(".confirm-booking-button")
    page.wait_for_selector("app-guest-checkout .sheet")
    check("sin sesión se abre el checkout de invitado (no redirige a /login)", "/login" not in page.url)
    shot(page, "02_checkout_invitado")

    email = "ui.invitada@test.co"
    page.fill("input[name=name]", "Ursula Interfaz")
    page.fill("input[name=email]", email)
    page.fill("input[name=phone]", "3109998877")
    check("el botón 'Enviar código' está deshabilitado sin aceptar datos", page.locator("app-guest-checkout button.primary[type=submit]").is_disabled())
    page.check("input[name=terms]")
    page.get_by_role("button", name="Enviar código a mi correo").click()
    page.wait_for_selector("input[name=code]")
    page.fill("input[name=code]", "000000")
    page.locator("app-guest-checkout button.primary[type=submit]").click()
    page.wait_for_selector(".error")
    check("código incorrecto muestra el error en pantalla", "código" in page.inner_text(".error").lower(), page.inner_text(".error"))
    page.fill("input[name=code]", last_code(email))
    page.locator("app-guest-checkout button.primary[type=submit]").click()
    page.wait_for_selector(".done", timeout=20000)
    check("reserva creada: '¡Reserva confirmada!'", "Reserva confirmada" in page.inner_text(".done h2"))
    check("muestra cómo pagar con Nequi", "Paga con Nequi" in page.inner_text(".pay") and "3001234567" in page.inner_text(".pay"))
    manage_url = page.inner_text(".manage code").strip()
    check("entrega el enlace de gestión", "/reserva/" in manage_url, manage_url)
    href = page.locator("app-guest-checkout app-calendar-buttons a.google").get_attribute("href") or ""
    check("la reserva creada ofrece 'Agregar a Google Calendar'", "calendar.google.com/calendar/render" in href, href[:120])
    check("el enlace trae título, horario en hora de Colombia y lugar", "Corte+cl" in href and "ctz=America%2FBogota" in href and "dates=" in href and "Calle+84" in href, href)
    with page.expect_download() as dl:
        page.locator("app-guest-checkout app-calendar-buttons button.ics").click()
    ics = Path(dl.value.path()).read_text(encoding="utf-8")
    check("descarga un .ics válido (evento, zona horaria, recordatorio)", all(k in ics for k in ("BEGIN:VCALENDAR", "BEGIN:VEVENT", "SUMMARY:Corte clásico · Test Barber Club", "DTSTART;TZID=America/Bogota:", "LOCATION:Calle 84", "BEGIN:VALARM", "END:VCALENDAR")), ics[:300])
    page.fill(".pay input", "NEQ-UI-2026")
    page.get_by_role("button", name="Ya pagué").click()
    page.wait_for_selector(".okmsg")
    check("reportar el comprobante muestra confirmación", "Pago reportado" in page.inner_text(".okmsg"))
    shot(page, "03_reserva_creada")

    page.get_by_role("link", name="Ver mi reserva").click()
    page.wait_for_selector("article.card h1")
    check("abre /reserva/<token>", "/reserva/" in page.url)
    body = page.inner_text("article.card")
    check("la página de gestión muestra servicio, estado y pago", "Corte clásico" in body and "Confirmada" in body and "Nequi" in body, body[:200])
    check("estado del pago 'En verificación'", "En verificación" in body)
    check("muestra la referencia reportada", "NEQ-UI-2026" in body)
    check("la página de gestión también ofrece agregar al calendario", page.locator("app-calendar-buttons a.google").count() == 1)
    shot(page, "04_gestion_reserva")
    page.get_by_role("button", name="Cancelar reserva").click()
    page.get_by_role("button", name="Sí, cancelar").click()
    page.wait_for_selector("text=Cancelada por ti", timeout=15000)
    check("cancelar desde el enlace funciona", True)
    check("aparece el aviso (toast) de cancelación", page.locator(".toast").count() >= 1)
    check("ya no ofrece cancelar de nuevo", page.get_by_role("button", name="Cancelar reserva").count() == 0)

    # ================================================================ 3. Domicilio con mapa
    section("3. Reserva a domicilio con mapa de cobertura")
    pick_booking(page, 7, slot_index=10)
    page.locator(".where-options button", has_text="A domicilio").click()
    page.wait_for_selector("app-home-address .map")
    time.sleep(1.5)  # carga del mapa
    page.locator("app-payment-picker .opt", has_text="Efectivo").click()
    page.click(".confirm-booking-button")
    check("a domicilio sin dirección se bloquea con mensaje", "dirección" in page.inner_text(".booking-feedback.error").lower(), page.inner_text(".booking-feedback"))

    page.fill("input[autocomplete=street-address]", "Carrera 53 # 82-86, apto 301")
    page.locator("app-home-address .map").scroll_into_view_if_needed()
    time.sleep(0.5)
    box = page.locator("app-home-address .map").bounding_box()
    # esquina del mapa: queda fuera del círculo de cobertura
    page.mouse.click(box["x"] + 6, box["y"] + 6)
    time.sleep(0.6)
    check("un punto fuera de cobertura lo avisa", "fuera de la zona" in page.inner_text("app-home-address").lower(), page.inner_text("app-home-address")[-200:])
    page.click(".confirm-booking-button")
    check("con punto fuera de cobertura no deja continuar", page.locator("app-guest-checkout").count() == 0)
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    time.sleep(0.6)
    check("un punto dentro de cobertura lo confirma", "Dentro de la cobertura" in page.inner_text("app-home-address"), page.inner_text("app-home-address")[-200:])
    shot(page, "05_domicilio_mapa")
    check("el total incluye el desplazamiento ($33.000)", "33.000" in page.inner_text(".summary-total"), page.inner_text(".summary-total"))
    page.click(".confirm-booking-button")
    page.wait_for_selector("app-guest-checkout .sheet")
    email2 = "ui.domicilio@test.co"
    page.fill("input[name=name]", "Dario Domicilio")
    page.fill("input[name=email]", email2)
    page.fill("input[name=phone]", "3101112233")
    page.check("input[name=terms]")
    page.get_by_role("button", name="Enviar código a mi correo").click()
    page.wait_for_selector("input[name=code]")
    page.fill("input[name=code]", last_code(email2))
    check("el botón dice 'Enviar solicitud' (domicilio requiere aprobación)", "Enviar solicitud" in page.inner_text("app-guest-checkout button.primary[type=submit]"))
    page.locator("app-guest-checkout button.primary[type=submit]").click()
    page.wait_for_selector(".done", timeout=20000)
    check("domicilio: '¡Solicitud enviada!'", "Solicitud enviada" in page.inner_text(".done h2"))
    time.sleep(1)
    token2 = page.inner_text(".manage code").strip().split("/")[-1]
    v = httpx.get(f"{API}/guest/bookings/{token2}").json()
    check("la API guarda domicilio, dirección y estado PENDING", v["booking_type"] == "HOME" and "Carrera 53" in (v["home_address"] or "") and v["status_code"] == "PENDING", str(v)[:200])

    # ================================================================ 4. Sesión: usuario con cuenta
    section("4. Usuario con cuenta reserva sin pasar por el checkout de invitado")
    ui_login(page, "client@test.co")
    pick_booking(page, 8)
    page.locator("app-payment-picker .opt", has_text="Efectivo").click()
    page.click(".confirm-booking-button")
    page.wait_for_selector(".booking-success-modal", timeout=15000)
    check("con sesión se crea la reserva directo (modal de éxito)", page.locator("app-guest-checkout").count() == 0)
    check("aparece el confeti de celebración", page.locator("app-confetti").count() >= 1)
    check("el modal de éxito ofrece agregar al calendario", page.locator(".booking-success-modal app-calendar-buttons").count() == 1)
    gh = page.locator(".booking-success-modal app-calendar-buttons a.google").get_attribute("href") or ""
    check("enlace de Google Calendar con nombre de barbería y dirección", "Test+Barber+Club" in gh and "Calle+84" in gh, gh)
    page.goto(f"{WEB}/mis-reservas", wait_until="networkidle")
    page.wait_for_selector(".booking-card", timeout=15000)
    check("'Mis reservas' ofrece agregar al calendario en cada cita vigente", page.locator(".booking-card app-calendar-buttons").count() >= 1)
    mine = httpx.get(f"{API}/bookings/me", headers=api_login("client@test.co")).json()
    check("la reserva queda con método CASH y a nombre del cliente", any(b["payment_method"] == "CASH" for b in mine), str(mine)[:200])
    page.evaluate("() => localStorage.clear()")

    # ================================================================ 5. Paneles de la barbería
    section("5. Panel de la barbería: Domicilio y Pagos")
    ui_login(page, "owner@test.co")
    page.goto(f"{WEB}/admin/configuracion", wait_until="networkidle")
    page.wait_for_selector("button.settings-tab", timeout=15000)
    tabs = page.locator("button.settings-tab").all_inner_texts()
    check("aparecen las pestañas Domicilio y Pagos", any("Domicilio" in t for t in tabs) and any("Pagos" in t for t in tabs), str(tabs))
    page.locator("button.settings-tab", has_text="Domicilio").click()
    page.wait_for_selector("app-home-service-panel .pill")
    check("el panel muestra el estado Aprobado", "Aprobado" in page.inner_text("app-home-service-panel .pill"))
    check("ofrece ajustar tarifa y desactivar", page.get_by_role("button", name="Desactivar domicilio").count() == 1)
    shot(page, "06_panel_domicilio")
    page.locator("button.settings-tab", has_text="Pagos").click()
    page.wait_for_selector("app-payment-methods-panel .method")
    check("el panel de pagos lista los 5 métodos", page.locator("app-payment-methods-panel .method").count() == 5)
    check("Nequi y Efectivo están activos", page.locator("app-payment-methods-panel .method.on").count() == 2)
    page.wait_for_selector("app-payment-methods-panel .pay", timeout=10000)
    check("lista pagos por verificar (reserva de la sección 2 ya reportada o pendiente)", page.locator("app-payment-methods-panel .pay").count() >= 1)
    shot(page, "07_panel_pagos")
    page.locator("app-payment-methods-panel .pay button.ok").first.click()
    time.sleep(1.2)
    paid = httpx.get(f"{API}/barbershop-settings/{SHOP}/payments", headers=owner_h, params={"state": "PAID"}).json()
    check("'Marcar pagado' confirma el pago en la API", len(paid) >= 1, str(paid)[:150])
    page.evaluate("() => localStorage.clear()")

    # ================================================================ 6. Responsive
    section("6. Responsive (móvil 390x844)")
    mobile = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, locale="es-CO")
    mp = mobile.new_page()
    mp.set_default_timeout(15000)
    mp.on("pageerror", lambda e: page_errors.append("[móvil] " + str(e)))
    for path, nombre in (("/", "portada"), ("/barberias", "listado"), (f"/barberias/{SHOP}", "detalle"), ("/login", "login"), ("/registro", "registro"), (f"/reserva/{token2}", "gestión de reserva")):
        mp.goto(WEB + path, wait_until="networkidle")
        time.sleep(0.8)
        ox = overflow_x(mp)
        check(f"sin desbordamiento horizontal en {nombre}", ox <= 2, f"sobran {ox}px")
    mp.goto(WEB + "/", wait_until="networkidle")
    mp.click("button.burger")
    time.sleep(0.6)
    check("el menú hamburguesa abre el panel de navegación", mp.locator("nav.navigation.show").count() == 1)
    shot(mp, "08_movil_menu")
    mp.click("nav.navigation .nav-link >> text=Barberías")
    mp.wait_for_url("**/barberias")
    check("navegar desde el menú móvil funciona y lo cierra", mp.locator("nav.navigation.show").count() == 0)
    # reserva a domicilio en móvil
    pick_booking(mp, 9, slot_index=12)
    check("en móvil se ve el selector de lugar", mp.locator(".where-options").is_visible())
    mp.locator(".where-options button", has_text="A domicilio").click()
    mp.wait_for_selector("app-home-address .map")
    time.sleep(1)
    check("en móvil el mapa cabe en pantalla", overflow_x(mp) <= 2, f"sobran {overflow_x(mp)}px")
    shot(mp, "09_movil_domicilio")
    mobile.close()

    # ================================================================ 7. Modo oscuro
    section("7. Modo oscuro")
    dp = ctx.new_page()
    dp.set_default_timeout(15000)
    dp.goto(f"{WEB}/", wait_until="networkidle")
    before = dp.evaluate("() => getComputedStyle(document.body).backgroundColor")
    dp.click("button.theme-toggle")
    time.sleep(0.8)
    after = dp.evaluate("() => getComputedStyle(document.body).backgroundColor")
    check("el interruptor activa data-theme=dark", dp.evaluate("() => document.documentElement.dataset.theme") == "dark")
    check("el fondo cambia a oscuro", before != after, f"{before} -> {after}")
    dp.reload(wait_until="networkidle")
    check("la preferencia persiste al recargar", dp.evaluate("() => document.documentElement.dataset.theme") == "dark")
    dp.goto(f"{WEB}/reserva/{token2}", wait_until="networkidle")
    shot(dp, "10_oscuro_gestion")
    check("la página de gestión también es oscura", dp.evaluate("() => document.documentElement.dataset.theme") == "dark")

    browser.close()

# ====================================================================== errores de consola
section("8. Errores de JavaScript durante toda la sesión")
ignorar = ("Failed to load resource", "tile.openstreetmap", "ERR_", "net::")
reales = [e for e in page_errors if not any(k in e for k in ignorar)]
check("sin errores de JavaScript en consola", not reales, " | ".join(reales[:3]))

print("\n" + "=" * 60)
print(f"RESULTADO UI: {len(passed)} pruebas OK, {len(failed)} con fallo")
for f in failed:
    print("  -", f)
sys.exit(1 if failed else 0)
