"""
Notificaciones por correo de BarberGo.

Usa Resend (mismas variables que el servicio de confirmación existente):

    RESEND_API_KEY      clave de Resend
    RESEND_FROM_EMAIL   remitente, p. ej. "BarberGo <no-reply@tu-dominio.com>"

  Alternativa SMTP (cualquier proveedor: Brevo, Mailjet, SendGrid, Zoho, Gmail con
  contraseña de aplicación...). Se usa solo si NO hay RESEND_API_KEY:
    SMTP_HOST, SMTP_PORT (587), SMTP_USER, SMTP_PASSWORD,
    SMTP_SECURITY (starttls | ssl, por defecto starttls), SMTP_FROM
    FRONTEND_URL        base de los enlaces, p. ej. https://barbergo.com
    ADMIN_NOTIFY_EMAIL  (opcional) recibe avisos de solicitudes de domicilio

Sin RESEND_API_KEY no se envía nada: el correo se imprime en consola
para poder probar el flujo en desarrollo (códigos, enlaces, etc.).
"""

import html
import os
import threading
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import Session

load_dotenv()

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def _e(value) -> str:
    return html.escape(str(value or ""))


def _money(value) -> str:
    try:
        return "$" + f"{float(value):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return ""


def _when(dt: datetime) -> str:
    return f"{DIAS[dt.weekday()]} {dt.day} de {MESES[dt.month - 1]} de {dt.year}, {dt:%H:%M}"


PAYMENT_LABELS = {
    "CASH": "Efectivo",
    "BANK_TRANSFER": "Transferencia bancaria",
    "DEPOSIT": "Consignación",
    "NEQUI": "Nequi",
    "DAVIPLATA": "Daviplata",
}


def payment_rows(ctx: dict) -> list[tuple[str, str]]:
    method = ctx.get("payment_method")
    if not method:
        return []
    rows = [("Forma de pago", PAYMENT_LABELS.get(method, method))]
    if method == "CASH":
        rows.append(("Cómo pagar", "Pagas en efectivo al recibir el servicio."))
        return rows
    if method in ("NEQUI", "DAVIPLATA"):
        rows.append((f"Número {PAYMENT_LABELS[method]}", ctx.get("account_number") or ""))
    else:
        rows.append(("Banco", ctx.get("bank_name") or ""))
        rows.append(("Tipo de cuenta", ctx.get("account_type") or ""))
        rows.append(("Número de cuenta", ctx.get("account_number") or ""))
    rows.append(("A nombre de", ctx.get("account_holder") or ""))
    if ctx.get("holder_document"):
        rows.append(("Documento", ctx["holder_document"]))
    if ctx.get("pay_instructions"):
        rows.append(("Indicaciones", ctx["pay_instructions"]))
    status = ctx.get("payment_status")
    rows.append(("Estado del pago", {"PAID": "Pagado", "REPORTED": "Pago reportado, en verificación"}.get(status, "Pendiente")))
    return rows


def google_calendar_url(ctx: dict) -> str:
    """Enlace para crear el evento en Google Calendar (hora local de Colombia)."""
    from urllib.parse import urlencode

    def stamp(dt: datetime) -> str:
        return dt.strftime("%Y%m%dT%H%M%S")

    home = ctx.get("booking_type") == "HOME"
    location = ctx.get("home_address") if home else ctx.get("shop_address")
    details = f"Barbero: {ctx.get('barber_name', '')}\nReserva #{ctx['id']}"
    if ctx.get("manage_token"):
        details += f"\nGestiónala en: {frontend_url()}/reserva/{ctx['manage_token']}"

    params = {
        "action": "TEMPLATE",
        "text": f"{ctx['service_name']} · {ctx['shop_name']}",
        "dates": f"{stamp(ctx['start_at'])}/{stamp(ctx['end_at'])}",
        "details": details,
        "location": location or "",
        "ctz": "America/Bogota",
    }
    return "https://calendar.google.com/calendar/render?" + urlencode(params)


