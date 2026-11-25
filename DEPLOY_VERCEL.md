# Despliegue en Vercel con Neon (PostgreSQL)

Un solo proyecto de Vercel sirve **todo**: el frontend (Angular, archivos estáticos) y la API
(FastAPI como función de Python). Como comparten dominio, el frontend llama a `/api/v1/...` y **no hay CORS**.

```
tu-sitio.vercel.app/            -> Angular  (frontend/dist/frontend/browser)
tu-sitio.vercel.app/api/v1/...  -> FastAPI  (api/index.py -> backend/app)
base de datos                   -> Neon (PostgreSQL)
```

El backend funciona con **PostgreSQL y con MySQL**. Para Neon solo necesitas la variable `DATABASE_URL`.

## Qué necesitas

1. Una cuenta de **GitHub**, una de **Vercel** y una de **Neon** (neon.com).
2. El proveedor de correo que ya configuraste (Gmail con clave de aplicación o Resend).

## Paso a paso

### 1. Subir el proyecto a GitHub
```powershell
git add .
git status        # comprueba que NO aparezca backend/.env
git commit -m "BarberGo"
git push origin jjvega
```
Vercel publica en producción desde la rama principal (normalmente `main`): fusiona `jjvega` en `main`
o cámbialo en Vercel, Settings, Git, Production Branch.

### 2. Crear la base de datos en Neon
1. En neon.com crea un **proyecto** (elige la región más cercana a tus usuarios; Vercel usa `iad1`/Este de EE. UU. por defecto).
2. En el panel, botón **Connect**, copia la cadena de conexión **con pooling** (el host contiene `-pooler`). Se ve así:
   `postgresql://usuario:clave@ep-algo-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require`

> Atajo: en Vercel, **Storage > Create Database > Neon** crea el proyecto y añade `DATABASE_URL`
> automáticamente a tu proyecto de Vercel. Si usas ese camino, salta a los pasos 3 y 4.

### 3. Crear las tablas y tu administrador (una sola vez, desde tu PC)
En PowerShell, dentro de `backend`:

```powershell
$env:DATABASE_URL="postgresql://usuario:clave@ep-algo-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
$env:JWT_SECRET_KEY="x"
.venv\Scripts\python init_db.py --admin-email tu@correo.com --admin-password "UnaClaveSegura123"
```

Debe imprimir `[OK]` en cada línea y terminar con `Listo.`. Crea las tablas, los roles, los estados de
reserva y tu usuario **administrador de la plataforma**. Se puede repetir sin problema.

### 4. Crear el proyecto en Vercel
**Add New > Project > Import** tu repositorio y deja:

| Campo | Valor |
|---|---|
| Framework Preset | **Other** |
| Root Directory | `./` (la raíz del repositorio) |
| Build / Install / Output | los toma de `vercel.json` (no los cambies) |

### 5. Variables de entorno (antes de pulsar Deploy)

| Variable | Valor |
|---|---|
| `DATABASE_URL` | la cadena de Neon del paso 2 (ya existe si usaste la integración de Vercel) |
| `JWT_SECRET_KEY` | cadena larga aleatoria. En PowerShell: `-join ((48..57)+(65..90)+(97..122) \| Get-Random -Count 48 \| % {[char]$_})` |
| `CRON_SECRET` | otra cadena aleatoria (protege el endpoint de recordatorios) |
| `TRUST_PROXY` | `1` (usa la IP real del cliente para los límites de intentos) |
| `FRONTEND_URL` | por ahora `https://placeholder.vercel.app`; se corrige en el paso 7 |
| `SMTP_HOST` `SMTP_PORT` `SMTP_USER` `SMTP_PASSWORD` `SMTP_SECURITY` `SMTP_FROM` | las líneas que ya tienes en `backend/.env` (Vercel acepta pegar varias de golpe) |
| *(o)* `RESEND_API_KEY` y `RESEND_FROM_EMAIL` | si usas Resend |
| `ADMIN_NOTIFY_EMAIL` | *(opcional)* recibe aviso de solicitudes de domicilio |

No hace falta `DB_SSL` ni las variables `DB_*`: con Neon todo va en `DATABASE_URL`.

Pulsa **Deploy** (2 a 4 minutos).

### 6. Comprobar
`https://tu-sitio.vercel.app/` carga la portada, `/docs` muestra la API y `/api/v1/health` responde
`"engine": "postgresql"`. Inicia sesión con el administrador del paso 3.

### 7. Corregir `FRONTEND_URL`
Con la dirección real, cambia `FRONTEND_URL` por `https://tu-sitio.vercel.app` y haz **Redeploy**
(los enlaces de los correos de reserva usan esa variable).

### 8. Recordatorios de citas (24 h y 2 h antes)
En GitHub, Settings, Secrets and variables, Actions, crea:

- `APP_URL` = `https://tu-sitio.vercel.app` (sin barra final)
- `CRON_SECRET` = el mismo valor que pusiste en Vercel

El flujo `.github/workflows/reminders.yml` ya está en el repositorio. Pruébalo en la pestaña **Actions**,
«Recordatorios de citas», **Run workflow**. (Alternativa en un plan Pro de Vercel: añade a `vercel.json`
`"crons": [{ "path": "/api/v1/cron/reminders", "schedule": "*/10 * * * *" }]`.)

## Cosas de Neon que conviene saber
- **Escala a cero:** en el plan gratuito la base se suspende tras unos minutos sin uso; la primera petición
  después tarda un poco más mientras despierta.
- **Usa la cadena con `-pooler`** en producción: las funciones serverless abren muchas conexiones y el pooler las agrupa.
  El backend ya desactiva las sentencias preparadas, que el pooler no admite.
- **Ramas de base de datos:** Neon permite crear una copia de la base para probar cambios sin tocar producción.

## Qué cambia respecto a tu equipo
- **Correos:** en Vercel se envían *dentro* de la petición (las funciones se congelan al responder),
  así que confirmar una reserva tarda 1-2 s más.
- **Límite de intentos** (códigos, reservas de invitado): vive en memoria de cada instancia; en serverless
  puede haber varias, así que es más laxo que en un servidor único. Para endurecerlo, usa Redis (Upstash).
- **Primera petición lenta:** una función "fría" tarda unos segundos en arrancar.
- **Tiempo máximo por petición:** 30 s (`vercel.json`).
- **Python:** `.python-version` fija 3.12.

## Si algo falla
- **500 en `/api/...`**: Vercel > tu proyecto > **Logs**. Lo más común: `DATABASE_URL` mal copiada o con espacios.
- **`/api/v1/health` da 503**: la API no llega a la base; revisa la cadena y que el proyecto de Neon esté activo.
- **No llegan correos**: busca `ERROR ENVIANDO CORREO` en los Logs.
- **Pantalla en blanco al recargar una ruta**: comprueba que `vercel.json` esté en la raíz del repositorio.

## Probado y no probado
**Probado en local, con PostgreSQL 16 y MySQL 8 reales en Docker:** el backend completo en ambas bases (80 pruebas
de API, 61 de interfaz), la paridad de respuestas entre las dos (incluidas las estadísticas del panel de
administración), `init_db.py` sobre una base vacía, la API arrancando desde `api/index.py` con `VERCEL=1`, el frontend
compilado con las reglas de `vercel.json`, y los correos (`python e2e/run_all.py`).

**No probado:** un despliegue real en Vercel (requiere tu cuenta) ni contra un proyecto concreto de Neon
(requiere tu cuenta). La conexión TLS y el pooler de Neon se configuraron según su documentación, no se ejercitaron en vivo.
