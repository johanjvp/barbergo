"""
Corre TODAS las pruebas, en MySQL y en PostgreSQL.

Requisitos (ver e2e/README.md): contenedores barbergo-test-db (MySQL :3399) y barbergo-test-pg
(PostgreSQL :3398) activos, y el frontend en http://localhost:4200 (npm start).

Uso:  python e2e/run_all.py            (Python del sistema con playwright)
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
VENV_PY = str(ROOT / "backend" / ".venv" / "Scripts" / "python.exe")
SYS_PY = sys.executable
results: list[tuple[str, bool, str]] = []


def run(label: str, cmd: list[str], env: dict) -> None:
    t0 = time.time()
    r = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    last = next((l for l in reversed(r.stdout.splitlines()) if "RESULTADO" in l), r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:])
    ok = r.returncode == 0
    results.append((label, ok, last.strip()))
    print(f"{'[OK]   ' if ok else '[FALLO]'} {label:<34} {last.strip()}  ({time.time() - t0:.0f}s)", flush=True)
    if not ok:
        print("\n".join(l for l in r.stdout.splitlines() if "FALLO" in l)[:1500])


def start_backend(db: str):
    sys.path.insert(0, str(ROOT / "e2e"))
    import importlib
    import env as e2e_env
    importlib.reload(e2e_env)
    e = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1", E2E_DB=db)
    e.update(e2e_env.DB_MYSQL if db == "mysql" else e2e_env.DB_POSTGRES)
    e.update({"JWT_SECRET_KEY": "e2e-secret-key-not-for-production-0123456789", "RESEND_API_KEY": "", "SMTP_HOST": "",
              "RATE_LIMIT_MULTIPLIER": "100", "FRONTEND_URL": "http://localhost:4200", "ADMIN_NOTIFY_EMAIL": "plataforma@test.co"})
    log = (ROOT / "e2e" / "backend.log").open("w", encoding="utf-8")
    p = subprocess.Popen([VENV_PY, "-m", "uvicorn", "app.main:app", "--port", "8000"], cwd=str(ROOT / "backend"), env=e, stdout=log, stderr=subprocess.STDOUT)
    for _ in range(40):
        try:
            if httpx.get("http://127.0.0.1:8000/", timeout=2).status_code == 200:
                return p
        except Exception:
            time.sleep(1)
    p.terminate()
    raise SystemExit("el backend no arrancó")


def main() -> None:
    try:
        httpx.get("http://localhost:4200", timeout=5)
    except Exception:
        sys.exit("El frontend no responde en http://localhost:4200 (cd frontend && npm start)")

    for db in ("mysql", "postgres"):
        print(f"\n===== {db.upper()} =====", flush=True)
        env = dict(os.environ, E2E_DB=db, PYTHONIOENCODING="utf-8")
        api = start_backend(db)
        try:
            run(f"{db}: preparar datos", [VENV_PY, "e2e/db_setup.py"], env)
            run(f"{db}: API", [VENV_PY, "e2e/test_api.py"], env)
            run(f"{db}: preparar datos (UI)", [VENV_PY, "e2e/db_setup.py"], env)
            run(f"{db}: interfaz (Chromium)", [SYS_PY, "e2e/test_ui.py"], env)
        finally:
            api.terminate()
            time.sleep(1)
        run(f"{db}: simulación de Vercel", [VENV_PY, "e2e/db_setup.py"], env)
        run(f"{db}: simulación de Vercel (pruebas)", [SYS_PY, "e2e/test_vercel_sim.py"], env)

    print("\n===== COMPARATIVAS =====", flush=True)
    run("paridad MySQL <-> PostgreSQL", [SYS_PY, "e2e/test_parity.py"], dict(os.environ, PYTHONIOENCODING="utf-8"))
    run("envío por SMTP", [VENV_PY, "e2e/test_smtp.py"], dict(os.environ, PYTHONIOENCODING="utf-8"))

    bad = [r for r in results if not r[1]]
    print(f"\nRESUMEN: {len(results) - len(bad)} bloques OK, {len(bad)} con fallo")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
