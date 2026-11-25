import { TiltDirective } from "../../directives-tilt";
import { Icon } from '../../components/icon/icon';
import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';
import { BarbershopService } from '../../services/barbershop';
import { RevealDirective } from "../../directives-reveal";
import { ParallaxDirective, MagneticDirective } from "../../directives-extra";
import { Compare } from "../../components/compare/compare";

import { Navbar } from '../../components/navbar/navbar';
import { Footer } from '../../components/footer/footer';
import { BarbershopCard } from '../../components/barbershop-card/barbershop-card';

export interface FeaturedShop {
  id: number;
  image: string;
  name: string;
  neighborhood: string;
  price: string;
  distance: string;
  tags: string[];
}

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
export class Home implements OnInit {

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


  // Barberías reales (API). Antes eran datos de ejemplo sin id y el enlace fallaba.
  featuredBarbershops: FeaturedShop[] = [];
  featuredLoading = true;

  private readonly barbershopService = inject(BarbershopService);
  private readonly cdr = inject(ChangeDetectorRef);

  ngOnInit(): void {
    this.barbershopService.discover().subscribe({
      next: response => {
        this.featuredBarbershops = response.items.slice(0, 3).map((shop, i) => ({
          id: shop.id,
          image: ['/images/barbergo/barbershop-1.jpg', '/images/barbergo/barbershop-2.jpg', '/images/barbergo/barbershop-3.jpg'][i % 3],
          name: shop.name,
          neighborhood: shop.neighborhood || shop.city,
          price: shop.starting_price === null
            ? 'Consultar'
            : new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(shop.starting_price),
          distance: shop.distance_km === null ? '' : `${shop.distance_km.toFixed(1)} km`,
          tags: [
            'Corte',
            ...(shop.offers_vip ? ['VIP'] : []),
            ...(shop.offers_home_service ? ['Domicilio'] : []),
            ...(shop.only_men ? ['Hombres'] : [])
          ]
        }));
        this.featuredLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.featuredBarbershops = [];
        this.featuredLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

}
