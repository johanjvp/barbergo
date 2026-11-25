"""
Envía un correo de prueba con la configuración de backend/.env (Resend o SMTP).

Uso (desde la carpeta backend):
    .venv/Scripts/python send_test_email.py tucorreo@gmail.com

Muestra por qué falla si algo está mal configurado (clave incorrecta, 2FA, etc.).
"""

import os
import smtplib
import sys

from dotenv import load_dotenv

load_dotenv()

if len(sys.argv) < 2:
    sys.exit("Uso: python send_test_email.py destinatario@correo.com")

to = sys.argv[1]

if os.getenv("RESEND_API_KEY"):
    mode = "Resend"
elif os.getenv("SMTP_HOST"):
    mode = f"SMTP ({os.getenv('SMTP_HOST')}:{os.getenv('SMTP_PORT', '587')} como {os.getenv('SMTP_USER')})"
else:
    sys.exit("No hay proveedor configurado: completa RESEND_API_KEY o las variables SMTP_* en backend/.env")

print(f"Proveedor: {mode}")
print(f"Enviando a: {to} ...")

# Diagnóstico explícito de SMTP para mostrar el motivo real de un fallo.
if mode.startswith("SMTP"):
    try:
        import ssl

        host = os.environ["SMTP_HOST"]
        port = int(os.getenv("SMTP_PORT", "587"))
        security = os.getenv("SMTP_SECURITY", "starttls").lower()
        ctx = ssl.create_default_context()
        server = smtplib.SMTP_SSL(host, port, timeout=20, context=ctx) if security == "ssl" else smtplib.SMTP(host, port, timeout=20)
        with server:
            if security == "starttls":
                server.starttls(context=ctx)
            server.login(os.getenv("SMTP_USER", ""), os.getenv("SMTP_PASSWORD", ""))
        print("  [OK] conexión y autenticación correctas")
    except smtplib.SMTPAuthenticationError as e:
        sys.exit(
            "  [FALLO] El servidor rechazó el usuario/clave.\n"
            "          Con Gmail debes usar una 'contraseña de aplicación' de 16 caracteres "
            "(requiere verificación en dos pasos), no la contraseña normal.\n"
            f"          Detalle: {e.smtp_code} {e.smtp_error!r}"
        )
    except Exception as e:  # noqa: BLE001
        sys.exit(f"  [FALLO] No se pudo conectar al servidor SMTP: {e!r}")

from app.services.notification_service import NotificationService, _layout  # noqa: E402

html_body = _layout(
    "¡Todo funciona!",
    "Este es un correo de prueba de BarberGo. Si lo estás leyendo, las notificaciones por correo ya están configuradas.",
    [("Proveedor", mode)],
)
ok = NotificationService.send(to, "Prueba de correo · BarberGo", html_body)
print("  [OK] correo enviado. Revisa tu bandeja (y spam)." if ok else "  [FALLO] el envío no se completó; revisa el mensaje de error de arriba.")
sys.exit(0 if ok else 1)
