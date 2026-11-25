import { DatePipe } from '@angular/common';
import { ChangeDetectorRef, Component, Input, OnChanges, SimpleChanges, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { HomeServiceApi, HomeServiceInfo } from '../../services/home-service';
import { ToastService } from '../../services/toast';
import { apiError } from '../guest-checkout/guest-checkout';
import { Icon } from '../icon/icon';

/** Panel de la barbería: solicitar, ver el estado y ajustar el servicio a domicilio. */
@Component({
  selector: 'app-home-service-panel',
  standalone: true,
  imports: [FormsModule, DatePipe, Icon],
  template: `
    <section class="panel">
      <header>
        <div class="ico"><app-icon name="pin"></app-icon></div>
        <div>
          <h3>Servicio a domicilio</h3>
          <p>Atiende a tus clientes en su casa u oficina. Requiere aprobación de BarberGo.</p>
        </div>
        @if (info) { <span class="pill" [class]="info.status">{{ statusLabel }}</span> }
      </header>

      @if (loading) {
        <div class="skeleton" style="height: 160px"></div>
      } @else if (info) {

        @if (info.status === 'REJECTED' && info.rejection_reason) {
          <p class="alert bad"><b>Solicitud rechazada:</b> {{ info.rejection_reason }}. Corrige los datos y envíala de nuevo.</p>
        }
        @if (info.status === 'SUSPENDED') {
          <p class="alert bad"><b>Servicio suspendido:</b> {{ info.rejection_reason }}</p>
        }
        @if (info.status === 'PENDING') {
          <p class="alert wait">
            Tu solicitud está en revisión desde {{ info.requested_at | date: "d 'de' MMM, h:mm a" }}.
            Te avisaremos por correo cuando sea aprobada.
          </p>
        }

        <!-- SOLICITAR -->
        @if (info.status === 'NONE' || info.status === 'REJECTED' || info.status === 'SUSPENDED') {
          <div class="reqs">
            <h4>Requisitos</h4>
            <ul>
              <li [class.done]="info.has_coordinates">Ubicación de la barbería registrada (latitud y longitud)</li>
              <li>Al menos un barbero que acepte domicilio</li>
              <li>Al menos un servicio habilitado para domicilio</li>
            </ul>
          </div>

          <form (ngSubmit)="submit()" class="form">
            <div class="grid">
              <label><span>Radio de cobertura (km)</span>
                <input type="number" name="radius" [(ngModel)]="radius" min="1" max="50" step="0.5" required></label>
              <label><span>Recargo por desplazamiento ($)</span>
                <input type="number" name="fee" [(ngModel)]="fee" min="0" step="500" required></label>
              <label><span>Anticipación mínima (horas)</span>
                <input type="number" name="notice" [(ngModel)]="notice" min="0" max="72" required></label>
            </div>
            <label><span>Barrios o zonas que cubres <em>(opcional)</em></span>
              <input type="text" name="zones" [(ngModel)]="zones" maxlength="500" placeholder="Alto Prado, Riomar, Villa Country…"></label>

            <fieldset>
              <legend>Declaración</legend>
              <label class="check"><input type="checkbox" name="kit" [(ngModel)]="kit"><span>Mis barberos llevan kit de higiene propio (herramientas esterilizadas, capa y toallas desechables).</span></label>
              <label class="check"><input type="checkbox" name="verified" [(ngModel)]="verified"><span>Los barberos que atienden a domicilio tienen identidad verificada y son del equipo de la barbería.</span></label>
              <label class="check"><input type="checkbox" name="policy" [(ngModel)]="policy"><span>Acepto la política de domicilios de BarberGo (puntualidad, cancelación y trato respetuoso).</span></label>
            </fieldset>

            <label><span>Notas para el revisor <em>(opcional)</em></span>
              <input type="text" name="notes" [(ngModel)]="notes" maxlength="500" placeholder="Experiencia previa, horarios de domicilio, etc."></label>

            @if (error) { <p class="alert bad">{{ error }}</p> }

            <button class="btn" type="submit" [disabled]="saving || !kit || !verified || !policy">
              {{ saving ? 'Enviando…' : 'Enviar solicitud' }} <app-icon name="arrow-right"></app-icon>
            </button>
          </form>
        }

        <!-- APROBADO: ajustar -->
        @if (info.status === 'APPROVED') {
          <p class="alert ok"><app-icon name="check"></app-icon> Activo: los clientes ya pueden reservar a domicilio dentro de {{ info.radius_km }} km.</p>
          <form (ngSubmit)="saveTerms()" class="form">
            <div class="grid">
              <label><span>Recargo por desplazamiento ($)</span><input type="number" name="fee2" [(ngModel)]="fee" min="0" step="500"></label>
              <label><span>Anticipación mínima (horas)</span><input type="number" name="notice2" [(ngModel)]="notice" min="0" max="72"></label>
            </div>
            <label><span>Barrios o zonas</span><input type="text" name="zones2" [(ngModel)]="zones" maxlength="500"></label>
            @if (error) { <p class="alert bad">{{ error }}</p> }
            <div class="row">
              <button class="btn" type="submit" [disabled]="saving">{{ saving ? 'Guardando…' : 'Guardar cambios' }}</button>
              <button class="btn ghost" type="button" [disabled]="saving" (click)="disable()">Desactivar domicilio</button>
            </div>
          </form>
        }
      }
    </section>
  `,
  styles: [`
    :host { display: block; }
    .panel { padding: 26px; border-radius: 24px; background: var(--surface); border: 1px solid var(--border); box-shadow: var(--shadow-sm); }
    header { display: flex; gap: 14px; align-items: flex-start; flex-wrap: wrap; margin-bottom: 18px; }
    header > div:nth-child(2) { flex: 1; min-width: 220px; }
    .ico { display: grid; place-items: center; width: 46px; height: 46px; border-radius: 14px; background: var(--primary-50); color: var(--primary-600); font-size: 22px; }
    h3 { margin: 0 0 4px; font-size: 18px; color: var(--ink); } header p { margin: 0; color: var(--muted); font-size: 13px; }
    .pill { padding: 6px 14px; border-radius: 99px; font-size: 12px; font-weight: 800; background: var(--surface-2); color: var(--muted); }
    .pill.APPROVED { background: #d1fae5; color: #047857; } .pill.PENDING { background: #fef3c7; color: #b45309; }
    .pill.REJECTED, .pill.SUSPENDED { background: #ffe4e6; color: #be123c; }
    .alert { margin: 0 0 16px; padding: 13px 15px; border-radius: 14px; font-size: 13px; line-height: 1.55; display: flex; gap: 8px; align-items: center; }
    .alert.bad { background: #fff1f2; border: 1px solid #fecdd3; color: #be123c; }
    .alert.wait { background: #fffbeb; border: 1px solid #fde68a; color: #92400e; }
    .alert.ok { background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; }
    .reqs { margin-bottom: 18px; padding: 16px; border-radius: 16px; background: var(--surface-2); }
    .reqs h4 { margin: 0 0 8px; font-size: 13px; color: var(--ink); } .reqs ul { margin: 0; padding-left: 18px; color: var(--muted); font-size: 13px; line-height: 1.8; }
    .reqs li.done { color: #059669; }
    .form { display: grid; gap: 14px; } .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
    label { display: grid; gap: 6px; } label span { font-size: 12px; font-weight: 700; color: var(--muted); } em { font-weight: 500; font-style: normal; }
    input:not([type=checkbox]) { padding: 12px 14px; border: 1.5px solid var(--border); border-radius: 12px; background: var(--surface-2); color: var(--ink); width: 100%; }
    fieldset { margin: 0; padding: 16px; border: 1.5px solid var(--border); border-radius: 16px; display: grid; gap: 12px; } legend { padding: 0 8px; font-size: 12px; font-weight: 800; color: var(--ink); }
    .check { grid-template-columns: auto 1fr; align-items: start; gap: 10px; } .check span { font-weight: 500; line-height: 1.5; color: var(--ink); }
    .row { display: flex; gap: 10px; flex-wrap: wrap; }
    .btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 13px 20px; border: 0; border-radius: 14px; background: var(--grad-primary); color: #fff; font-weight: 700; box-shadow: var(--shadow-md); }
    .btn.ghost { background: transparent; color: var(--ink); border: 1.5px solid var(--border); box-shadow: none; } .btn:disabled { opacity: .55; box-shadow: none; transform: none; }
    @media (max-width: 720px) { .grid { grid-template-columns: 1fr; } }
  `]
})
export class HomeServicePanel implements OnChanges {
  @Input({ required: true }) barbershopId!: number;

  private readonly api = inject(HomeServiceApi);
  private readonly toast = inject(ToastService);
  private readonly cdr = inject(ChangeDetectorRef);

  info: HomeServiceInfo | null = null;
  loading = true;
  saving = false;
  error = '';

  radius = 5;
  fee = 8000;
  notice = 3;
  zones = '';
  notes = '';
  kit = false;
  verified = false;
  policy = false;

  private static readonly LABELS: Record<string, string> = {
    NONE: 'No solicitado', PENDING: 'En revisión', APPROVED: 'Aprobado', REJECTED: 'Rechazado', SUSPENDED: 'Suspendido'
  };

  get statusLabel(): string {
    return HomeServicePanel.LABELS[this.info?.status ?? 'NONE'];
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['barbershopId']) this.load();
  }

  private load(): void {
    this.loading = true;
    this.error = '';
    this.api.get(this.barbershopId).subscribe({
      next: info => { this.apply(info); this.loading = false; this.cdr.detectChanges(); },
      error: err => {
        this.loading = false;
        this.error = apiError(err, 'No se pudo cargar el servicio a domicilio.');
        this.cdr.detectChanges();
      }
    });
  }

  private apply(info: HomeServiceInfo): void {
    this.info = info;
    if (info.radius_km) this.radius = info.radius_km;
    this.fee = info.fee ?? this.fee;
    this.notice = info.min_notice_hours ?? this.notice;
    this.zones = info.zones ?? '';
  }

  submit(): void {
    this.saving = true;
    this.error = '';
    this.api.request(this.barbershopId, {
      radius_km: this.radius,
      fee: this.fee,
      min_notice_hours: this.notice,
      zones: this.zones.trim() || null,
      hygiene_kit: this.kit,
      barbers_verified: this.verified,
      accepts_policy: this.policy,
      notes: this.notes.trim() || null
    }).subscribe({
      next: info => { this.apply(info); this.saving = false; this.toast.success('Solicitud enviada. Te avisaremos por correo.'); this.cdr.detectChanges(); },
      error: err => { this.saving = false; this.error = apiError(err, 'No se pudo enviar la solicitud.'); this.cdr.detectChanges(); }
    });
  }

  saveTerms(): void {
    this.saving = true;
    this.error = '';
    this.api.updateTerms(this.barbershopId, { fee: this.fee, min_notice_hours: this.notice, zones: this.zones.trim() || null }).subscribe({
      next: info => { this.apply(info); this.saving = false; this.toast.success('Cambios guardados.'); this.cdr.detectChanges(); },
      error: err => { this.saving = false; this.error = apiError(err, 'No se pudieron guardar los cambios.'); this.cdr.detectChanges(); }
    });
  }

  disable(): void {
    if (!confirm('¿Desactivar el servicio a domicilio? Tendrás que solicitarlo de nuevo para reactivarlo.')) return;
    this.saving = true;
    this.api.disable(this.barbershopId).subscribe({
      next: info => { this.apply(info); this.saving = false; this.toast.success('Servicio a domicilio desactivado.'); this.cdr.detectChanges(); },
      error: err => { this.saving = false; this.error = apiError(err, 'No se pudo desactivar.'); this.cdr.detectChanges(); }
    });
  }
}
