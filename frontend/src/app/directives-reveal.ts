import { Directive, ElementRef, OnDestroy, OnInit, inject } from '@angular/core';

/** Adds `.reveal` and toggles `.visible` once the element scrolls into view. */
@Directive({ selector: '[appReveal]', standalone: true })
export class RevealDirective implements OnInit, OnDestroy {
  private el = inject(ElementRef<HTMLElement>);
  private io?: IntersectionObserver;

  ngOnInit() {
    const node = this.el.nativeElement as HTMLElement;
    node.classList.add('reveal');
    this.io = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) { node.classList.add('visible'); this.io?.disconnect(); }
    }, { threshold: 0.12 });
    this.io.observe(node);
  }

  ngOnDestroy() { this.io?.disconnect(); }
}
