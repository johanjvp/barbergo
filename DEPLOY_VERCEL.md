# Despliegue en Vercel

Un solo proyecto de Vercel sirve **todo**: el frontend (Angular, archivos estáticos) y la API
(FastAPI como función de Python). Como comparten dominio, el frontend llama a `/api/v1/...` y **no hay CORS**.

```
tu-sitio.vercel.app/            -> Angular  (frontend/dist/frontend/browser)
tu-sitio.vercel.app/api/v1/...  -> FastAPI  (api/index.py -> backend/app)
```

## Qué necesitas

1. Una cuenta de **GitHub** y una de **Vercel**.
2. Una **base de datos MySQL en la nube** (Vercel no aloja MySQL). Opciones compatibles con MySQL que
   suelen tener plan gratuito o de prueba (verifica condiciones vigentes): TiDB Cloud Serverless, Aiven,
   Railway, Clever Cloud. Casi todas exigen TLS: se activa con `DB_SSL=true`.
3. El proveedor de correo que ya configuraste (Gmail con clave de aplicación o Resend).

## Paso a paso

### 1. Subir el proyecto a GitHub
`backend/.env` **no** se sube (está ignorado). Verifica con `git status` que no aparezca.

### 2. Crear la base de datos en la nube
Crea una base vacía (por ejemplo `barbergo`) y anota host, puerto, usuario y clave.

### 3. Inicializar las tablas (una sola vez, desde tu PC)
En PowerShell, dentro de `backend`:

```powershell
$env:DB_HOST="host-de-tu-proveedor"; $env:DB_PORT="4000"; $env:DB_USER="usuario"
$env:DB_PASSWORD="clave"; $env:DB_NAME="barbergo"; $env:DB_SSL="true"; $env:JWT_SECRET_KEY="x"
.venv\Scripts\python init_db.py --admin-email tu@correo.com --admin-password "UnaClaveSegura123"
```

Crea las tablas, los roles, los estados de reserva y tu usuario **administrador de la plataforma**.
Se puede repetir sin problema.

### 4. Crear el proyecto en Vercel
**Add New > Project > Import** tu repositorio, y deja:

| Campo | Valor |
|---|---|
| Framework Preset | **Other** |
| Root Directory | `./` (la raíz del repositorio) |
| Build / Install / Output | los toma de `vercel.json` (no los cambies) |

### 5. Variables de entorno (Settings > Environment Variables)

| Variable | Valor |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | los de tu base en la nube |
| `DB_SSL` | `true` (si el proveedor exige TLS) |
| `JWT_SECRET_KEY` | cadena larga aleatoria. En PowerShell: `-join ((48..57)+(65..90)+(97..122) \| Get-Random -Count 48 \| % {[char]$_})` |
| `FRONTEND_URL` | `https://tu-sitio.vercel.app` (los enlaces de los correos apuntan aquí) |
| `SMTP_HOST` `SMTP_PORT` `SMTP_USER` `SMTP_PASSWORD` `SMTP_SECURITY` `SMTP_FROM` | tu configuración de Gmail (ver `backend/.env`) |
| *(o)* `RESEND_API_KEY` y `RESEND_FROM_EMAIL` | si usas Resend |
| `CRON_SECRET` | cadena aleatoria (protege el endpoint de recordatorios) |
| `TRUST_PROXY` | `1` (usa la IP real del cliente para los límites de intentos) |
| `ADMIN_NOTIFY_EMAIL` | *(opcional)* recibe aviso de solicitudes de domicilio |

Pulsa **Deploy**.

### 6. Comprobar
- `https://tu-sitio.vercel.app/` carga la portada con tus barberías.
- `https://tu-sitio.vercel.app/docs` muestra la documentación de la API.
- Inicia sesión con el administrador del paso 3.

### 7. Recordatorios de citas (24 h y 2 h antes)
En Vercel no hay procesos permanentes, así que un programador llama a `/api/v1/cron/reminders`.
El repositorio ya trae `.github/workflows/reminders.yml` (gratis). En GitHub, **Settings > Secrets and
variables > Actions**, crea:

- `APP_URL` = `https://tu-sitio.vercel.app`
- `CRON_SECRET` = el mismo valor que pusiste en Vercel

Alternativa en un plan Pro de Vercel: añade a `vercel.json`
`"crons": [{ "path": "/api/v1/cron/reminders", "schedule": "*/10 * * * *" }]`
(los planes gratuitos solo permiten una ejecución diaria, por eso no viene incluido).

## Qué cambia respecto a tu equipo

- **Correos:** en Vercel se envían *dentro* de la petición (las funciones se congelan al responder), así que
  confirmar una reserva tarda 1-2 s más que en local.
- **Límite de intentos** (códigos, reservas de invitado): vive en memoria de cada instancia; en serverless
  puede haber varias, así que el límite es más laxo que en un servidor único. Para endurecerlo, usa Redis
  (por ejemplo Upstash).
- **Primera petición lenta:** una función "fría" tarda unos segundos en arrancar (conecta a la base y verifica
  el esquema).
- **Tiempo máximo por petición:** 30 s (`vercel.json`).
- **Python:** si Vercel se queja de la versión, `.python-version` fija 3.12.

## Si algo falla
- **500 en `/api/...`**: Vercel > tu proyecto > **Logs**. Lo más común: variables `DB_*` mal escritas o falta `DB_SSL=true`.
- **No llegan correos**: revisa los logs buscando `ERROR ENVIANDO CORREO`.
- **Pantalla en blanco al recargar una ruta**: comprueba que `vercel.json` esté en la raíz del repositorio.

## Probado y no probado
Probado en local: la API arrancando desde `api/index.py` con `VERCEL=1`, el frontend compilado servido con las
mismas reglas de `vercel.json` desde otro dominio, enlaces directos, correos en línea, el endpoint de
recordatorios y `init_db.py` sobre una base vacía (`python e2e/test_vercel_sim.py`).
**No** se probó un despliegue real (requiere tu cuenta) ni una base de datos de un proveedor concreto en la nube.
