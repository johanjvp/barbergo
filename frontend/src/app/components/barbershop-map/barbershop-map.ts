import {
  AfterViewInit,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnChanges,
  OnDestroy,
  Output,
  SimpleChanges,
  ViewChild
} from '@angular/core';

import * as L from 'leaflet';

import type {
  LatLngTuple
} from 'leaflet';

import {
  BarbershopDiscoveryItem
} from '../../models/barbershop';


type ShopId = BarbershopDiscoveryItem['id'];


@Component({
  selector: 'app-barbershop-map',
  imports: [],
  templateUrl: './barbershop-map.html',
  styleUrl: './barbershop-map.scss'
})
export class BarbershopMap
  implements AfterViewInit, OnChanges, OnDestroy {


  // =====================================================
  // DATOS RECIBIDOS DESDE LA PÁGINA
  // =====================================================

  @Input()
  shops: BarbershopDiscoveryItem[] = [];

  /** Id de la barbería a resaltar (por ejemplo, al pasar el mouse por su tarjeta). */
  @Input()
  highlightedId: ShopId | null = null;


  // =====================================================
  // EVENTOS HACIA LA PÁGINA
  // =====================================================

  /** Mouse sobre un marcador (id) o fuera de él (null). */
  @Output()
  shopHover = new EventEmitter<ShopId | null>();

  /** Clic en un marcador. También funciona en móvil. */
  @Output()
  shopSelect = new EventEmitter<ShopId>();


  // =====================================================
  // CONTENEDOR DEL MAPA
  // =====================================================

  @ViewChild(
    'mapContainer',
    {
      static: true
    }
  )
  mapContainer!: ElementRef<HTMLDivElement>;


  // =====================================================
  // INSTANCIAS LEAFLET
  // =====================================================

  private map?: L.Map;

  private barberLayer =
    L.layerGroup();

  // id de barbería -> marcador (para poder resaltarlo)
  private markers =
    new Map<ShopId, L.Marker>();

  private userMarker?: L.Marker;

  private userAccuracyCircle?: L.Circle;


  // =====================================================
  // GEOLOCALIZACIÓN
  // =====================================================

  private locationWatchId:
    number | null = null;


  locationError = '';

  locating = false;

  userLocated = false;


  // =====================================================
  // CENTRO INICIAL DE BARRANQUILLA
  // =====================================================

  private readonly barranquillaCenter:
    LatLngTuple = [
      10.96854,
      -74.78132
    ];


  // =====================================================
  // ICONO DE BARBERÍA
  //
  // Se crea una sola vez y se reutiliza.
  // =====================================================

  private readonly barbershopIcon =
    L.divIcon({

      className:
        'barbergo-marker-wrapper',

      html: `
        <div class="barbergo-marker">
          <span>✂</span>
        </div>
      `,

      iconSize: [44, 44],

      iconAnchor: [22, 44]

    });


  // =====================================================
  // ICONO DEL USUARIO
  // =====================================================

  private readonly userIcon =
    L.divIcon({

      className:
        'user-marker-wrapper',

      html: `
        <div class="user-marker">
          <div class="user-marker-dot"></div>
        </div>
      `,

      iconSize: [28, 28],

      iconAnchor: [14, 14]

    });


  // =====================================================
  // CICLO DE VIDA
  // =====================================================

  ngAfterViewInit(): void {

    this.initializeMap();

    this.renderBarbershops();

    this.watchUserLocation();

  }


  ngOnChanges(
    changes: SimpleChanges
  ): void {

    if (!this.map) {
      return;
    }

    if (changes['shops']) {

      this.renderBarbershops();

    }

    else if (changes['highlightedId']) {

      this.applyHighlight();

    }

  }


  ngOnDestroy(): void {

    if (
      this.locationWatchId !== null
    ) {

      navigator.geolocation
        .clearWatch(
          this.locationWatchId
        );

    }


    this.markers.clear();

    this.map?.remove();

  }


  // =====================================================
  // INICIALIZAR MAPA
  // =====================================================

  private initializeMap(): void {

    this.map = L.map(
      this.mapContainer.nativeElement,
      {
        center:
          this.barranquillaCenter,

        zoom:
          12,

        zoomControl:
          false
      }
    );


    // ---------------------------------------------------
    // CAPA OPENSTREETMAP
    // ---------------------------------------------------

    L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        maxZoom:
          19,

        attribution:
          '&copy; OpenStreetMap contributors'
      }
    )
      .addTo(
        this.map
      );


    // ---------------------------------------------------
    // CONTROL DE ZOOM
    // ---------------------------------------------------

    L.control
      .zoom({
        position:
          'bottomright'
      })
      .addTo(
        this.map
      );


    // ---------------------------------------------------
    // CAPA DE BARBERÍAS
    // ---------------------------------------------------

    this.barberLayer
      .addTo(
        this.map
      );


    // ---------------------------------------------------
    // ASEGURAR DIMENSIONES CORRECTAS
    // ---------------------------------------------------

    requestAnimationFrame(
      () => {

        this.map?.invalidateSize();

      }
    );

  }


  // =====================================================
  // RENDERIZAR BARBERÍAS
  // =====================================================

  private renderBarbershops(): void {

    if (
      !this.map
    ) {

      return;

    }


    // Limpiar marcadores anteriores

    this.barberLayer
      .clearLayers();

    this.markers
      .clear();


    const bounds:
      LatLngTuple[] = [];


    // ---------------------------------------------------
    // CREAR MARCADORES
    // ---------------------------------------------------

    for (
      const shop
      of this.shops
    ) {

      if (
        shop.latitude === null
        ||
        shop.longitude === null
      ) {

        continue;

      }


      const latitude =
        Number(
          shop.latitude
        );


      const longitude =
        Number(
          shop.longitude
        );


      if (
        !Number.isFinite(latitude)
        ||
        !Number.isFinite(longitude)
      ) {

        continue;

      }


      const position:
        LatLngTuple = [
          latitude,
          longitude
        ];


      bounds.push(
        position
      );


      const marker =
        L.marker(
          position,
          {
            icon:
              this.barbershopIcon,

            title:
              shop.name
          }
        );


      // -------------------------------------------------
      // EVENTOS: la tarjeta flotante la pinta la página
      // -------------------------------------------------

      marker.on(
        'mouseover',
        () => this.shopHover.emit(shop.id)
      );

      marker.on(
        'mouseout',
        () => this.shopHover.emit(null)
      );

      marker.on(
        'click',
        () => this.shopSelect.emit(shop.id)
      );


      marker
        .addTo(
          this.barberLayer
        );


      this.markers
        .set(
          shop.id,
          marker
        );

    }


    // El resaltado actual se reaplica sobre los marcadores nuevos
    this.applyHighlight();


    // ---------------------------------------------------
    // AJUSTAR MAPA A TODAS LAS BARBERÍAS
    // ---------------------------------------------------

    if (
      bounds.length > 1
    ) {

      const leafletBounds =
        L.latLngBounds(
          bounds
        );


      this.map
        .fitBounds(
          leafletBounds,
          {
            padding: [
              40,
              40
            ],

            maxZoom:
              14
          }
        );

    }

    else if (
      bounds.length === 1
    ) {

      this.map
        .setView(
          bounds[0],
          15
        );

    }

    else {

      this.map
        .setView(
          this.barranquillaCenter,
          12
        );

    }

  }


  // =====================================================
  // RESALTAR MARCADOR ACTIVO
  // =====================================================

  private applyHighlight(): void {

    this.markers.forEach(
      (marker, id) => {

        const active =
          id === this.highlightedId;

        // Sube el marcador activo por encima de los demás
        marker.setZIndexOffset(
          active ? 900 : 0
        );

        marker
          .getElement()
          ?.querySelector('.barbergo-marker')
          ?.classList
          .toggle(
            'is-active',
            active
          );

      }
    );

  }


  // =====================================================
  // OBTENER UBICACIÓN DEL USUARIO
  // =====================================================

  private watchUserLocation(): void {

    if (
      !navigator.geolocation
    ) {

      this.locationError =
        'Este navegador no permite obtener tu ubicación.';

      return;

    }


    this.locating =
      true;


    this.locationWatchId =
      navigator.geolocation
        .watchPosition(

          // =============================================
          // UBICACIÓN OBTENIDA
          // =============================================

          (position) => {

            const latitude =
              position.coords.latitude;


            const longitude =
              position.coords.longitude;


            const accuracy =
              position.coords.accuracy;


            this.updateUserLocation(
              latitude,
              longitude,
              accuracy
            );


            this.locationError =
              '';

            this.locating =
              false;

          },


          // =============================================
          // ERROR DE GEOLOCALIZACIÓN
          // =============================================

          (error) => {

            console.warn(
              'Error de geolocalización:',
              error
            );


            this.locating =
              false;


            switch (
              error.code
            ) {

              case error.PERMISSION_DENIED:

                this.locationError =
                  'Permite el acceso a tu ubicación para mostrar barberías cercanas.';

                break;


              case error.POSITION_UNAVAILABLE:

                this.locationError =
                  'No pudimos determinar tu ubicación actual.';

                break;


              case error.TIMEOUT:

                this.locationError =
                  'La ubicación está tardando demasiado en responder.';

                break;


              default:

                this.locationError =
                  'No pudimos acceder a tu ubicación.';

            }

          },


          // =============================================
          // OPCIONES
          // =============================================

          {
            enableHighAccuracy:
              true,

            maximumAge:
              5000,

            timeout:
              15000
          }

        );

  }


  // =====================================================
  // ACTUALIZAR UBICACIÓN DEL USUARIO
  // =====================================================

  private updateUserLocation(
    latitude: number,
    longitude: number,
    accuracy: number
  ): void {

    if (
      !this.map
    ) {

      return;

    }


    const position:
      LatLngTuple = [
        latitude,
        longitude
      ];


    // ---------------------------------------------------
    // MARCADOR DEL USUARIO
    // ---------------------------------------------------

    if (
      !this.userMarker
    ) {

      this.userMarker =
        L.marker(
          position,
          {
            icon:
              this.userIcon,

            zIndexOffset:
              1000
          }
        )
          .bindPopup(
            `
              <div class="user-popup">
                <strong>
                  Estás aquí
                </strong>
              </div>
            `
          )
          .addTo(
            this.map
          );

    }

    else {

      this.userMarker
        .setLatLng(
          position
        );

    }


    // ---------------------------------------------------
    // CÍRCULO DE PRECISIÓN
    // ---------------------------------------------------

    if (
      !this.userAccuracyCircle
    ) {

      this.userAccuracyCircle =
        L.circle(
          position,
          {
            radius:
              accuracy,

            weight:
              1,

            opacity:
              0.25,

            fillOpacity:
              0.07
          }
        )
          .addTo(
            this.map
          );

    }

    else {

      this.userAccuracyCircle
        .setLatLng(
          position
        )
        .setRadius(
          accuracy
        );

    }


    // ---------------------------------------------------
    // IMPORTANTE:
    //
    // NO hacemos setView() automáticamente.
    //
    // El mapa permanece mostrando las barberías.
    // Si el usuario quiere centrarse en sí mismo,
    // utiliza el botón "Mi ubicación".
    // ---------------------------------------------------

    if (
      !this.userLocated
    ) {

      this.userLocated =
        true;

    }

  }


  // =====================================================
  // CENTRAR EN EL USUARIO
  // =====================================================

  centerOnUser(): void {

    if (
      !this.map
      ||
      !this.userMarker
    ) {

      return;

    }


    this.map
      .flyTo(
        this.userMarker
          .getLatLng(),

        15,

        {
          duration:
            0.8
        }
      );

  }


  // =====================================================
  // MOSTRAR TODAS LAS BARBERÍAS
  // =====================================================

  showAllBarbershops(): void {

    if (
      !this.map
    ) {

      return;

    }


    const coordinates:
      LatLngTuple[] =
      this.shops

        .filter(
          shop =>
            shop.latitude !== null
            &&
            shop.longitude !== null
        )

        .map(
          shop => [

            Number(
              shop.latitude
            ),

            Number(
              shop.longitude
            )

          ] as LatLngTuple
        )

        .filter(
          coordinates =>
            Number.isFinite(
              coordinates[0]
            )
            &&
            Number.isFinite(
              coordinates[1]
            )
        );


    // ---------------------------------------------------
    // SIN BARBERÍAS
    // ---------------------------------------------------

    if (
      coordinates.length === 0
    ) {

      this.map
        .setView(
          this.barranquillaCenter,
          12
        );

      return;

    }


    // ---------------------------------------------------
    // UNA BARBERÍA
    // ---------------------------------------------------

    if (
      coordinates.length === 1
    ) {

      this.map
        .setView(
          coordinates[0],
          15
        );

      return;

    }


    // ---------------------------------------------------
    // VARIAS BARBERÍAS
    // ---------------------------------------------------

    const bounds =
      L.latLngBounds(
        coordinates
      );


    this.map
      .fitBounds(
        bounds,
        {
          padding: [
            45,
            45
          ],

          maxZoom:
            14
        }
      );

  }

}
