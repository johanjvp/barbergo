import { CalendarButtons } from '../calendar-buttons/calendar-buttons';
import { CalendarEvent } from '../../utils/calendar';
import { HttpErrorResponse } from '@angular/common/http';
import { ChangeDetectorRef, Component, EventEmitter, Input, OnDestroy, Output, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { HomeAddressValue } from '../../models/booking';
import { GuestBookingCreated, GuestBookingService } from '../../services/guest-booking';
import { PAYMENT_LABELS, PaymentApi, PaymentMethod, PaymentMethodCode } from '../../services/payment';
import { Confetti } from '../confetti/confetti';
import { Icon } from '../icon/icon';

export interface GuestCheckoutBooking {
  barberId: number;
  serviceId: number;
  startAt: string;
  bookingType: 'IN_SHOP' | 'HOME';
  home: HomeAddressValue | null;
  paymentMethod: PaymentMethodCode | null;
  paymentDetails: PaymentMethod | null;
}

export interface GuestCheckoutSummary {
  shopName: string;
  serviceName: string;
  barberName: string;
  dateText: string;
  total: string;
  homeFee: string | null;
  needsApproval: boolean;
    paymentLabel: string | null;
  shopAddress: string | null;
}

export function apiError(error: unknown, fallback: string): string {
  if (error instanceof HttpErrorResponse) {
    const detail = error.error?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail) && detail.length) {
      return String(detail[0]?.msg ?? fallback).replace(/^Value error, /, '');
    }
    if (error.status === 0) return 'No hay conexión con el servidor. Inténtalo de nuevo.';
  }
  return fallback;
}

