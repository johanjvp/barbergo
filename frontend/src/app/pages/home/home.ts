import { Component } from '@angular/core';

import { Navbar } from '../../components/navbar/navbar';
import { Footer } from '../../components/footer/footer';
import { BarbershopCard } from '../../components/barbershop-card/barbershop-card';

@Component({
  selector: 'app-home',
  imports: [
    Navbar,
    Footer,
    BarbershopCard
  ],
  templateUrl: './home.html',
  styleUrl: './home.scss'
})
export class Home {

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
