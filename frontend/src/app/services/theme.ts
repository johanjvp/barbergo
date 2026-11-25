import { Injectable } from '@angular/core';

export type Theme = 'light' | 'dark';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly key = 'barbergo-theme';
  theme: Theme = 'light';

  constructor() {
    const saved = localStorage.getItem(this.key) as Theme | null;
    const prefersDark = matchMedia('(prefers-color-scheme: dark)').matches;
    this.apply(saved ?? (prefersDark ? 'dark' : 'light'));
  }

  toggle(): void {
    this.apply(this.theme === 'dark' ? 'light' : 'dark', true);
  }

  private apply(theme: Theme, animate = false): void {
    this.theme = theme;
    const root = document.documentElement;
    if (animate) {
      root.classList.add('theme-transition');
      setTimeout(() => root.classList.remove('theme-transition'), 500);
    }
    root.setAttribute('data-theme', theme);
    localStorage.setItem(this.key, theme);
  }
}
