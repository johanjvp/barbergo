import { Component, ElementRef, Input, ViewChild } from '@angular/core';

/** Slider comparador antes / después. */
@Component({
  selector: 'app-compare',
  standalone: true,
  template: `
    <div class="cmp" #box
         (pointerdown)="start($event)" (pointermove)="drag($event)" (pointerup)="stop()" (pointerleave)="stop()"
         [style.--pos.%]="pos">
      <div class="layer after"><ng-content select="[after]"></ng-content></div>
      <div class="layer before"><ng-content select="[before]"></ng-content></div>
      <span class="tag l">Antes</span><span class="tag r">Después</span>
      <div class="handle"><span>‹ ›</span></div>
      <input type="range" min="0" max="100" [value]="pos" (input)="pos = +$any($event.target).value" aria-label="Comparar antes y después">
    </div>
  `,
  styles: [`
    .cmp { position: relative; overflow: hidden; border-radius: 28px; aspect-ratio: 3/2; user-select: none; touch-action: pan-y;
      cursor: ew-resize; box-shadow: 0 28px 60px -18px rgba(11,31,42,.4); }
    img, .layer, ::ng-deep .layer img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; pointer-events: none; }
    ::ng-deep .layer img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .before { clip-path: inset(0 calc(100% - var(--pos)) 0 0); }
    .handle { position: absolute; top: 0; bottom: 0; left: var(--pos); width: 3px; background: #fff; transform: translateX(-50%); box-shadow: 0 0 20px rgba(0,0,0,.4); }
    .handle span { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); display: grid; place-items: center; width: 48px; height: 48px;
      border-radius: 50%; background: #fff; color: #0f766e; font-weight: 800; letter-spacing: -2px; box-shadow: 0 10px 24px rgba(0,0,0,.3); }
    .tag { position: absolute; top: 16px; padding: 6px 14px; border-radius: 99px; background: rgba(11,31,42,.6); backdrop-filter: blur(8px); color: #fff; font-size: 12px; font-weight: 700; }
    .l { left: 16px; } .r { right: 16px; }
    input { position: absolute; inset: 0; opacity: 0; cursor: ew-resize; width: 100%; height: 100%; }
  `]
})
export class Compare {
  @ViewChild('box', { static: true }) box!: ElementRef<HTMLElement>;
  pos = 50;
  private dragging = false;

  start(e: PointerEvent) { this.dragging = true; this.drag(e); }
  stop() { this.dragging = false; }
  drag(e: PointerEvent) {
    if (!this.dragging) return;
    const r = this.box.nativeElement.getBoundingClientRect();
    this.pos = Math.max(0, Math.min(100, ((e.clientX - r.left) / r.width) * 100));
  }
}
