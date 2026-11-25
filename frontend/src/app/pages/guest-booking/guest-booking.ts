import { CalendarButtons } from '../../components/calendar-buttons/calendar-buttons';
import { CalendarEvent } from '../../utils/calendar';
import { DatePipe } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { apiError } from '../../components/guest-checkout/guest-checkout';
import { Footer } from '../../components/footer/footer';
import { Icon } from '../../components/icon/icon';
import { Navbar } from '../../components/navbar/navbar';
import { GuestBookingService, GuestBookingView } from '../../services/guest-booking';
import { PAYMENT_LABELS, PaymentApi } from '../../services/payment';
import { FormsModule } from '@angular/forms';
import { ToastService } from '../../services/toast';

const STATUS: Record<string, { label: string; tone: 'ok' | 'wait' | 'bad' | 'info' }> = {
  PENDING: { label: 'Pendiente de confirmación', tone: 'wait' },
  CONFIRMED: { label: 'Confirmada', tone: 'ok' },
  IN_PROGRESS: { label: 'En curso', tone: 'info' },
  COMPLETED: { label: 'Completada', tone: 'info' },
  REJECTED: { label: 'Rechazada por la barbería', tone: 'bad' },
  CANCELLED_BY_CUSTOMER: { label: 'Cancelada por ti', tone: 'bad' },
  CANCELLED_BY_BARBER: { label: 'Cancelada por el barbero', tone: 'bad' },
  CANCELLED_BY_ADMIN: { label: 'Cancelada por la barbería', tone: 'bad' },
  NO_SHOW: { label: 'No asististe', tone: 'bad' }
};

