import {
  AfterViewInit,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnDestroy,
  Output,
  ViewChild,
  ChangeDetectorRef,
  inject
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import * as L from 'leaflet';

import { HomeAddressValue } from '../../models/booking';
import { Icon } from '../icon/icon';

function distanceKm(aLat: number, aLng: number, bLat: number, bLng: number): number {
  const r = (v: number) => (v * Math.PI) / 180;
  const h =
    Math.sin(r(bLat - aLat) / 2) ** 2 +
    Math.cos(r(aLat)) * Math.cos(r(bLat)) * Math.sin(r(bLng - aLng) / 2) ** 2;
  return 6371.0088 * 2 * Math.asin(Math.sqrt(h));
}

/**
 * Selector de dirección para servicio a domicilio: texto + pin en el mapa.
 * Muestra la zona de cobertura y solo emite un valor válido si el pin cae dentro.
 */
@Component({
  selector: 'app-home-address',
  standalone: true,
  imports: [FormsModule, Icon],
  template: `
    <div class="box">
      <label class="field">
        <span>Dirección completa</span>
        <input type="text" [(ngModel)]="address" (ngModelChange)="emit()" maxlength="300"
               placeholder="Calle 84 # 50-20, apto 301, barrio Alto Prado" autocomplete="street-address">
      </label>

      <label class="field">
        <span>Indicaciones de acceso <em>(opcional)</em></span>
        <input type="text" [(ngModel)]="notes" (ngModelChange)="emit()" maxlength="300"
               placeholder="Torre B, portería, timbre dañado, llamar al llegar…">
      </label>

      <div class="map-head">
        <span><app-icon name="pin"></app-icon> Toca el mapa para marcar dónde te atenderemos</span>
        <button type="button" class="locate" (click)="useMyLocation()">
          <app-icon name="sparkle"></app-icon> Usar mi ubicación
        </button>
      </div>

      <div #map class="map"></div>

      @if (status === 'out') {
        <p class="msg bad">Ese punto está a {{ distance.toFixed(1) }} km: fuera de la zona de cobertura ({{ radiusKm }} km).</p>
      } @else if (status === 'in') {
        <p class="msg ok"><app-icon name="check"></app-icon> Dentro de la cobertura ({{ distance.toFixed(1) }} km de la barbería).</p>
      } @else {
        <p class="msg">La zona sombreada es donde esta barbería atiende a domicilio.</p>
      }
      @if (geoError) { <p class="msg bad">{{ geoError }}</p> }
    </div>
  `,
  styles: [`
    :host { display: block; }
    .box { display: grid; gap: 14px; }
    .field { display: grid; gap: 6px; }
    .field span { font-size: 12px; font-weight: 700; color: var(--muted); }
    .field em { font-weight: 500; font-style: normal; opacity: .8; }
    .field input { padding: 13px 14px; border: 1.5px solid var(--border); border-radius: 12px; background: var(--surface-2); color: var(--ink); }
    .map-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap; font-size: 13px; font-weight: 600; color: var(--ink); }
    .map-head app-icon { color: var(--primary); }
    .locate { display: inline-flex; align-items: center; gap: 6px; padding: 8px 12px; border: 1.5px solid var(--primary); border-radius: 99px; background: transparent; color: var(--primary-600); font-weight: 700; font-size: 12px; }
    .map { height: 240px; border-radius: 18px; overflow: hidden; border: 1px solid var(--border); z-index: 0; }
    .msg { margin: 0; font-size: 13px; color: var(--muted); display: flex; align-items: center; gap: 6px; }
    .msg.ok { color: var(--ok-text, #059669); font-weight: 600; }
    .msg.bad { color: var(--bad-text, #e11d48); font-weight: 600; }
  `]
})
export class HomeAddress implements AfterViewInit, OnDestroy {
  @Input() shopLat: number | null = null;
  @Input() shopLng: number | null = null;
  @Input() radiusKm: number | null = null;

  @Output() valueChange = new EventEmitter<HomeAddressValue | null>();

  @ViewChild('map', { static: true }) mapEl!: ElementRef<HTMLElement>;

  private readonly cdr = inject(ChangeDetectorRef);
  private map?: L.Map;
  private pin?: L.CircleMarker;

  address = '';
  notes = '';
  geoError = '';
  distance = 0;
  status: 'idle' | 'in' | 'out' = 'idle';
  private point: { lat: number; lng: number } | null = null;

  ngAfterViewInit(): void {
    const lat = this.shopLat ?? 10.9685;
    const lng = this.shopLng ?? -74.7813;

    this.map = L.map(this.mapEl.nativeElement, { zoomControl: true, attributionControl: true })
      .setView([lat, lng], this.radiusKm && this.radiusKm > 8 ? 11 : 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap'
    }).addTo(this.map);

    if (this.shopLat !== null && this.shopLng !== null) {
      L.circleMarker([lat, lng], { radius: 9, color: '#0f766e', weight: 3, fillColor: '#14b8a6', fillOpacity: 1 })
        .addTo(this.map)
        .bindTooltip('Barbería');

      if (this.radiusKm) {
        const circle = L.circle([lat, lng], {
          radius: this.radiusKm * 1000,
          color: '#0d9488',
          weight: 2,
          fillColor: '#14b8a6',
          fillOpacity: 0.12
        }).addTo(this.map);
        this.map.fitBounds(circle.getBounds(), { padding: [16, 16] });
      }
    }

    this.map.on('click', (e: L.LeafletMouseEvent) => this.setPoint(e.latlng.lat, e.latlng.lng));
    setTimeout(() => this.map?.invalidateSize(), 250);
  }

  ngOnDestroy(): void {
    this.map?.remove();
  }

  useMyLocation(): void {
    this.geoError = '';
    if (!navigator.geolocation) {
      this.geoError = 'Tu navegador no permite obtener la ubicación.';
      return;
    }
    navigator.geolocation.getCurrentPosition(
      pos => {
        this.setPoint(pos.coords.latitude, pos.coords.longitude);
        this.map?.setView([pos.coords.latitude, pos.coords.longitude], 15);
        this.cdr.detectChanges();
      },
      () => {
        this.geoError = 'No pudimos obtener tu ubicación. Márcala en el mapa.';
        this.cdr.detectChanges();
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  }

  private setPoint(lat: number, lng: number): void {
    this.point = { lat, lng };
    this.geoError = '';

    if (this.pin) {
      this.pin.setLatLng([lat, lng]);
    } else if (this.map) {
      this.pin = L.circleMarker([lat, lng], { radius: 10, color: '#be123c', weight: 3, fillColor: '#fb7185', fillOpacity: 1 }).addTo(this.map);
    }

    if (this.shopLat !== null && this.shopLng !== null && this.radiusKm) {
      this.distance = distanceKm(this.shopLat, this.shopLng, lat, lng);
      this.status = this.distance <= this.radiusKm ? 'in' : 'out';
    } else {
      this.status = 'in';
    }
    this.emit();
    this.cdr.detectChanges();
  }

  emit(): void {
    const valid = this.point && this.status !== 'out' && this.address.trim().length >= 6;
    this.valueChange.emit(
      valid
        ? {
            address: this.address.trim(),
            latitude: +this.point!.lat.toFixed(7),
            longitude: +this.point!.lng.toFixed(7),
            access_notes: this.notes.trim() || null
          }
        : null
    );
  }
}
