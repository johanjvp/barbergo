import { Component, EventEmitter, Input, Output } from '@angular/core';

import { PAYMENT_HINTS, PAYMENT_LABELS, PaymentMethod, PaymentMethodCode } from '../../services/payment';
import { Icon } from '../icon/icon';

/** Tarjetas para elegir cómo pagar (pago directo a la barbería). */
@Component({
  selector: 'app-payment-picker',
  standalone: true,
  imports: [Icon],
  template: `
    <fieldset class="picker">
      <legend>¿Cómo vas a pagar?</legend>

      <div class="grid">
        @for (m of methods; track m.method) {
          <button type="button" class="opt" [class.on]="value === m.method" (click)="choose(m.method)"
                  [attr.aria-pressed]="value === m.method">
            <span class="tick"><app-icon name="check"></app-icon></span>
            <b>{{ labels[m.method] }}</b>
            <small>{{ hints[m.method] }}</small>
          </button>
        }
      </div>

      @if (selected && selected.method !== 'CASH') {
        <div class="details">
          <b>Datos para pagar</b>
          @if (selected.method === 'NEQUI' || selected.method === 'DAVIPLATA') {
            <span>{{ labels[selected.method] }}: <i>{{ selected.account_number }}</i></span>
          } @else {
            <span>{{ selected.bank_name }} · {{ selected.account_type }} <i>{{ selected.account_number }}</i></span>
          }
          <span>A nombre de {{ selected.account_holder }}{{ selected.holder_document ? ' · ' + selected.holder_document : '' }}</span>
          @if (selected.instructions) { <em>{{ selected.instructions }}</em> }
          <small>Tras reservar podrás reportar tu comprobante. La barbería confirma el pago.</small>
        </div>
      }
    </fieldset>
  `,
  styles: [`
    :host { display: block; }
    .picker { margin: 0; padding: 0; border: 0; display: grid; gap: 12px; }
    legend { padding: 0; margin-bottom: 10px; font-size: 12px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
    .opt { position: relative; display: grid; gap: 2px; text-align: left; padding: 14px; border: 1.5px solid var(--border); border-radius: 16px; background: var(--surface-2); color: var(--ink); }
    .opt b { font-size: 14px; } .opt small { font-size: 11px; color: var(--muted); line-height: 1.35; }
    .opt:hover { border-color: var(--primary); }
    .opt.on { border-color: var(--primary); background: var(--primary-50); box-shadow: 0 0 0 3px rgba(13,148,136,.18); }
    .tick { position: absolute; top: 10px; right: 10px; display: grid; place-items: center; width: 20px; height: 20px; border-radius: 50%; background: var(--grad-primary); color: #fff; font-size: 12px; opacity: 0; transform: scale(.4); transition: all .3s var(--ease); }
    .opt.on .tick { opacity: 1; transform: none; }
    .details { display: grid; gap: 4px; padding: 14px 16px; border-radius: 16px; background: var(--surface-2); border: 1px dashed var(--border); font-size: 13px; color: var(--ink); animation: fade-up .3s var(--ease) both; }
    .details i { font-style: normal; font-weight: 800; letter-spacing: .02em; } .details em { color: var(--muted); font-style: normal; } .details small { color: var(--muted); }
  `]
})
export class PaymentPicker {
  @Input() methods: PaymentMethod[] = [];
  @Input() value: PaymentMethodCode | null = null;
  @Output() valueChange = new EventEmitter<PaymentMethodCode>();

  readonly labels = PAYMENT_LABELS;
  readonly hints = PAYMENT_HINTS;

  get selected(): PaymentMethod | undefined {
    return this.methods.find(m => m.method === this.value);
  }

  choose(m: PaymentMethodCode): void {
    this.value = m;
    this.valueChange.emit(m);
  }
}