@Component({
  selector: 'app-guest-booking',
  standalone: true,
  imports: [DatePipe, FormsModule, RouterLink, Navbar, Footer, Icon, CalendarButtons],
  template: `
    <app-navbar></app-navbar>

    <main class="page">
      @if (loading) {
        <div class="card skeleton" style="height: 360px"></div>
      } @else if (error) {
        <div class="card center">
          <div class="big bad"><app-icon name="shield"></app-icon></div>
          <h1>No encontramos esta reserva</h1>
          <p>{{ error }}</p>
          <a class="btn" routerLink="/barberias">Buscar barberías</a>
        </div>
      } @else if (b) {
        <article class="card">
          <header>
            <span class="eyebrow">Reserva #{{ b.id }}</span>
            <h1>{{ b.service_name }}</h1>
            <span class="pill" [class]="tone">{{ label }}</span>
          </header>

          <dl>
            <div><dt>Fecha</dt><dd>{{ b.start_at | date: "EEEE d 'de' MMMM, y" : '' : 'es' }}</dd></div>
            <div><dt>Hora</dt><dd>{{ b.start_at | date: 'shortTime' }} – {{ b.end_at | date: 'shortTime' }}</dd></div>
            <div><dt>Barbería</dt><dd>{{ b.barbershop_name }}</dd></div>
            <div><dt>Barbero</dt><dd>{{ b.barber_name }}</dd></div>
            <div>
              <dt>Lugar</dt>
              <dd>{{ b.booking_type === 'HOME' ? 'A domicilio: ' + b.home_address : b.barbershop_address }}</dd>
            </div>
            @if (b.barbershop_phone) { <div><dt>Contacto</dt><dd><a [href]="'tel:' + b.barbershop_phone">{{ b.barbershop_phone }}</a></dd></div> }
            <div class="total"><dt>Total</dt><dd>{{ total }}</dd></div>
          </dl>

@if (isActive && calendarEvent; as ev) {
            <div class="calbox"><app-calendar-buttons [event]="ev"></app-calendar-buttons></div>
          }

          @if (b.payment_method) { <section class="paybox">
              <div class="phead">
                <b>Pago: {{ labels[b.payment_method] }}</b>
                <span class="pill" [class]="b.payment_status === 'PAID' ? 'ok' : b.payment_status === 'REPORTED' ? 'info' : 'wait'">
                  {{ b.payment_status === 'PAID' ? 'Pagado' : b.payment_status === 'REPORTED' ? 'En verificación' : 'Pendiente' }}
                </span>
              </div>

              @if (b.payment_method === 'CASH') {
                <p>Pagas en efectivo al recibir el servicio.</p>
              } @else if (b.payment_details) {
                @if (b.payment_method === 'NEQUI' || b.payment_method === 'DAVIPLATA') {
                  <p>Número: <strong>{{ b.payment_details.account_number }}</strong></p>
                } @else {
                  <p>{{ b.payment_details.bank_name }} · {{ b.payment_details.account_type }} <strong>{{ b.payment_details.account_number }}</strong></p>
                }
                <p>A nombre de {{ b.payment_details.account_holder }}{{ b.payment_details.holder_document ? ' · ' + b.payment_details.holder_document : '' }}</p>
                @if (b.payment_details.instructions) { <p class="muted">{{ b.payment_details.instructions }}</p> }

                @if (b.payment_status === 'PENDING' && isActive) {
                  <div class="row">
                    <input [(ngModel)]="reference" name="ref" maxlength="80" placeholder="N.º de comprobante o referencia">
                    <button class="btn" type="button" [disabled]="reference.trim().length < 3" (click)="report()">Ya pagué</button>
                  </div>
                } @else if (b.payment_reference) {
                  <p class="muted">Referencia reportada: {{ b.payment_reference }}</p>
                }
              }
            </section>
          }

          @if (b.booking_type === 'HOME') {
            <p class="note">Recuerda tener un espacio con buena luz, una silla y un enchufe cerca.</p>
          }

          @if (b.can_cancel) {
            <p class="note">
              Puedes cancelar sin costo hasta {{ b.cancellation_hours_before }} hora(s) antes
              ({{ b.cancel_deadline | date: "d 'de' MMM, h:mm a" : '' : 'es' }}).
            </p>
            <div class="actions">
              @if (!confirming) {
                <button class="btn danger" type="button" (click)="confirming = true">Cancelar reserva</button>
              } @else {
                <span class="ask">¿Seguro que quieres cancelarla?</span>
                <button class="btn danger" type="button" [disabled]="cancelling" (click)="cancel()">
                  {{ cancelling ? 'Cancelando…' : 'Sí, cancelar' }}
                </button>
                <button class="btn ghost" type="button" (click)="confirming = false">No, mantener</button>
              }
            </div>
          } @else if (isActive) {
            <p class="note">Ya no es posible cancelar esta reserva desde aquí. Comunícate con la barbería.</p>
          }
        </article>
      }
    </main>

    <app-footer></app-footer>
  `,
  styles: [`
    :host { display: block; background: radial-gradient(circle at 90% 0%, rgba(20,184,166,.14), transparent 45%), var(--bg); min-height: 100vh; }
    .page { max-width: 640px; margin: 0 auto; padding: 48px 20px 90px; }
    .card { padding: 34px; border-radius: 28px; background: var(--surface); border: 1px solid var(--border); box-shadow: var(--shadow-lg); animation: fade-up .6s var(--ease) both; }
    .center { text-align: center; display: grid; justify-items: center; gap: 12px; }
    .center p { margin: 0; color: var(--muted); }
    .big { display: grid; place-items: center; width: 68px; height: 68px; border-radius: 50%; font-size: 32px; }
    .big.bad { background: #fff1f2; color: #e11d48; }
    header { margin-bottom: 22px; }
    .eyebrow { font-size: 11px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: var(--accent-text); }
    h1 { margin: 6px 0 12px; font-size: 28px; letter-spacing: -.03em; color: var(--ink); }
    .pill { display: inline-block; padding: 6px 14px; border-radius: 99px; font-size: 12px; font-weight: 800; }
    .pill.ok { background: #d1fae5; color: #047857; } .pill.wait { background: #fef3c7; color: #b45309; }
    .pill.bad { background: #ffe4e6; color: #be123c; } .pill.info { background: var(--primary-50); color: var(--primary-600); }
    dl { margin: 0; display: grid; }
    dl div { display: flex; justify-content: space-between; gap: 18px; padding: 13px 0; border-bottom: 1px solid var(--border); font-size: 14px; }
    dt { color: var(--muted); } dd { margin: 0; font-weight: 700; text-align: right; color: var(--ink); }
    dd a { color: var(--primary-600); text-decoration: none; }
    .total { font-size: 16px; border-bottom: 0 !important; }
    .note { margin: 18px 0 0; padding: 14px 16px; border-radius: 14px; background: var(--surface-2); color: var(--muted); font-size: 13px; line-height: 1.6; }
    .actions { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-top: 18px; }
    .ask { font-weight: 700; color: var(--ink); font-size: 14px; }
    .btn { display: inline-flex; align-items: center; justify-content: center; padding: 13px 20px; border: 0; border-radius: 14px; background: var(--grad-primary); color: #fff; font-weight: 700; text-decoration: none; }
    .btn.danger { background: linear-gradient(135deg, #e11d48, #fb7185); } .btn.ghost { background: transparent; color: var(--ink); border: 1.5px solid var(--border); }
    .btn:disabled { opacity: .6; transform: none; }
    .calbox { margin-top: 18px; }
    .paybox { margin-top: 18px; padding: 18px; border-radius: 18px; background: var(--primary-50); display: grid; gap: 4px; font-size: 14px; color: var(--ink); }
    .paybox p { margin: 2px 0; } .paybox .muted { color: var(--muted); font-size: 13px; } .phead { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
    .row { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 8px; } .row input { flex: 1; min-width: 180px; padding: 12px 14px; border: 1.5px solid var(--border); border-radius: 12px; background: var(--surface); color: var(--ink); }
  `]
})
export class GuestBooking implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(GuestBookingService);
  private readonly toast = inject(ToastService);
  private readonly payments = inject(PaymentApi);
  readonly labels = PAYMENT_LABELS;
  reference = '';
  private readonly cdr = inject(ChangeDetectorRef);

  b: GuestBookingView | null = null;
  loading = true;
  error = '';
  confirming = false;
  cancelling = false;
  private token = '';

  get label(): string { return STATUS[this.b?.status_code ?? '']?.label ?? this.b?.status_code ?? ''; }
  get tone(): string { return STATUS[this.b?.status_code ?? '']?.tone ?? 'info'; }
  get calendarEvent(): CalendarEvent | null {
    const b = this.b;
    if (!b) return null;

    return {
      title: `${b.service_name} · ${b.barbershop_name}`,
      start: b.start_at,
      end: b.end_at,
      location: b.booking_type === 'HOME' ? b.home_address : b.barbershop_address,
      description: `Barbero: ${b.barber_name}\nReserva #${b.id}\nGestiónala en: ${location.href}`,
      uid: `barbergo-${b.id}@barbergo`
    };
  }

  get isActive(): boolean { return ['PENDING', 'CONFIRMED'].includes(this.b?.status_code ?? ''); }

  get total(): string {
    const n = Number(this.b?.service_price ?? 0) + Number(this.b?.home_fee ?? 0);
    return '$' + n.toLocaleString('es-CO');
  }

  ngOnInit(): void {
    this.token = this.route.snapshot.paramMap.get('token') ?? '';
    this.api.get(this.token).subscribe({
      next: b => { this.b = b; this.loading = false; this.cdr.detectChanges(); },
      error: err => {
        this.error = apiError(err, 'El enlace no es válido o la reserva ya no existe.');
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

report(): void {
    this.payments.reportGuestReference(this.token, this.reference.trim()).subscribe({
      next: () => {
        this.toast.success('Pago reportado. La barbería lo verificará.');
        this.api.get(this.token).subscribe(b => { this.b = b; this.cdr.detectChanges(); });
      },
      error: err => this.toast.error(apiError(err, 'No se pudo reportar el pago.'))
    });
  }

  cancel(): void {
    this.cancelling = true;
    this.api.cancel(this.token).subscribe({
      next: b => {
        this.b = b;
        this.cancelling = false;
        this.confirming = false;
        this.toast.success('Tu reserva fue cancelada.');
        this.cdr.detectChanges();
      },
      error: err => {
        this.cancelling = false;
        this.toast.error(apiError(err, 'No fue posible cancelar la reserva.'));
        this.cdr.detectChanges();
      }
    });
  }
}
