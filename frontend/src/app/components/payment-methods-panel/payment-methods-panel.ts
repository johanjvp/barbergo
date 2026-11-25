import { DatePipe } from '@angular/common';
import { ChangeDetectorRef, Component, Input, OnChanges, SimpleChanges, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import {
  PAYMENT_LABELS,
  PaymentApi,
  PaymentMethod,
  PaymentMethodCode,
  PaymentRow
} from '../../services/payment';
import { ToastService } from '../../services/toast';
import { apiError } from '../guest-checkout/guest-checkout';
import { Icon } from '../icon/icon';

const ORDER: PaymentMethodCode[] = ['CASH', 'NEQUI', 'DAVIPLATA', 'BANK_TRANSFER', 'DEPOSIT'];

const blank = (method: PaymentMethodCode): PaymentMethod => ({
  method,
  bank_name: null,
  account_type: method === 'BANK_TRANSFER' || method === 'DEPOSIT' ? 'Ahorros' : null,
  account_number: null,
  account_holder: null,
  holder_document: null,
  instructions: null,
  is_active: false
});

/** Panel de la barbería: configurar métodos de pago directo y verificar pagos recibidos. */
@Component({
  selector: 'app-payment-methods-panel',
  standalone: true,
  imports: [FormsModule, DatePipe, Icon],
  template: `
    <section class="panel">
      <header>
        <div class="ico"><app-icon name="shield"></app-icon></div>
        <div>
          <h3>Pagos directos</h3>
          <p>Cobra sin pasarela: tus clientes te pagan directamente y tú confirmas la recepción.</p>
        </div>
      </header>

      @if (loading) {
        <div class="skeleton" style="height: 180px"></div>
      } @else {
        <div class="methods">
          @for (m of rows; track m.method) {
            <div class="method" [class.on]="m.is_active">
              <label class="switch">
                <input type="checkbox" [(ngModel)]="m.is_active" [name]="'on-' + m.method">
                <span class="track"></span>
                <b>{{ labels[m.method] }}</b>
              </label>

              @if (m.is_active && m.method !== 'CASH') {
                <div class="fields">
                  @if (m.method === 'NEQUI' || m.method === 'DAVIPLATA') {
                    <label><span>Número (10 dígitos)</span><input [(ngModel)]="m.account_number" [name]="'n-' + m.method" maxlength="10" inputmode="numeric" placeholder="3001234567"></label>
                    <label><span>A nombre de</span><input [(ngModel)]="m.account_holder" [name]="'h-' + m.method" maxlength="120"></label>
                  } @else {
                    <label><span>Banco</span><input [(ngModel)]="m.bank_name" [name]="'b-' + m.method" maxlength="80" placeholder="Bancolombia"></label>
                    <label><span>Tipo de cuenta</span>
                      <select [(ngModel)]="m.account_type" [name]="'t-' + m.method"><option>Ahorros</option><option>Corriente</option></select></label>
                    <label><span>Número de cuenta</span><input [(ngModel)]="m.account_number" [name]="'a-' + m.method" maxlength="40"></label>
                    <label><span>Titular</span><input [(ngModel)]="m.account_holder" [name]="'h-' + m.method" maxlength="120"></label>
                    <label><span>Documento <em>(opcional)</em></span><input [(ngModel)]="m.holder_document" [name]="'d-' + m.method" maxlength="30"></label>
                  }
                  <label class="wide"><span>Indicaciones <em>(opcional)</em></span>
                    <input [(ngModel)]="m.instructions" [name]="'i-' + m.method" maxlength="300" placeholder="Envía el comprobante al reservar"></label>
                </div>
              }
            </div>
          }
        </div>

        @if (error) { <p class="alert">{{ error }}</p> }
        <button class="btn" type="button" [disabled]="saving" (click)="save()">{{ saving ? 'Guardando…' : 'Guardar métodos de pago' }}</button>

        <!-- VERIFICACIÓN -->
        <div class="verify">
          <div class="vhead">
            <h4>Pagos por verificar</h4>
            <div class="tabs">
              <button type="button" [class.active]="state === 'OPEN'" (click)="setState('OPEN')">Pendientes</button>
              <button type="button" [class.active]="state === 'PAID'" (click)="setState('PAID')">Pagados</button>
            </div>
          </div>

          @if (!payments.length) {
            <p class="empty">No hay pagos {{ state === 'OPEN' ? 'pendientes' : 'confirmados' }}.</p>
          }
          @for (p of payments; track p.id) {
            <div class="pay">
              <div class="info">
                <b>#{{ p.id }} · {{ p.client_name || 'Cliente' }}</b>
                <small>{{ p.service_name }} · {{ p.start_at | date: "d MMM, h:mm a" }}</small>
                <small>{{ labels[p.payment_method] }}{{ p.payment_reference ? ' · Ref. ' + p.payment_reference : '' }}</small>
              </div>
              <div class="amount">\${{ p.total.toLocaleString('es-CO') }}</div>
              <span class="tag" [class]="p.payment_status">{{ statusText(p.payment_status) }}</span>
              @if (p.payment_status !== 'PAID') {
                <button type="button" class="ok" (click)="mark(p, 'PAID')">Marcar pagado</button>
              } @else {
                <button type="button" class="ghost" (click)="mark(p, 'PENDING')">Deshacer</button>
              }
            </div>
          }
        </div>
      }
    </section>
  `,
  styles: [`
    :host { display: block; }
    .panel { padding: 26px; border-radius: 24px; background: var(--surface); border: 1px solid var(--border); box-shadow: var(--shadow-sm); display: grid; gap: 18px; }
    header { display: flex; gap: 14px; align-items: flex-start; }
    .ico { display: grid; place-items: center; width: 46px; height: 46px; border-radius: 14px; background: var(--primary-50); color: var(--primary-600); font-size: 22px; flex-shrink: 0; }
    h3 { margin: 0 0 4px; font-size: 18px; color: var(--ink); } header p { margin: 0; color: var(--muted); font-size: 13px; }
    .methods { display: grid; gap: 10px; }
    .method { padding: 14px 16px; border: 1.5px solid var(--border); border-radius: 16px; background: var(--surface-2); transition: all .3s var(--ease); } .method.on { border-color: var(--primary); background: var(--primary-50); }
    .switch { display: flex; align-items: center; gap: 12px; cursor: pointer; } .switch input { position: absolute; opacity: 0; }
    .track { position: relative; width: 40px; height: 22px; border-radius: 99px; background: #cbd5d3; transition: background .3s; flex-shrink: 0; }
    .track::after { content: ""; position: absolute; top: 3px; left: 3px; width: 16px; height: 16px; border-radius: 50%; background: #fff; transition: transform .3s var(--ease); box-shadow: 0 1px 3px rgba(0,0,0,.3); }
    .switch input:checked + .track { background: var(--primary); } .switch input:checked + .track::after { transform: translateX(18px); }
    .switch b { color: var(--ink); font-size: 14px; }
    .fields { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 14px; animation: fade-up .3s var(--ease) both; } .wide { grid-column: 1 / -1; }
    label { display: grid; gap: 5px; } label span { font-size: 11px; font-weight: 700; color: var(--muted); } em { font-style: normal; font-weight: 500; }
    input:not([type=checkbox]), select { padding: 11px 12px; border: 1.5px solid var(--border); border-radius: 10px; background: var(--surface); color: var(--ink); width: 100%; }
    .alert { margin: 0; padding: 12px 14px; border-radius: 12px; background: #fff1f2; border: 1px solid #fecdd3; color: #be123c; font-size: 13px; }
    .btn { justify-self: start; padding: 13px 20px; border: 0; border-radius: 14px; background: var(--grad-primary); color: #fff; font-weight: 700; box-shadow: var(--shadow-md); } .btn:disabled { opacity: .6; transform: none; }
    .verify { padding-top: 18px; border-top: 1px solid var(--border); display: grid; gap: 10px; }
    .vhead { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; } h4 { margin: 0; font-size: 15px; color: var(--ink); }
    .tabs { display: flex; gap: 6px; } .tabs button { padding: 7px 14px; border: 1.5px solid var(--border); border-radius: 99px; background: transparent; color: var(--ink); font-size: 12px; font-weight: 700; }
    .tabs .active { background: var(--grad-primary); border-color: transparent; color: #fff; }
    .empty { margin: 0; padding: 18px; text-align: center; border-radius: 14px; background: var(--surface-2); color: var(--muted); font-size: 13px; }
    .pay { display: grid; grid-template-columns: 1fr auto auto auto; gap: 12px; align-items: center; padding: 12px 14px; border-radius: 14px; background: var(--surface-2); }
    .info { display: grid; gap: 2px; } .info b { color: var(--ink); font-size: 13px; } .info small { color: var(--muted); font-size: 12px; } .amount { font-weight: 800; color: var(--ink); }
    .tag { padding: 5px 12px; border-radius: 99px; font-size: 11px; font-weight: 800; background: #fef3c7; color: #b45309; } .tag.PAID { background: #d1fae5; color: #047857; } .tag.REPORTED { background: #dbeafe; color: #1d4ed8; }
    .ok, .ghost { padding: 9px 14px; border-radius: 10px; font-size: 12px; font-weight: 700; border: 0; } .ok { background: linear-gradient(135deg, #059669, #10b981); color: #fff; } .ghost { background: transparent; border: 1.5px solid var(--border); color: var(--ink); }
    @media (max-width: 720px) { .fields { grid-template-columns: 1fr; } .pay { grid-template-columns: 1fr auto; } }
  `]
})
export class PaymentMethodsPanel implements OnChanges {
  @Input({ required: true }) barbershopId!: number;

  private readonly api = inject(PaymentApi);
  private readonly toast = inject(ToastService);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly labels = PAYMENT_LABELS;
  rows: PaymentMethod[] = ORDER.map(blank);
  payments: PaymentRow[] = [];
  state: 'OPEN' | 'PAID' = 'OPEN';
  loading = true;
  saving = false;
  error = '';

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['barbershopId']) {
      this.load();
      this.loadPayments();
    }
  }

  private load(): void {
    this.loading = true;
    this.api.getSettings(this.barbershopId).subscribe({
      next: saved => {
        this.rows = ORDER.map(code => saved.find(s => s.method === code) ?? blank(code));
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: err => { this.loading = false; this.error = apiError(err, 'No se pudieron cargar los métodos de pago.'); this.cdr.detectChanges(); }
    });
  }

  private loadPayments(): void {
    this.api.listPayments(this.barbershopId, this.state).subscribe({
      next: list => { this.payments = list; this.cdr.detectChanges(); },
      error: () => { this.payments = []; this.cdr.detectChanges(); }
    });
  }

  setState(s: 'OPEN' | 'PAID'): void { this.state = s; this.loadPayments(); }

  statusText(s: string): string {
    return ({ PENDING: 'Pendiente', REPORTED: 'Reportado', PAID: 'Pagado' } as Record<string, string>)[s] ?? s;
  }

  save(): void {
    this.saving = true;
    this.error = '';
    const active = this.rows.filter(r => r.is_active || r.method === 'CASH' && r.is_active);
    this.api.saveSettings(this.barbershopId, this.rows.filter(r => r.is_active)).subscribe({
      next: saved => {
        this.rows = ORDER.map(code => saved.find(s => s.method === code) ?? blank(code));
        this.saving = false;
        this.toast.success(active.length ? 'Métodos de pago guardados.' : 'Sin métodos de pago: el cliente no deberá elegir uno.');
        this.cdr.detectChanges();
      },
      error: err => { this.saving = false; this.error = apiError(err, 'No se pudieron guardar los métodos de pago.'); this.cdr.detectChanges(); }
    });
  }

  mark(p: PaymentRow, status: 'PAID' | 'PENDING'): void {
    this.api.setStatus(this.barbershopId, p.id, status).subscribe({
      next: () => { this.toast.success(status === 'PAID' ? 'Pago confirmado.' : 'Pago marcado como pendiente.'); this.loadPayments(); },
      error: err => this.toast.error(apiError(err, 'No se pudo actualizar el pago.'))
    });
  }
}
