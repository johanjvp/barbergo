import { TiltDirective } from "../../directives-tilt";
import { Icon } from '../../components/icon/icon';
import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { RevealDirective } from "../../directives-reveal";
import { ParallaxDirective, MagneticDirective } from "../../directives-extra";
import { Compare } from "../../components/compare/compare";

import { Navbar } from '../../components/navbar/navbar';
import { Footer } from '../../components/footer/footer';
import { BarbershopCard } from '../../components/barbershop-card/barbershop-card';

@Component({
  selector: 'app-home',
  imports: [
    Icon,
    RevealDirective,
    TiltDirective,
    ParallaxDirective,
    MagneticDirective,
    Compare,
    Navbar,
    Footer,
    BarbershopCard
  ],
  templateUrl: './home.html',
  styleUrl: './home.scss'
})
export class Home {

  private readonly router = inject(Router);

  query = '';
  zone = '';
  showSuggest = false;

  private readonly catalog = [
    'Corte clásico', 'Fade', 'Degradado', 'Barba', 'Perfilado de barba',
    'Corte + barba', 'Afeitado con toalla', 'Corte infantil', 'VIP', 'Domicilio'
  ];

  get suggestions(): string[] {
    const q = this.query.trim().toLowerCase();
    const list = q
      ? this.catalog.filter(s => s.toLowerCase().includes(q))
      : this.catalog.slice(0, 5);
    return list.slice(0, 6);
  }

  pick(value: string): void {
    this.query = value;
    this.showSuggest = false;
    this.goSearch();
  }

  hideSuggest(): void {
    setTimeout(() => (this.showSuggest = false), 120);
  }

  goSearch(): void {
    this.router.navigate(['/barberias'], {
      queryParams: {
        search: this.query.trim() || null,
        zona: this.zone.trim() || null
      }
    });
  }


  featuredBarbershops = [

    {
      image:
        '/images/barbergo/barbershop-1.jpg',

      name:
        'District Barber Club',

      neighborhood:
        'Alto Prado',

      price:
        '$25.000',

      distance:
        '1.2 km',

      tags: [
        'Corte',
        'Barba',
        'VIP'
      ]
    },

    {
      image:
        '/images/barbergo/barbershop-2.jpg',

      name:
        'The Gentlemen Room',

      neighborhood:
        'Riomar',

      price:
        '$30.000',

      distance:
        '2.4 km',

      tags: [
        'Corte',
        'Barba',
        'Premium'
      ]
    },

    {
      image:
        '/images/barbergo/barbershop-3.jpg',

      name:
        'Black Chair Studio',

      neighborhood:
        'Villa Country',

      price:
        '$20.000',

      distance:
        '3.1 km',

      tags: [
        'Corte',
        'Fade',
        'Barba'
      ]
    }

  ];

}
