import { Icon } from '../icon/icon';
import {
  Component,
  inject
} from '@angular/core';

import { AuthService } from '../../services/auth';
import { ToastService } from '../../services/toast';

import {
  Router,
  RouterLink,
  RouterLinkActive
} from '@angular/router';


@Component({
  selector:
    'app-admin-sidebar',

  imports: [
    Icon,
    RouterLink,
    RouterLinkActive
  ],

  templateUrl:
    './admin-sidebar.html',

  styleUrl:
    './admin-sidebar.scss'
})
export class AdminSidebar {

  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly toast = inject(ToastService);

  logout(): void {
    this.authService.logout();
    this.toast.success('Sesión cerrada. ¡Hasta pronto!');
    this.router.navigateByUrl('/login');
  }
}
