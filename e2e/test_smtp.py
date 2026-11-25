"""
Prueba el envío por SMTP contra un servidor SMTP falso local (sin internet ni cuentas reales).

Uso:  backend/.venv/Scripts/python e2e/test_smtp.py
"""

import os
import socketserver
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import env  # noqa: E402

env.apply()
os.environ["RESEND_API_KEY"] = ""

received = {"commands": [], "data": ""}


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        w = lambda s: self.wfile.write((s + "\r\n").encode())
        w("220 fake.smtp ESMTP")
        in_data = False
        while True:
            line = self.rfile.readline()
            if not line:
                break
            text = line.decode(errors="replace").rstrip("\r\n")
            if in_data:
                if text == ".":
                    in_data = False
                    w("250 OK queued")
                else:
                    received["data"] += text + "\n"
                continue
            cmd = text.upper()
            received["commands"].append(text.split(" ")[0].upper())
            if cmd.startswith("EHLO") or cmd.startswith("HELO"):
                w("250-fake.smtp")
                w("250 AUTH PLAIN LOGIN")
            elif cmd.startswith("AUTH"):
                received["auth"] = text
                w("235 Authentication successful")
            elif cmd.startswith("MAIL FROM") or cmd.startswith("RCPT TO"):
                received.setdefault("addr", []).append(text)
                w("250 OK")
            elif cmd == "DATA":
                in_data = True
                w("354 End data with <CR><LF>.<CR><LF>")
            elif cmd == "QUIT":
                w("221 Bye")
                break
            else:
                w("250 OK")


server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Handler)
port = server.server_address[1]
threading.Thread(target=server.serve_forever, daemon=True).start()

os.environ.update({
    "SMTP_HOST": "127.0.0.1", "SMTP_PORT": str(port), "SMTP_SECURITY": "none",
    "SMTP_USER": "usuario-prueba", "SMTP_PASSWORD": "clave-de-prueba",
    "SMTP_FROM": "BarberGo <no-reply@ejemplo.test>",
})

from app.services.notification_service import NotificationService  # noqa: E402

ok = NotificationService.send("cliente@ejemplo.test", "Prueba SMTP · BarberGo", "<p>Hola <b>mundo</b></p><a href=\"http://x/reserva/abc\">Ir</a>")
server.shutdown()

checks = {
    "send() devuelve True": ok is True,
    "habló SMTP (EHLO, AUTH, MAIL, RCPT, DATA)": all(c in received["commands"] for c in ("EHLO", "AUTH", "MAIL", "RCPT", "DATA")),
    "autenticó con usuario y clave": "AUTH" in received.get("auth", ""),
    "remitente y destinatario correctos": any("no-reply@ejemplo.test" in a for a in received.get("addr", [])) and any("cliente@ejemplo.test" in a for a in received.get("addr", [])),
    "asunto correcto": "Subject:" in received["data"] and "Prueba SMTP" in received["data"],
    "incluye HTML y versión de texto": "text/html" in received["data"] and "text/plain" in received["data"],
}
for k, v in checks.items():
    print(("  [OK]    " if v else "  [FALLO] ") + k)

# Un SMTP caído no debe lanzar excepción (la reserva no puede fallar por un correo)
os.environ["SMTP_PORT"] = "1"
print(("  [OK]    " if NotificationService.send("a@b.co", "x", "<p>x</p>") is False else "  [FALLO] ") + "SMTP caído -> devuelve False sin romper")

bad = [k for k, v in checks.items() if not v]
print(f"\nRESULTADO SMTP: {len(checks) + 1 - len(bad)} OK, {len(bad)} con fallo")
sys.exit(1 if bad else 0)
