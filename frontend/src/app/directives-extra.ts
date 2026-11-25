import { Directive, ElementRef, HostListener, Input, OnDestroy, OnInit, inject } from '@angular/core';

const reduceMotion = () => typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;

/**
 * Parallax con el mouse: el contenedor reparte --px/--py (-1..1) y los hijos
 * con [data-depth] se desplazan en capas. Uso: <section appParallax> <i data-depth="30"> </section>
 */
@Directive({ selector: '[appParallax]', standalone: true })
export class ParallaxDirective implements OnInit, OnDestroy {
  private el = inject<ElementRef<HTMLElement>>(ElementRef).nativeElement;
  private onScroll = () => {
    if (reduceMotion()) return;
    this.el.style.setProperty('--sy', String(Math.min(window.scrollY, 700)));
  };

  ngOnInit() { window.addEventListener('scroll', this.onScroll, { passive: true }); }
  ngOnDestroy() { window.removeEventListener('scroll', this.onScroll); }

  @HostListener('pointermove', ['$event'])
  move(e: PointerEvent) {
    if (reduceMotion()) return;
    const r = this.el.getBoundingClientRect();
    this.el.style.setProperty('--px', String(((e.clientX - r.left) / r.width - 0.5) * 2));
    this.el.style.setProperty('--py', String(((e.clientY - r.top) / r.height - 0.5) * 2));
    this.el.style.setProperty('--gx', `${e.clientX - r.left}px`);
    this.el.style.setProperty('--gy', `${e.clientY - r.top}px`);
  }
}

/** Cuenta animada hasta el valor al entrar en pantalla. Uso: <b [appCount]="3500" suffix="+"> */
@Directive({ selector: '[appCount]', standalone: true })
export class CountDirective implements OnInit, OnDestroy {
  @Input('appCount') target = 0;
  @Input() decimals = 0;
  @Input() prefix = '';
  @Input() suffix = '';
  private el = inject<ElementRef<HTMLElement>>(ElementRef).nativeElement;
  private io?: IntersectionObserver;

  ngOnInit() {
    this.render(0);
    this.io = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return;
      this.io?.disconnect();
      if (reduceMotion()) return this.render(this.target);
      const start = performance.now(), dur = 1600;
      const tick = (t: number) => {
        const p = Math.min((t - start) / dur, 1);
        this.render(this.target * (1 - Math.pow(1 - p, 4)));
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    }, { threshold: 0.4 });
    this.io.observe(this.el);
  }
  ngOnDestroy() { this.io?.disconnect(); }

  private render(v: number) {
    const n = v.toLocaleString('es-CO', { minimumFractionDigits: this.decimals, maximumFractionDigits: this.decimals });
    this.el.textContent = `${this.prefix}${n}${this.suffix}`;
  }
}

/** Botón "magnético": se acerca suavemente al cursor. */
@Directive({ selector: '[appMagnetic]', standalone: true })
export class MagneticDirective {
  private el = inject<ElementRef<HTMLElement>>(ElementRef).nativeElement;

  @HostListener('pointermove', ['$event'])
  move(e: PointerEvent) {
    if (reduceMotion() || matchMedia('(hover: none)').matches) return;
    const r = this.el.getBoundingClientRect();
    const x = (e.clientX - (r.left + r.width / 2)) * 0.25;
    const y = (e.clientY - (r.top + r.height / 2)) * 0.35;
    this.el.style.transform = `translate(${x}px, ${y}px)`;
  }

  @HostListener('pointerleave')
  leave() { this.el.style.transform = ''; }
}
