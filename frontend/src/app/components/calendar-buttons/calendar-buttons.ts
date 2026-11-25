import { Component, Input } from '@angular/core';

import { CalendarEvent, downloadIcs, googleCalendarUrl } from '../../utils/calendar';
import { Icon } from '../icon/icon';

/** «Agregar a Google Calendar» + descarga .ics (Apple, Outlook...). */
@Component({
  selector: 'app-calendar-buttons',
  standalone: true,
  imports: [Icon],
  template: `
    <div class="cal">
      <a class="google" [href]="google" target="_blank" rel="noopener noreferrer">
        <app-icon name="calendar"></app-icon>
        Agregar a Google Calendar
      </a>
      <button type="button" class="ics" (click)="download()" title="Compatible con Apple Calendar y Outlook">
        <app-icon name="download"></app-icon>
        .ics
      </button>
    </div>
  `,
  styles: [`
    :host { display: block; }
    .cal { display: flex; flex-wrap: wrap; gap: 8px; }
    a, button {
      display: inline-flex; align-items: center; justify-content: center; gap: 8px;
      padding: 10px 16px; border: 1px solid var(--border); border-radius: 980px;
      background: var(--surface); color: var(--ink); font-size: 13px; font-weight: 600;
      text-decoration: none; cursor: pointer; transition: background .2s, border-color .2s;
    }
    a:hover, button:hover { background: var(--surface-2); border-color: rgba(0, 0, 0, .14); }
    app-icon { color: var(--primary-600); font-size: 16px; }
  `]
})
export class CalendarButtons {
  @Input({ required: true }) event!: CalendarEvent;

  get google(): string {
    return googleCalendarUrl(this.event);
  }

  download(): void {
    downloadIcs(this.event);
  }
}
