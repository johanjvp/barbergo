import { AfterViewInit, Component, ElementRef, OnDestroy, ViewChild } from '@angular/core';

/** Lluvia de confeti sobre un canvas (se lanza al montarse). */
@Component({
  selector: 'app-confetti',
  standalone: true,
  template: `<canvas #cv></canvas>`,
  styles: [`
    :host { position: fixed; inset: 0; pointer-events: none; z-index: 2000; }
    canvas { width: 100%; height: 100%; display: block; }
  `]
})
export class Confetti implements AfterViewInit, OnDestroy {
  @ViewChild('cv', { static: true }) cv!: ElementRef<HTMLCanvasElement>;
  private raf = 0;

  ngAfterViewInit(): void {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const canvas = this.cv.nativeElement;
    const ctx = canvas.getContext('2d')!;
    const w = (canvas.width = window.innerWidth);
    const h = (canvas.height = window.innerHeight);
    const colors = ['#0d9488', '#14b8a6', '#fb7185', '#f97316', '#fde047', '#0ea5e9', '#ffffff'];

    const bits = Array.from({ length: 160 }, () => ({
      x: w / 2 + (Math.random() - 0.5) * 120,
      y: h * 0.4,
      vx: (Math.random() - 0.5) * 16,
      vy: -Math.random() * 16 - 4,
      s: Math.random() * 8 + 4,
      r: Math.random() * Math.PI,
      vr: (Math.random() - 0.5) * 0.4,
      c: colors[Math.floor(Math.random() * colors.length)],
      round: Math.random() > 0.6
    }));

    let frame = 0;
    const draw = () => {
      ctx.clearRect(0, 0, w, h);
      for (const b of bits) {
        b.vy += 0.35; b.vx *= 0.99; b.x += b.vx; b.y += b.vy; b.r += b.vr;
        ctx.save();
        ctx.globalAlpha = Math.max(0, 1 - frame / 170);
        ctx.translate(b.x, b.y); ctx.rotate(b.r); ctx.fillStyle = b.c;
        if (b.round) { ctx.beginPath(); ctx.arc(0, 0, b.s / 2, 0, 7); ctx.fill(); }
        else ctx.fillRect(-b.s / 2, -b.s / 4, b.s, b.s / 2);
        ctx.restore();
      }
      if (++frame < 180) this.raf = requestAnimationFrame(draw);
      else ctx.clearRect(0, 0, w, h);
    };
    draw();
  }

  ngOnDestroy(): void { cancelAnimationFrame(this.raf); }
}
