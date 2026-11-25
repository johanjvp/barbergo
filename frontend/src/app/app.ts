import { Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Toasts } from './components/toasts/toasts';
import { ThemeService } from './services/theme';

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    Toasts
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  // Instanciar el servicio aplica el tema guardado desde el arranque.
  private readonly theme = inject(ThemeService);
}