@Component({
  selector: 'app-guest-checkout',
  standalone: true,
  imports: [FormsModule, RouterLink, Icon, Confetti, CalendarButtons],
  template: `
    @if (step === 'done') { <app-confetti></app-confetti> }

    <div class="backdrop" (click)="step === 'done' ? close() : null">
      <section class="sheet" role="dialog" aria-modal="true" (click)="$event.stopPropagation()">

        @if (step !== 'done') {
          <button class="x" type="button" (click)="close()" aria-label="Cerrar">×</button>

          <header>
            <span class="eyebrow">Reserva sin cuenta</span>
            <h2>{{ step === 'contact' ? 'Tus datos de contacto' : 'Verifica tu correo' }}</h2>
          </header>

          <dl class="summary">
            <div><dt>Servicio</dt><dd>{{ summary.serviceName }}</dd></div>
            <div><dt>Barbero</dt><dd>{{ summary.barberName }}</dd></div>
            <div><dt>Cuándo</dt><dd>{{ summary.dateText }}</dd></div>
            @if (summary.homeFee) { <div><dt>Desplazamiento</dt><dd>{{ summary.homeFee }}</dd></div> }
            @if (summary.paymentLabel) { <div><dt>Pago</dt><dd>{{ summary.paymentLabel }}</dd></div> }
            <div class="total"><dt>Total</dt><dd>{{ summary.total }}</dd></div>
          </dl>
        }

        <!-- PASO 1: datos -->
        @if (step === 'contact') {
          <form (ngSubmit)="sendCode()" class="form">
            <label><span>Nombre completo</span>
              <input name="name" [(ngModel)]="name" required minlength="2" maxlength="120" autocomplete="name" placeholder="Tu nombre"></label>
            <label><span>Correo electrónico</span>
              <input name="email" type="email" [(ngModel)]="email" required autocomplete="email" placeholder="tu@correo.com"></label>
            <label><span>Teléfono / WhatsApp</span>
              <input name="phone" type="tel" [(ngModel)]="phone" required minlength="7" maxlength="30" autocomplete="tel" placeholder="300 000 0000"></label>

            <label class="check">
              <input name="terms" type="checkbox" [(ngModel)]="accepted">
              <span>Acepto que BarberGo use mis datos para gestionar esta reserva y enviarme avisos por correo.</span>
            </label>

            @if (error) { <p class="error">{{ error }}</p> }

            <button class="primary" type="submit" [disabled]="loading || !canSend">
              {{ loading ? 'Enviando código…' : 'Enviar código a mi correo' }}
              <app-icon name="arrow-right"></app-icon>
            </button>

            <p class="alt">¿Ya tienes cuenta? <button type="button" class="link" (click)="login.emit()">Inicia sesión</button></p>
          </form>
        }

        <!-- PASO 2: código -->
        @if (step === 'code') {
          <form (ngSubmit)="confirm()" class="form">
            <p class="hint">Enviamos un código de 6 dígitos a <b>{{ email }}</b>. Vence en {{ ttl }} minutos.</p>

            <input class="code" name="code" inputmode="numeric" pattern="[0-9]*" maxlength="6" [(ngModel)]="code"
                   autocomplete="one-time-code" placeholder="••••••" aria-label="Código de verificación">

            @if (error) { <p class="error">{{ error }}</p> }

            <button class="primary" type="submit" [disabled]="loading || code.length !== 6">
              {{ loading ? 'Confirmando…' : summary.needsApproval ? 'Enviar solicitud de reserva' : 'Confirmar reserva' }}
              <app-icon name="check"></app-icon>
            </button>

            <p class="alt">
              ¿No llegó? <button type="button" class="link" [disabled]="cooldown > 0 || loading" (click)="sendCode(true)">
                {{ cooldown > 0 ? 'Reenviar en ' + cooldown + 's' : 'Reenviar código' }}</button>
              · <button type="button" class="link" (click)="step = 'contact'; error = ''">Cambiar correo</button>
            </p>
          </form>
        }

        <!-- PASO 3: listo -->
        @if (step === 'done' && created) {
          <div class="done">
            <div class="badge"><app-icon name="check"></app-icon></div>
            <h2>{{ summary.needsApproval ? '¡Solicitud enviada!' : '¡Reserva confirmada!' }}</h2>
            <p>
              {{ summary.needsApproval
                ? 'La barbería revisará tu solicitud y te avisaremos por correo.'
                : 'Te enviamos los detalles a' }}
              @if (!summary.needsApproval) { <b>{{ email }}</b> }
            </p>
            <p class="num">Reserva #{{ created.id }}</p>

            <app-calendar-buttons [event]="calendarEvent"></app-calendar-buttons>

            <div class="manage">
              <span>Tu enlace para ver o cancelar la cita (también va en el correo):</span>
              <code>{{ manageUrl }}</code>
              <div class="row">
                <button type="button" class="ghost" (click)="copy()">{{ copied ? '¡Copiado!' : 'Copiar enlace' }}</button>
                <a class="primary small" [routerLink]="['/reserva', created.manage_token]" (click)="close()">Ver mi reserva</a>
              </div>
            </div>

@if (booking.paymentMethod && booking.paymentDetails && booking.paymentMethod !== 'CASH') {
              <div class="pay">
                <b>Paga con {{ labels[booking.paymentMethod] }}</b>
                @if (booking.paymentMethod === 'NEQUI' || booking.paymentMethod === 'DAVIPLATA') {
                  <span>Número: <i>{{ booking.paymentDetails.account_number }}</i></span>
                } @else {
                  <span>{{ booking.paymentDetails.bank_name }} · {{ booking.paymentDetails.account_type }} <i>{{ booking.paymentDetails.account_number }}</i></span>
                }
                <span>A nombre de {{ booking.paymentDetails.account_holder }}</span>
                @if (!reported) {
                  <div class="row">
                    <input name="ref" [(ngModel)]="reference" placeholder="N.º de comprobante o referencia" maxlength="80">
                    <button type="button" class="ghost" [disabled]="reference.trim().length < 3" (click)="report()">Ya pagué</button>
                  </div>
                } @else { <span class="okmsg"><app-icon name="check"></app-icon> Pago reportado. La barbería lo verificará.</span> }
              </div>
            } @else if (booking.paymentMethod === 'CASH') {
              <p class="num">Pagas en efectivo al recibir el servicio.</p>
            }

            <p class="alt">¿Quieres gestionar todas tus citas? <a [routerLink]="['/registro']" (click)="close()">Crea una cuenta gratis</a></p>
            <button class="ghost wide" type="button" (click)="close()">Cerrar</button>
          </div>
        }
      </section>
    </div>
  `,
  styles: [`
    .backdrop { position: fixed; inset: 0; z-index: 1500; display: grid; place-items: center; padding: 16px; background: rgba(6,22,29,.6); backdrop-filter: blur(8px); animation: fade-in .25s ease both; }
    .sheet { position: relative; width: min(480px, 100%); max-height: calc(100vh - 32px); overflow: auto; padding: 30px; border-radius: 28px;
      background: var(--surface); color: var(--ink); box-shadow: 0 40px 90px -20px rgba(0,0,0,.55); animation: scale-in .35s var(--ease) both; }
    .x { position: absolute; top: 14px; right: 14px; width: 36px; height: 36px; border: 0; border-radius: 50%; background: var(--surface-2); color: var(--ink); font-size: 22px; line-height: 1; }
    .eyebrow { font-size: 11px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: var(--accent-text); }
    h2 { margin: 6px 0 16px; font-size: 24px; letter-spacing: -.02em; }
    .summary { margin: 0 0 20px; padding: 14px 16px; border-radius: 16px; background: var(--surface-2); display: grid; gap: 8px; }
    .summary div { display: flex; justify-content: space-between; gap: 12px; font-size: 13px; }
    .summary dt { color: var(--muted); } .summary dd { margin: 0; font-weight: 700; text-align: right; }
    .summary .total { padding-top: 8px; border-top: 1px dashed var(--border); font-size: 15px; }
    .form { display: grid; gap: 14px; }
    label { display: grid; gap: 6px; } label span { font-size: 12px; font-weight: 700; color: var(--muted); }
    input:not([type=checkbox]) { padding: 14px; border: 1.5px solid var(--border); border-radius: 12px; background: var(--surface-2); color: var(--ink); width: 100%; }
    .check { grid-template-columns: auto 1fr; align-items: start; gap: 10px; } .check span { font-weight: 500; line-height: 1.5; }
    .code { text-align: center; font: 800 30px Inter, sans-serif; letter-spacing: 12px; padding: 16px !important; }
    .hint { margin: 0; color: var(--muted); font-size: 14px; line-height: 1.6; }
    .error { margin: 0; padding: 12px 14px; border-radius: 12px; background: #fff1f2; border: 1px solid #fecdd3; color: #be123c; font-size: 13px; }
    .primary { display: inline-flex; justify-content: center; align-items: center; gap: 10px; padding: 15px 20px; border: 0; border-radius: 14px; background: var(--grad-primary); color: #fff; font-weight: 700; box-shadow: var(--shadow-md); text-decoration: none; }
    .primary:disabled { opacity: .55; box-shadow: none; transform: none; }
    .primary.small { padding: 11px 16px; font-size: 13px; }
    .ghost { padding: 11px 16px; border: 1.5px solid var(--border); border-radius: 12px; background: transparent; color: var(--ink); font-weight: 700; font-size: 13px; }
    .wide { width: 100%; margin-top: 8px; }
    .alt { margin: 0; text-align: center; font-size: 13px; color: var(--muted); }
    .alt a, .link { color: var(--primary-600); font-weight: 700; background: none; border: 0; padding: 0; text-decoration: none; }
    .link:disabled { opacity: .5; }
    .done { display: grid; gap: 10px; text-align: center; justify-items: center; }
    .badge { display: grid; place-items: center; width: 68px; height: 68px; border-radius: 50%; background: var(--grad-primary); color: #fff; font-size: 34px; box-shadow: var(--shadow-md); animation: pop .6s var(--ease) both; }
    @keyframes pop { from { transform: scale(0) rotate(-90deg); } to { transform: none; } }
    .done h2 { margin: 6px 0 0; } .done p { margin: 0; color: var(--muted); line-height: 1.6; }
    .num { font-weight: 800; color: var(--ink) !important; }
    .manage { width: 100%; display: grid; gap: 10px; padding: 16px; border-radius: 16px; background: var(--surface-2); text-align: left; font-size: 13px; color: var(--muted); }
    .manage code { display: block; padding: 10px 12px; border-radius: 10px; background: var(--surface); border: 1px solid var(--border); color: var(--ink); font-size: 12px; word-break: break-all; }
    .row { display: flex; gap: 10px; flex-wrap: wrap; }
    .pay { width: 100%; display: grid; gap: 6px; padding: 16px; border-radius: 16px; background: var(--primary-50); text-align: left; font-size: 13px; color: var(--ink); }
    .pay i { font-style: normal; font-weight: 800; } .pay input { flex: 1; min-width: 160px; padding: 10px 12px !important; }
    .okmsg { display: flex; align-items: center; gap: 6px; color: #059669; font-weight: 700; }
  `]
})
export class GuestCheckout implements OnDestroy {
  @Input({ required: true }) booking!: GuestCheckoutBooking;
  @Input({ required: true }) summary!: GuestCheckoutSummary;

