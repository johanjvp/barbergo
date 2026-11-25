import { Directive, ElementRef, HostListener, inject } from '@angular/core';

/**
 * Efecto 3D estilo Apple: la tarjeta se inclina siguiendo el cursor
 * y muestra un brillo suave. Uso: <div appTilt>...</div>
 */
@Directive({ selector: '[appTilt]', standalone: true })
export class TiltDirective {
  private el = inject<ElementRef<HTMLElement>>(ElementRef).nativeElement;
  private reduce = typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;
  private touch = typeof matchMedia !== 'undefined' && matchMedia('(hover: none)').matches;

  constructor() {
    this.el.classList.add('tilt');
  }

  @HostListener('pointermove', ['$event'])
  move(e: PointerEvent) {
    if (this.reduce || this.touch) return;
    const r = this.el.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width;
    const y = (e.clientY - r.top) / r.height;
    this.el.style.setProperty('--rx', `${(0.5 - y) * 4}deg`);
    this.el.style.setProperty('--ry', `${(x - 0.5) * 5}deg`);
    this.el.style.setProperty('--mx', `${x * 100}%`);
    this.el.style.setProperty('--my', `${y * 100}%`);
  }

  @HostListener('pointerleave')
  leave() {
    this.el.style.setProperty('--rx', '0deg');
    this.el.style.setProperty('--ry', '0deg');
  }
}
