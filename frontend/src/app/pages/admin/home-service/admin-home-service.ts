import { DatePipe } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { apiError } from '../../../components/guest-checkout/guest-checkout';
import { Icon } from '../../../components/icon/icon';
import { HomeServiceApi, HomeServiceInfo, HomeServiceStatus } from '../../../services/home-service';
import { ToastService } from '../../../services/toast';

@Component({
  selector: 'app-admin-home-service',
  standalone: true,
  imports: [DatePipe, FormsModule, RouterLink, Icon],
  template: `
    <header class="head">
      <span class="eyebrow">Plataforma</span>
      <h1>Solicitudes de domicilio</h1>
      <p>Revisa los requisitos declarados por cada barbería antes de habilitar el servicio a domicilio.</p>
    </header>

    <nav class="tabs">
      @for (t of tabs; track t.value) {
        <button type="button" [class.active]="filter === t.value" (click)="setFilter(t.value)">{{ t.label }}</button>
      }
    </nav>

    @if (loading) {
      <div class="skeleton" style="height: 180px"></div>
    } @else if (!items.length) {
      <div class="empty"><app-icon name="shield"></app-icon><p>No hay solicitudes en este estado.</p></div>
    } @else {
      <div class="list">
        @for (s of items; track s.barbershop_id) {
          <article class="card">
            <div class="top">
              <div>
                <h3>{{ s.barbershop_name }}</h3>
                <small>Solicitada {{ s.requested_at | date: "d 'de' MMM y, h:mm a" }}</small>
              </div>
              <span class="pill" [class]="s.status">{{ label(s.status) }}</span>
            </div>

            <dl>
              <div><dt>Cobertura</dt><dd>{{ s.radius_km }} km</dd></div>
              <div><dt>Recargo</dt><dd>\${{ s.fee.toLocaleString("es-CO") }}</dd></div>
              <div><dt>Anticipación</dt><dd>{{ s.min_notice_hours }} h</dd></div>
              <div><dt>Barberos a domicilio</dt><dd>{{ s.requirements?.declared_barbers ?? '—' }}</dd></div>
              <div><dt>Servicios a domicilio</dt><dd>{{ s.requirements?.declared_services ?? '—' }}</dd></div>
              <div><dt>Ubicación registrada</dt><dd>{{ s.has_coordinates ? 'Sí' : 'No' }}</dd></div>
            </dl>

            @if (s.zones) { <p class="zones"><b>Zonas:</b> {{ s.zones }}</p> }

            <ul class="decl">
              <li [class.ok]="s.requirements?.hygiene_kit">Kit de higiene propio</li>
              <li [class.ok]="s.requirements?.barbers_verified">Barberos verificados</li>
              <li [class.ok]="s.requirements?.accepts_policy">Acepta la política</li>
            </ul>
            @if (s.requirements?.notes) { <p class="zones"><b>Notas:</b> {{ s.requirements?.notes }}</p> }
            @if (s.rejection_reason) { <p class="zones bad"><b>Motivo:</b> {{ s.rejection_reason }}</p> }

            <div class="actions">
              <a class="ghost" [routerLink]="['/admin/barberias', s.barbershop_id]">Ver barbería</a>

              @if (s.status === 'PENDING' || s.status === 'SUSPENDED') {
                <button type="button" class="ok-btn" [disabled]="busy === s.barbershop_id" (click)="approve(s)">Aprobar</button>
              }
              @if (s.status === 'PENDING' || s.status === 'APPROVED') {
                <button type="button" class="bad-btn" (click)="openReason(s)">{{ s.status === 'APPROVED' ? 'Suspender' : 'Rechazar' }}</button>
              }
            </div>

            @if (reasonFor === s.barbershop_id) {
              <form class="reason" (ngSubmit)="submitReason(s)">
                <input name="reason" [(ngModel)]="reason" minlength="5" maxlength="300" required
                       placeholder="Motivo (se enviará por correo a la barbería)">
                <button type="submit" class="bad-btn" [disabled]="reason.trim().length < 5 || busy === s.barbershop_id">Confirmar</button>
                <button type="button" class="ghost" (click)="reasonFor = null">Cancelar</button>
              </form>
            }
          </article>
        }
      </div>
    }
  `,
  styles: [`
    :host { display: block; }
    .head { margin-bottom: 20px; } .eyebrow { font-size: 11px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: var(--accent-text); }
    h1 { margin: 6px 0 6px; font-size: 30px; letter-spacing: -.03em; color: var(--ink); } .head p { margin: 0; color: var(--muted); }
    .tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }
    .tabs button { padding: 9px 16px; border: 1.5px solid var(--border); border-radius: 99px; background: var(--surface); color: var(--ink); font-weight: 700; font-size: 13px; }
    .tabs button.active { background: var(--grad-primary); border-color: transparent; color: #fff; box-shadow: var(--shadow-md); }
    .list { display: grid; gap: 16px; }
    .card { padding: 24px; border-radius: 24px; background: var(--surface); border: 1px solid var(--border); box-shadow: var(--shadow-sm); animation: fade-up .5s var(--ease) both; }
    .top { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; } h3 { margin: 0 0 4px; font-size: 18px; color: var(--ink); } small { color: var(--muted); }
    .pill { padding: 6px 14px; border-radius: 99px; font-size: 12px; font-weight: 800; background: var(--surface-2); color: var(--muted); }
    .pill.APPROVED { background: #d1fae5; color: #047857; } .pill.PENDING { background: #fef3c7; color: #b45309; } .pill.REJECTED, .pill.SUSPENDED { background: #ffe4e6; color: #be123c; }
    dl { margin: 18px 0 12px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
    dl div { padding: 12px 14px; border-radius: 14px; background: var(--surface-2); } dt { font-size: 11px; color: var(--muted); font-weight: 700; } dd { margin: 4px 0 0; font-weight: 800; color: var(--ink); }
    .zones { margin: 8px 0; font-size: 13px; color: var(--muted); } .zones.bad { color: #be123c; }
    .decl { display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0 0; padding: 0; list-style: none; }
    .decl li { padding: 6px 12px; border-radius: 99px; font-size: 12px; font-weight: 700; background: #ffe4e6; color: #be123c; } .decl li.ok { background: #d1fae5; color: #047857; }
    .actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 18px; }
    .ghost, .ok-btn, .bad-btn { display: inline-flex; padding: 11px 18px; border-radius: 12px; font-weight: 700; font-size: 13px; text-decoration: none; border: 0; }
    .ghost { background: transparent; border: 1.5px solid var(--border); color: var(--ink); }
    .ok-btn { background: linear-gradient(135deg, #059669, #10b981); color: #fff; } .bad-btn { background: linear-gradient(135deg, #e11d48, #fb7185); color: #fff; }
    .reason { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; } .reason input { flex: 1; min-width: 220px; padding: 12px 14px; border: 1.5px solid var(--border); border-radius: 12px; background: var(--surface-2); color: var(--ink); }
    .empty { display: grid; justify-items: center; gap: 6px; padding: 60px 20px; border-radius: 24px; background: var(--surface); border: 1px dashed var(--border); color: var(--muted); font-size: 28px; } .empty p { margin: 0; font-size: 14px; }
    @media (max-width: 720px) { dl { grid-template-columns: 1fr 1fr; } }
  `]
})
export class AdminHomeService implements OnInit {
  private readonly api = inject(HomeServiceApi);
  private readonly toast = inject(ToastService);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly tabs: { value: HomeServiceStatus; label: string }[] = [
    { value: 'PENDING', label: 'Pendientes' },
    { value: 'APPROVED', label: 'Aprobadas' },
    { value: 'REJECTED', label: 'Rechazadas' },
    { value: 'SUSPENDED', label: 'Suspendidas' }
  ];

