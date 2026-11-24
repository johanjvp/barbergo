import {
  ChangeDetectorRef,
  Component,
  HostListener,
  OnDestroy,
  OnInit,
  inject
} from '@angular/core';

import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { Navbar } from '../../components/navbar/navbar';
import { Footer } from '../../components/footer/footer';
import { BarbershopCard } from '../../components/barbershop-card/barbershop-card';
import { BarbershopMap } from '../../components/barbershop-map/barbershop-map';

import { BarbershopService } from '../../services/barbershop';
import { BarbershopDiscoveryItem } from '../../models/barbershop';


type Shop = BarbershopDiscoveryItem;

/**
 * Barbería + datos ya formateados para la vista.
 * Se calcula una sola vez en applyFilters() en vez de llamar
 * funciones dentro del template en cada ciclo de detección de cambios.
 */
export type ShopView = Shop & {
  image: string;
  priceLabel: string;
  distanceLabel: string;
  tags: string[];
};


@Component({
  selector: 'app-barbershops',

  imports: [
    FormsModule,
    Navbar,
    Footer,
    BarbershopCard,
    BarbershopMap
  ],

  templateUrl: './barbershops.html',
  styleUrl: './barbershops.scss'
})
export class Barbershops implements OnInit, OnDestroy {

  private readonly barbershopService = inject(BarbershopService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly router = inject(Router);


  // ======================================
  // ESTADO
  // ======================================

  barbershops: Shop[] = [];        // respuesta cruda del backend
  visibleShops: ShopView[] = [];   // lista filtrada y lista para pintar

  search = '';
  neighborhood = '';

  loading = false;
  error = '';
  total = 0;

  // Filtros rápidos
  activeFilters = new Set<string>();
  filterOptions = ['VIP', 'Domicilio', 'Hombres'];

  // Tarjeta flotante del mapa, modal y sincronía mapa <-> lista
  previewShop: ShopView | null = null;
  modalShop: ShopView | null = null;
  hoveredId: Shop['id'] | null = null;

  private lastFocused: HTMLElement | null = null;


  // ======================================
  // CICLO DE VIDA
  // ======================================

  ngOnInit(): void {
    this.loadBarbershops();
  }

  ngOnDestroy(): void {
    // Evita que el scroll quede bloqueado si se navega con el modal abierto.
    document.body.style.overflow = '';
  }


  // ======================================
  // CARGA DE DATOS
  // ======================================

  loadBarbershops(): void {

    const startTime = performance.now();

    this.loading = true;
    this.error = '';
    this.previewShop = null;
    this.hoveredId = null;

    // Fuerza actualización inmediata del estado de carga.
    this.cdr.detectChanges();

    this.barbershopService
      .discover(this.search, this.neighborhood)
      .subscribe({

        next: (response) => {

          this.barbershops = response.items;
          this.applyFilters();

          this.loading = false;

          console.log('Barberías recibidas:', this.barbershops.length);
          console.log(
            'Tiempo HTTP + Angular:',
            Math.round(performance.now() - startTime),
            'ms'
          );

          this.cdr.detectChanges();
        },

        error: (error) => {

          console.error('Error cargando barberías:', error);

          this.error = 'No pudimos cargar las barberías.';
          this.loading = false;

          this.cdr.detectChanges();
        }

      });
  }


  searchBarbershops(): void {
    this.loadBarbershops();
  }


  clearFilters(): void {
    this.search = '';
    this.neighborhood = '';
    this.activeFilters.clear();
    this.loadBarbershops();
  }


  // ======================================
  // FILTROS RÁPIDOS
  // ======================================

  applyFilters(): void {

    const active = [...this.activeFilters];

    this.visibleShops = this.barbershops
      .map(shop => ({ shop, tags: this.getTags(shop) }))
      .filter(({ tags }) => active.every(f => tags.includes(f)))
      .map(({ shop, tags }, i): ShopView => ({
        ...shop,
        tags,
        image: this.getImage(i),
        priceLabel: this.getPrice(shop.starting_price),
        distanceLabel: this.getDistance(shop.distance_km)
      }));

    this.total = this.visibleShops.length;
  }


  toggleFilter(filter: string): void {

    if (this.activeFilters.has(filter)) {
      this.activeFilters.delete(filter);
    } else {
      this.activeFilters.add(filter);
    }

    this.previewShop = null;
    this.applyFilters();
  }


  // ======================================
  // MAPA
  // ======================================

  /** Hover sobre un marcador: muestra la tarjeta y resalta la tarjeta de la lista. */
  onMapHover(id: Shop['id'] | null): void {

    this.hoveredId = id;

    // Al salir del marcador NO cerramos la tarjeta,
    // así el usuario puede llevar el mouse hasta ella.
    if (id === null) return;

    this.previewShop = this.visibleShops.find(s => s.id === id) ?? null;
  }


  /** Clic en un marcador (también sirve en móvil, donde no hay hover). */
  onMapSelect(id: Shop['id']): void {
    this.previewShop = this.visibleShops.find(s => s.id === id) ?? null;
  }


  closePreview(): void {
    this.previewShop = null;
  }


  // ======================================
  // MODAL
  // ======================================

  openModal(shop: ShopView): void {

    this.lastFocused = document.activeElement as HTMLElement | null;
    this.modalShop = shop;
    document.body.style.overflow = 'hidden';

    // Lleva el foco al botón de cerrar (accesibilidad con teclado).
    setTimeout(() => {
      document.querySelector<HTMLElement>('.modal-close')?.focus();
    });
  }


  closeModal(): void {

    this.modalShop = null;
    document.body.style.overflow = '';

    this.lastFocused?.focus();
    this.lastFocused = null;
  }


  /** Escape cierra primero el modal; si no hay modal, cierra la tarjeta del mapa. */
  @HostListener('document:keydown.escape')
  onEscape(): void {

    if (this.modalShop) {
      this.closeModal();
    } else if (this.previewShop) {
      this.closePreview();
    }
  }


  // ======================================
  // NAVEGACIÓN
  // ======================================

  goToShop(shop: ShopView): void {

    this.closeModal();

    // AJUSTA esta ruta a la que uses para el detalle de una barbería.
    this.router.navigate(['/barbershops', shop.id]);
  }


  // ======================================
  // HELPERS
  // ======================================

  private getImage(index: number): string {

    const images = [
      '/images/barbergo/barbershop-1.jpg',
      '/images/barbergo/barbershop-2.jpg',
      '/images/barbergo/barbershop-3.jpg'
    ];

    const safeIndex = index < 0 ? 0 : index;

    return images[safeIndex % images.length];
  }


  private getPrice(price: number | null): string {

    if (price === null) {
      return 'Consultar';
    }

    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0
    }).format(price);
  }


  private getDistance(distance: number | null): string {

    if (distance === null) {
      return 'Barranquilla';
    }

    return `${distance.toFixed(1)} km`;
  }


  private getTags(shop: Shop): string[] {

    const tags: string[] = [];

    if (shop.offers_vip) {
      tags.push('VIP');
    }

    if (shop.offers_home_service) {
      tags.push('Domicilio');
    }

    if (shop.only_men) {
      tags.push('Hombres');
    }

    if (tags.length === 0) {
      tags.push('Barbería');
    }

    return tags;
  }

}
