"""
Punto de entrada de la API en Vercel (función serverless de Python).

Vercel busca una variable ASGI llamada `app` en api/*.py. Aquí se reutiliza la
aplicación FastAPI que vive en backend/app. Las rutas siguen siendo /api/v1/...
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))

from app.main import app  # noqa: E402,F401  (Vercel detecta `app`)
