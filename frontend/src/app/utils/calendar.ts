/**
 * Utilidades para agregar una reserva al calendario del usuario.
 * Las horas de las reservas son locales (sin zona horaria) de Colombia.
 */

export interface CalendarEvent {
  title: string;
  /** Fecha/hora local ISO sin zona: 2026-12-02T10:30:00 */
  start: string;
  end: string;
  location?: string | null;
  description?: string | null;
  /** Identificador estable (evita duplicados si se importa dos veces) */
  uid?: string;
}

export const CALENDAR_TIMEZONE = 'America/Bogota';

/** 2026-12-02T10:30:00 -> 20261202T103000 */
function compact(iso: string): string {
  const digits = iso.replace(/\D/g, '');
  const date = digits.slice(0, 8);
  const time = (digits.slice(8, 14) || '000000').padEnd(6, '0');
  return `${date}T${time}`;
}

function escapeIcs(text: string): string {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/;/g, '\\;')
    .replace(/,/g, '\\,')
    .replace(/\r?\n/g, '\\n');
}

/** Enlace directo para crear el evento en Google Calendar. */
export function googleCalendarUrl(event: CalendarEvent): string {
  const params = new URLSearchParams({
    action: 'TEMPLATE',
    text: event.title,
    dates: `${compact(event.start)}/${compact(event.end)}`,
    ctz: CALENDAR_TIMEZONE
  });

  if (event.description) params.set('details', event.description);
  if (event.location) params.set('location', event.location);

  return `https://calendar.google.com/calendar/render?${params.toString()}`;
}

/** Contenido .ics (Apple Calendar, Outlook, Google, etc.) con recordatorio 1 h antes. */
export function buildIcs(event: CalendarEvent): string {
  const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
  const uid = event.uid ?? `${compact(event.start)}-${Math.random().toString(36).slice(2)}@barbergo`;

  const lines = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//BarberGo//Reservas//ES',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'BEGIN:VEVENT',
    `UID:${uid}`,
    `DTSTAMP:${stamp}`,
    `DTSTART;TZID=${CALENDAR_TIMEZONE}:${compact(event.start)}`,
    `DTEND;TZID=${CALENDAR_TIMEZONE}:${compact(event.end)}`,
    `SUMMARY:${escapeIcs(event.title)}`
  ];

  if (event.location) lines.push(`LOCATION:${escapeIcs(event.location)}`);
  if (event.description) lines.push(`DESCRIPTION:${escapeIcs(event.description)}`);

  lines.push(
    'BEGIN:VALARM',
    'ACTION:DISPLAY',
    `DESCRIPTION:${escapeIcs(event.title)}`,
    'TRIGGER:-PT1H',
    'END:VALARM',
    'END:VEVENT',
    'END:VCALENDAR'
  );

  return lines.join('\r\n');
}

/** Descarga el evento como archivo .ics. */
export function downloadIcs(event: CalendarEvent, filename = 'reserva-barbergo.ics'): void {
  const blob = new Blob([buildIcs(event)], { type: 'text/calendar;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