def frontend_url() -> str:
    return os.getenv("FRONTEND_URL", "http://localhost:4200").rstrip("/")


# =========================================================
# PLANTILLA BASE
# =========================================================
def _layout(title: str, intro: str, rows: list[tuple[str, str]] | None = None,
            cta: tuple[str, str] | None = None, footer: str = "",
            extra_links: list[tuple[str, str]] | None = None) -> str:
    rows_html = ""
    if rows:
        rows_html = "".join(
            f'<tr><td style="padding:10px 0;color:#64748b;font-size:13px;width:38%;'
            f'border-bottom:1px solid #e5eeec">{_e(k)}</td>'
            f'<td style="padding:10px 0;color:#0b1f2a;font-size:14px;font-weight:600;'
            f'border-bottom:1px solid #e5eeec">{_e(v)}</td></tr>'
            for k, v in rows if v
        )
        rows_html = f'<table width="100%" cellpadding="0" cellspacing="0" style="margin:22px 0">{rows_html}</table>'

    cta_html = ""
    if cta:
        cta_html = (
            f'<p style="margin:26px 0"><a href="{_e(cta[1])}" style="display:inline-block;'
            f'padding:14px 26px;border-radius:12px;background:#0d9488;color:#ffffff;'
            f'font-weight:700;text-decoration:none">{_e(cta[0])}</a></p>'
        )

    links_html = ""
    if extra_links:
        links_html = '<p style="margin:0 0 6px">' + " &nbsp;·&nbsp; ".join(
            f'<a href="{_e(u)}" style="color:#0f766e;font-weight:600;font-size:14px;text-decoration:none">{_e(l)}</a>'
            for l, u in extra_links
        ) + "</p>"

    return f"""<!doctype html>
<html lang="es"><body style="margin:0;background:#f2f7f6;font-family:Inter,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="padding:32px 12px"><tr><td align="center">
  <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%">
    <tr><td style="padding:0 4px 18px;font-size:22px;font-weight:800;color:#0f766e">&#9986; BarberGo</td></tr>
    <tr><td style="background:#ffffff;border-radius:22px;padding:34px;border:1px solid #dfeae8">
      <h1 style="margin:0 0 12px;font-size:24px;color:#0b1f2a;letter-spacing:-.02em">{_e(title)}</h1>
      <p style="margin:0;color:#3b5560;line-height:1.65;font-size:15px">{intro}</p>
      {rows_html}{cta_html}{links_html}
      <p style="margin:18px 0 0;color:#64748b;font-size:12px;line-height:1.6">{footer}</p>
    </td></tr>
    <tr><td style="padding:18px 4px;color:#8fa6a2;font-size:12px">
      Este correo fue enviado por BarberGo. Si no esperabas este mensaje, puedes ignorarlo.
    </td></tr>
  </table>
</td></tr></table></body></html>"""


def _dev_print(message: str) -> None:
    """print() que no falla con consolas que no admiten ciertos caracteres (Windows cp1252)."""
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "replace").decode("ascii"))


