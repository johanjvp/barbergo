import { Icon } from '../icon/icon';
import {
  Component
} from '@angular/core';

import {
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

}