  @Output() closed = new EventEmitter<void>();
  @Output() login = new EventEmitter<void>();
  @Output() created$ = new EventEmitter<GuestBookingCreated>();

  private readonly api = inject(GuestBookingService);
  private readonly payments = inject(PaymentApi);
  readonly labels = PAYMENT_LABELS;
  reference = '';
  reported = false;
  private readonly cdr = inject(ChangeDetectorRef);

  step: 'contact' | 'code' | 'done' = 'contact';
  name = '';
  email = '';
  phone = '';
  code = '';
  accepted = false;
  loading = false;
  error = '';
  ttl = 10;
  cooldown = 0;
  copied = false;
  created: GuestBookingCreated | null = null;
  private timer?: ReturnType<typeof setInterval>;

  get canSend(): boolean {
    return (
      this.name.trim().length >= 2 &&
      /^\S+@\S+\.\S+$/.test(this.email.trim()) &&
      this.phone.trim().length >= 7 &&
      this.accepted
    );
  }

  get calendarEvent(): CalendarEvent {
    const c = this.created!;
    return {
      title: `${this.summary.serviceName} · ${this.summary.shopName}`,
      start: c.start_at,
      end: c.end_at,
      location: this.booking.bookingType === 'HOME' ? this.booking.home?.address : this.summary.shopAddress,
      description: `Barbero: ${this.summary.barberName}\nReserva #${c.id}\nGestiónala en: ${this.manageUrl}`,
      uid: `barbergo-${c.id}@barbergo`
    };
  }