  filter: HomeServiceStatus = 'PENDING';
  items: HomeServiceInfo[] = [];
  loading = true;
  busy: number | null = null;
  reasonFor: number | null = null;
  reason = '';

  ngOnInit(): void { this.load(); }

  label(s: string): string { return this.tabs.find(t => t.value === s)?.label.replace(/s$/, '') ?? s; }

  setFilter(f: HomeServiceStatus): void { this.filter = f; this.reasonFor = null; this.load(); }

  private load(): void {
    this.loading = true;
    this.cdr.detectChanges();
    this.api.listRequests(this.filter).subscribe({
      next: items => { this.items = items; this.loading = false; this.cdr.detectChanges(); },
      error: err => { this.loading = false; this.toast.error(apiError(err, 'No se pudieron cargar las solicitudes.')); this.cdr.detectChanges(); }
    });
  }

  approve(s: HomeServiceInfo): void {
    this.busy = s.barbershop_id;
    this.api.approve(s.barbershop_id).subscribe({
      next: () => { this.busy = null; this.load(); this.toast.success(s.barbershop_name + ': domicilio aprobado.'); },
      error: err => { this.busy = null; this.toast.error(apiError(err, 'No se pudo aprobar.')); this.cdr.detectChanges(); }
    });
  }

  openReason(s: HomeServiceInfo): void { this.reasonFor = s.barbershop_id; this.reason = ''; }

  submitReason(s: HomeServiceInfo): void {
    this.busy = s.barbershop_id;
    const call = s.status === 'APPROVED'
      ? this.api.suspend(s.barbershop_id, this.reason.trim())
      : this.api.reject(s.barbershop_id, this.reason.trim());
    call.subscribe({
      next: () => { this.busy = null; this.reasonFor = null; this.load(); this.toast.success('Decisión registrada y notificada por correo.'); },
      error: err => { this.busy = null; this.toast.error(apiError(err, 'No se pudo registrar la decisión.')); this.cdr.detectChanges(); }
    });
  }
}
