import { Component, inject } from '@angular/core';
import { ToastService } from '../../services/toast';
import { Icon } from '../icon/icon';

@Component({
  selector: 'app-toasts',
  standalone: true,
  imports: [Icon],
  template: `
    <div class="stack" aria-live="polite">
      @for (t of toast.toasts(); track t.id) {
        <div class="toast" [class]="t.type" (click)="toast.dismiss(t.id)">
          <span class="ico">
            <app-icon [name]="t.type === 'error' ? 'shield' : t.type === 'success' ? 'check' : 'sparkle'"></app-icon>
          </span>
          <span>{{ t.message }}</span>
        </div>
      }
    </div>
  `,
  styles: [`
    .stack { position: fixed; right: 20px; bottom: 20px; z-index: 1000; display: flex; flex-direction: column; gap: 10px; }
    .toast { display: flex; align-items: center; gap: 12px; min-width: 260px; max-width: 360px; padding: 14px 18px; border-radius: 18px;
      background: rgba(11,31,42,.92); color: #fff; backdrop-filter: blur(16px); box-shadow: 0 18px 40px -12px rgba(0,0,0,.45);
      font-size: 14px; font-weight: 600; cursor: pointer; animation: in .45s cubic-bezier(.22,1,.36,1) both; }
    .ico { display: grid; place-items: center; width: 30px; height: 30px; border-radius: 10px; font-size: 16px; background: #0d9488; }
    .error .ico { background: #e11d48; }
    .info .ico { background: #0ea5e9; }
    @keyframes in { from { opacity: 0; transform: translateX(40px) scale(.95); } to { opacity: 1; transform: none; } }
    @media (max-width: 600px) { .stack { left: 14px; right: 14px; bottom: 14px; } .toast { min-width: 0; max-width: none; } }
  `]
})
export class Toasts {
  readonly toast = inject(ToastService);
}