  get manageUrl(): string {
    return this.created ? `${location.origin}/reserva/${this.created.manage_token}` : '';
  }

  ngOnDestroy(): void {
    clearInterval(this.timer);
  }

  sendCode(resend = false): void {
    if (this.loading || (!resend && !this.canSend)) return;
    this.loading = true;
    this.error = '';

    this.api.requestCode(this.email.trim()).subscribe({
      next: res => {
        this.ttl = res.expires_in_minutes;
        this.step = 'code';
        this.loading = false;
        this.startCooldown();
        this.cdr.detectChanges();
      },
      error: err => {
        this.error = apiError(err, 'No pudimos enviar el código. Revisa tu correo e inténtalo otra vez.');
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  confirm(): void {
    if (this.loading || this.code.length !== 6) return;
    this.loading = true;
    this.error = '';

    this.api
      .create({
        barber_id: this.booking.barberId,
        service_id: this.booking.serviceId,
        start_at: this.booking.startAt,
        customer_notes: null,
        booking_type: this.booking.bookingType,
        home: this.booking.home,
        payment_method: this.booking.paymentMethod,
        name: this.name.trim(),
        email: this.email.trim(),
        phone: this.phone.trim(),
        code: this.code,
        accept_terms: this.accepted
      })
      .subscribe({
        next: res => {
          this.created = res;
          this.step = 'done';
          this.loading = false;
          this.created$.emit(res);
          this.cdr.detectChanges();
        },
        error: err => {
          this.error = apiError(err, 'No pudimos crear la reserva. Inténtalo de nuevo.');
          this.loading = false;
          this.cdr.detectChanges();
        }
      });
  }

report(): void {
    if (!this.created) return;
    this.payments.reportGuestReference(this.created.manage_token, this.reference.trim()).subscribe({
      next: () => { this.reported = true; this.cdr.detectChanges(); },
      error: err => { this.error = apiError(err, 'No se pudo reportar el pago.'); this.cdr.detectChanges(); }
    });
  }

  copy(): void {
    navigator.clipboard?.writeText(this.manageUrl).then(() => {
      this.copied = true;
      this.cdr.detectChanges();
      setTimeout(() => { this.copied = false; this.cdr.detectChanges(); }, 2000);
    });
  }

  close(): void {
    this.closed.emit();
  }

  private startCooldown(): void {
    clearInterval(this.timer);
    this.cooldown = 30;
    this.timer = setInterval(() => {
      this.cooldown = Math.max(0, this.cooldown - 1);
      if (this.cooldown === 0) clearInterval(this.timer);
      this.cdr.detectChanges();
    }, 1000);
  }
}
