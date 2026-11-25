import { TiltDirective } from "../../directives-tilt";
import { Icon } from '../icon/icon';

import {
  Component,
  Input
} from '@angular/core';

import {
  RouterLink
} from '@angular/router';


@Component({
  selector: 'app-barbershop-card',

  imports: [
    TiltDirective,
    Icon,
    RouterLink
  ],

  templateUrl: './barbershop-card.html',
  styleUrl: './barbershop-card.scss'
})
export class BarbershopCard {

  @Input()
  id!: number;

  @Input()
  image = '';

  @Input()
  name = '';

  @Input()
  neighborhood = '';

  @Input()
  price = '';

  @Input()
  distance = '';

  @Input()
  tags: string[] = [];

}


