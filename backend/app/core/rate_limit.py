"""
Limitador de peticiones en memoria (por clave, ventana deslizante).

Suficiente para una sola instancia. Si se despliega con varias
instancias, conviene sustituirlo por Redis.

Variables de entorno:
  TRUST_PROXY=1            confiar en X-Forwarded-For (solo detrás de un proxy propio)
  RATE_LIMIT_MULTIPLIER=N  multiplica los límites (útil en pruebas e2e)
"""

import os
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request, status

_hits: dict[str, deque] = defaultdict(deque)
_lock = Lock()


def client_ip(request: Request) -> str:
    # X-Forwarded-For lo controla el cliente: solo se usa si hay un proxy de confianza.
    if os.getenv("TRUST_PROXY") == "1":
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(key: str, max_hits: int, window_seconds: int) -> None:
    limit = max_hits * max(1, int(os.getenv("RATE_LIMIT_MULTIPLIER", "1")))
    now = time.monotonic()
    with _lock:
        q = _hits[key]
        while q and now - q[0] > window_seconds:
            q.popleft()
        if len(q) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiados intentos. Espera unos minutos e inténtalo de nuevo.",
            )
        q.append(now)