class NotificationService:

    # =====================================================
    # ENVÍO
    # =====================================================
    @staticmethod
    def send(to: str | None, subject: str, html_body: str) -> bool:
        if not to:
            return False

        api_key = os.getenv("RESEND_API_KEY")
        smtp_host = os.getenv("SMTP_HOST")

        if api_key:
            return NotificationService._send_resend(api_key, to, subject, html_body)

        if smtp_host:
            return NotificationService._send_smtp(smtp_host, to, subject, html_body)

        # Sin proveedor configurado: se imprime para poder probar en desarrollo.
        _dev_print(f"[EMAIL-DEV] Para: {to} | Asunto: {subject}")
        import re
        for url in re.findall(r'href="([^"]+)"', html_body):
            _dev_print(f"[EMAIL-DEV]   enlace: {url}")
        m = re.search(r'letter-spacing:8px[^>]*>([0-9]{6})<', html_body)
        if m:
            _dev_print(f"[EMAIL-DEV]   código: {m.group(1)}")
        plain = re.sub(r"<[^>]+>", " ", html_body)
        plain = " ".join(html.unescape(plain).split())
        _dev_print(f"[EMAIL-DEV]   cuerpo: {plain[:900]}")
        return False

    @staticmethod
    def _send_resend(api_key: str, to: str, subject: str, html_body: str) -> bool:
        try:
            import resend
            resend.api_key = api_key
            resend.Emails.send({
                "from": os.getenv("RESEND_FROM_EMAIL", "BarberGo <onboarding@resend.dev>"),
                "to": [to],
                "subject": subject,
                "html": html_body,
            })
            return True
        except Exception as error:  # un correo fallido nunca debe romper la reserva
            print("ERROR ENVIANDO CORREO (Resend):", repr(error))
            return False

    @staticmethod
    def _send_smtp(host: str, to: str, subject: str, html_body: str) -> bool:
        import re
        import smtplib
        import ssl
        from email.message import EmailMessage
        from email.utils import formataddr, parseaddr

        user = os.getenv("SMTP_USER", "")
        password = os.getenv("SMTP_PASSWORD", "")
        port = int(os.getenv("SMTP_PORT", "587"))
        security = os.getenv("SMTP_SECURITY", "starttls").lower()
        sender = os.getenv("SMTP_FROM") or formataddr(("BarberGo", user))

        try:
            msg = EmailMessage()
            msg["From"] = sender
            msg["To"] = to
            msg["Subject"] = subject
            plain = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", html_body)).split())
            msg.set_content(plain)
            msg.add_alternative(html_body, subtype="html")

            context = ssl.create_default_context()
            if security == "ssl":
                server = smtplib.SMTP_SSL(host, port, timeout=20, context=context)
            else:
                server = smtplib.SMTP(host, port, timeout=20)
            with server:
                if security == "starttls":
                    server.starttls(context=context)
                if user and password:
                    server.login(user, password)
                server.send_message(msg, from_addr=parseaddr(sender)[1])
            return True
        except Exception as error:
            print("ERROR ENVIANDO CORREO (SMTP):", repr(error))
            return False

    @staticmethod
    def send_async(to: str | None, subject: str, html_body: str) -> None:
        # Serverless (Vercel): la función se congela al responder, un hilo no terminaría.
        if os.getenv("VERCEL"):
            NotificationService.send(to, subject, html_body)
            return

        threading.Thread(
            target=NotificationService.send,
            args=(to, subject, html_body),
            daemon=True,
        ).start()

    # =====================================================
    # CÓDIGO DE VERIFICACIÓN
    # =====================================================
    @staticmethod
    def send_verification_code(email: str, code: str, minutes: int) -> None:
        body = _layout(
            "Tu código de verificación",
            "Usa este código para confirmar tu reserva en BarberGo:"
            f'<div style="margin:22px 0;padding:18px;border-radius:14px;background:#e6f7f4;'
            f'text-align:center;font-size:34px;font-weight:800;letter-spacing:8px;color:#0f766e">{_e(code)}</div>',
            footer=f"El código vence en {minutes} minutos. Si no lo pediste tú, ignora este mensaje.",
        )
        NotificationService.send_async(email, "Tu código de verificación de BarberGo", body)

    # =====================================================
    # DATOS DE UNA RESERVA
    # =====================================================
    @staticmethod
    def booking_context(db: Session, booking_id: int) -> dict | None:
        row = db.execute(text("""
            SELECT b.id, b.client_user_id, b.guest_name, b.guest_email, b.manage_token,
                   b.start_at, b.end_at, b.service_price, b.home_fee, b.booking_type,
                   b.home_address, b.reminder_24h_sent_at, b.reminder_2h_sent_at,
                   bs.name AS shop_name, bs.address AS shop_address, bs.phone AS shop_phone,
                   s.name AS service_name,
                   CONCAT(ub.first_name, ' ', ub.last_name) AS barber_name,
                   uc.email AS client_email,
                   CONCAT(uc.first_name, ' ', uc.last_name) AS client_name,
                   st.code AS status_code,
                   b.payment_method, b.payment_status,
                   pm.bank_name, pm.account_type, pm.account_number,
                   pm.account_holder, pm.holder_document, pm.instructions AS pay_instructions
            FROM bookings b
            JOIN barbershops bs ON bs.id = b.barbershop_id
            JOIN services s ON s.id = b.service_id
            JOIN barbers br ON br.id = b.barber_id
            JOIN users ub ON ub.id = br.user_id
            JOIN booking_statuses st ON st.id = b.status_id
            LEFT JOIN users uc ON uc.id = b.client_user_id
            LEFT JOIN barbershop_payment_methods pm
                   ON pm.barbershop_id = b.barbershop_id AND pm.method = b.payment_method
            WHERE b.id = :id
            LIMIT 1
        """), {"id": booking_id}).mappings().first()

        if not row:
            return None

        ctx = dict(row)
        ctx["to_email"] = ctx.get("client_email") or ctx.get("guest_email")
        ctx["to_name"] = (ctx.get("client_name") or ctx.get("guest_name") or "").strip()
        ctx["is_guest"] = ctx.get("client_user_id") is None
        return ctx

    @staticmethod
    def _booking_rows(ctx: dict) -> list[tuple[str, str]]:
        home = ctx.get("booking_type") == "HOME"
        total = float(ctx["service_price"] or 0) + float(ctx.get("home_fee") or 0)
        rows = [
            ("Servicio", ctx["service_name"]),
            ("Barbería", ctx["shop_name"]),
            ("Barbero", ctx["barber_name"]),
            ("Fecha y hora", _when(ctx["start_at"])),
            ("Lugar", ("A domicilio: " + (ctx.get("home_address") or "")) if home
                else (ctx.get("shop_address") or "")),
        ]
        if home and float(ctx.get("home_fee") or 0) > 0:
            rows.append(("Desplazamiento", _money(ctx["home_fee"])))
        rows.append(("Total", _money(total)))
        rows.append(("Reserva", f"#{ctx['id']}"))
        rows += payment_rows(ctx)
        return rows

    @staticmethod
    def manage_link(ctx: dict) -> str | None:
        if ctx.get("manage_token"):
            return f"{frontend_url()}/reserva/{ctx['manage_token']}"
        return None

    # =====================================================
    # EVENTOS DE RESERVA
    # =====================================================
    @staticmethod
    def booking_event(db: Session, booking_id: int, event: str) -> None:
        """
        event: CREATED_GUEST | CONFIRMED | REJECTED | CANCELLED |
               REMINDER_24H | REMINDER_2H
        """
        try:
            ctx = NotificationService.booking_context(db, booking_id)
            if not ctx or not ctx["to_email"]:
                return

            name = _e(ctx["to_name"].split(" ")[0] if ctx["to_name"] else "")
            hello = f"Hola {name}, " if name else "Hola, "
            link = NotificationService.manage_link(ctx)
            rows = NotificationService._booking_rows(ctx)
            pending = ctx["status_code"] == "PENDING"
            home = ctx.get("booking_type") == "HOME"

            manage_cta = ("Ver o cancelar mi reserva", link) if link else None
            manage_note = (
                "Guarda este correo: el botón es tu acceso para ver o cancelar la cita sin cuenta."
                if link else ""
            )

            if event == "CREATED_GUEST":
                subject = "Recibimos tu solicitud de reserva" if pending else "Tu reserva está confirmada"
                title = "¡Solicitud recibida!" if pending else "¡Reserva confirmada!"
                intro = hello + (
                    "tu solicitud quedó registrada y la barbería la confirmará en breve."
                    if pending else "tu cita quedó confirmada. Te esperamos."
                )
                if home:
                    intro += " Recuerda tener un espacio con buena luz y una silla lista."
                cal = [] if pending else [("Agregar a Google Calendar", google_calendar_url(ctx))]
                body = _layout(title, intro, rows, manage_cta, manage_note, extra_links=cal)

            elif event == "CONFIRMED":
                subject, title = "Tu reserva fue confirmada", "¡Reserva confirmada!"
                body = _layout(title, hello + "la barbería confirmó tu cita.", rows, manage_cta, manage_note,
                               extra_links=[("Agregar a Google Calendar", google_calendar_url(ctx))])

            elif event == "REJECTED":
                subject, title = "Tu reserva no pudo ser confirmada", "No pudimos confirmar tu reserva"
                body = _layout(
                    title,
                    hello + "lamentablemente la barbería no pudo atender esta cita. "
                    "Puedes elegir otro horario o barbero.",
                    rows, ("Buscar otro horario", f"{frontend_url()}/barberias"),
                )

            elif event == "CANCELLED":
                subject, title = "Tu reserva fue cancelada", "Reserva cancelada"
                body = _layout(
                    title, hello + "tu reserva fue cancelada. Cuando quieras, agenda una nueva cita.",
                    rows, ("Reservar de nuevo", f"{frontend_url()}/barberias"),
                )

            elif event in ("REMINDER_24H", "REMINDER_2H"):
                soon = event == "REMINDER_2H"
                subject = "Tu cita es en 2 horas" if soon else "Tu cita es mañana"
                title = "Tu cita es en 2 horas" if soon else "Recordatorio: tu cita es mañana"
                body = _layout(title, hello + "te recordamos tu próxima cita.", rows, manage_cta, manage_note)

            else:
                return

            NotificationService.send_async(ctx["to_email"], subject + " · BarberGo", body)

        except Exception as error:
            print("ERROR NOTIFICACION RESERVA:", repr(error))

    # =====================================================
    # DOMICILIO
    # =====================================================
    @staticmethod
    def home_service_requested(db: Session, barbershop_id: int) -> None:
        admin_email = os.getenv("ADMIN_NOTIFY_EMAIL")
        if not admin_email:
            return
        row = db.execute(text("SELECT name FROM barbershops WHERE id=:i"), {"i": barbershop_id}).first()
        name = row[0] if row else f"#{barbershop_id}"
        body = _layout(
            "Nueva solicitud de servicio a domicilio",
            f"La barbería <b>{_e(name)}</b> solicitó ofrecer servicio a domicilio y espera tu revisión.",
            cta=("Revisar solicitud", f"{frontend_url()}/admin/barberias/{barbershop_id}"),
        )
        NotificationService.send_async(admin_email, "Solicitud de domicilio pendiente · BarberGo", body)

    @staticmethod
    def home_service_decision(db: Session, barbershop_id: int, approved: bool, reason: str | None) -> None:
        row = db.execute(text("""
            SELECT bs.name, COALESCE(bs.email, u.email) AS email
            FROM barbershops bs LEFT JOIN users u ON u.id = bs.owner_user_id
            WHERE bs.id = :i
        """), {"i": barbershop_id}).first()
        if not row or not row[1]:
            return
        if approved:
            subject, title = "Tu servicio a domicilio fue aprobado", "¡Servicio a domicilio aprobado!"
            intro = (f"<b>{_e(row[0])}</b> ya puede recibir reservas a domicilio. "
                     "Los clientes verán la opción en tu perfil.")
        else:
            subject, title = "Tu solicitud de domicilio fue rechazada", "Solicitud de domicilio rechazada"
            intro = (f"Revisamos la solicitud de <b>{_e(row[0])}</b> y no pudo ser aprobada."
                     + (f"<br><br><b>Motivo:</b> {_e(reason)}" if reason else "")
                     + "<br><br>Puedes corregir los datos y enviarla de nuevo.")
        NotificationService.send_async(row[1], subject + " · BarberGo", _layout(title, intro))
