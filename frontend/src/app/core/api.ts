/**
 * URL base de la API.
 *
 *  - En tu equipo (localhost / 127.0.0.1): el backend local en el puerto 8000.
 *  - En producción (Vercel): ruta relativa /api/v1 (mismo dominio, sin CORS).
 */
const isLocal =
  typeof location !== 'undefined' &&
  (location.hostname === 'localhost' || location.hostname === '127.0.0.1');

export const API_URL = isLocal ? 'http://127.0.0.1:8000/api/v1' : '/api/v1';
