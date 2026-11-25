import { Icon } from '../../../components/icon/icon';
import {
  ChangeDetectorRef,
  Component,
  OnDestroy,
  OnInit,
  inject
} from '@angular/core';

import {
  RouterLink
} from '@angular/router';

import {
  HttpErrorResponse
} from '@angular/common/http';

import {
  AdminBarbershopService
} from '../../../services/admin-barbershop';

import {
  AdminBarbershopItem,
  AdminBarbershopListResponse
} from '../../../models/admin-barbershop';


@Component({
  selector:
    'app-admin-barbershops',

  imports: [
    Icon,
    RouterLink
  ],

  templateUrl:
    './admin-barbershops.html',

  styleUrl:
    './admin-barbershops.scss'
})
export class AdminBarbershops
  implements OnInit, OnDestroy {


  // =====================================================
  // DEPENDENCIAS
  // =====================================================

  private readonly service =
    inject(
      AdminBarbershopService
    );


  private readonly cdr =
    inject(
      ChangeDetectorRef
    );


  // =====================================================
  // DATOS
  // =====================================================

  barbershops:
    AdminBarbershopItem[] = [];


  total =
    0;


  // =====================================================
  // PAGINACIÓN PROGRESIVA
  // =====================================================

  readonly pageSize =
    12;


  offset =
    0;


  loadingMore =
    false;


  // =====================================================
  // ESTADOS
  // =====================================================

  loading =
    true;


  error =
    '';


  updatingId:
    number | null =
      null;


  // =====================================================
  // FILTROS
  // =====================================================

  search =
    '';


  statusFilter:
    'all'
    |
    'active'
    |
    'inactive' =
      'all';


  // =====================================================
  // DEBOUNCE DE BÚSQUEDA
  // =====================================================

  private searchTimeout:
    ReturnType<typeof setTimeout>
    |
    null =
      null;


  // =====================================================
  // GETTERS PAGINACIÓN
  // =====================================================

  get hasMore(): boolean {

    return (
      this.barbershops.length
      <
      this.total
    );

  }


  get remainingCount(): number {

    return Math.max(
      0,
      this.total
      -
      this.barbershops.length
    );

  }


  get loadProgress(): number {

    if (
      this.total <= 0
    ) {

      return 0;

    }


    return Math.min(
      100,
      (
        this.barbershops.length
        /
        this.total
      )
      *
      100
    );

  }


  // =====================================================
  // INICIO
  // =====================================================

  ngOnInit(): void {

    this.loadBarbershops(
      true
    );

  }


  // =====================================================
  // DESTRUIR
  // =====================================================

  ngOnDestroy(): void {

    if (
      this.searchTimeout !==
      null
    ) {

      clearTimeout(
        this.searchTimeout
      );


      this.searchTimeout =
        null;

    }

  }


  // =====================================================
  // CARGAR BARBERÍAS
  // =====================================================

  loadBarbershops(
    reset = true
  ): void {


    // -----------------------------------------------------
    // CARGA INICIAL / NUEVA BÚSQUEDA / NUEVO FILTRO
    // -----------------------------------------------------

    if (
      reset
    ) {

      this.offset =
        0;


      this.loading =
        true;


      this.loadingMore =
        false;


      this.error =
        '';

    }


    // -----------------------------------------------------
    // CARGAR MÁS
    // -----------------------------------------------------

    else {

      if (
        this.loadingMore
        ||
        !this.hasMore
      ) {

        return;

      }


      this.loadingMore =
        true;

    }


    this.service
      .getAll(
        this.search,
        this.statusFilter,
        this.pageSize,
        this.offset
      )
      .subscribe({

        next: (
          response:
            AdminBarbershopListResponse
        ) => {


          // -------------------------------------------------
          // SI ES UNA NUEVA CONSULTA
          // REEMPLAZAMOS LOS DATOS
          // -------------------------------------------------

          if (
            reset
          ) {

            this.barbershops =
              response.items;

          }


          // -------------------------------------------------
          // SI ES "CARGAR MÁS"
          // AGREGAMOS LOS NUEVOS RESULTADOS
          // -------------------------------------------------

          else {

            this.barbershops = [
              ...this.barbershops,
              ...response.items
            ];

          }


          this.total =
            response.total;


          // -------------------------------------------------
          // EL SIGUIENTE OFFSET ES LA CANTIDAD YA CARGADA
          // -------------------------------------------------

          this.offset =
            this.barbershops.length;


          this.loading =
            false;


          this.loadingMore =
            false;


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error cargando barberías:',
            error
          );


          // -------------------------------------------------
          // SOLO BORRAMOS TODO SI FALLÓ
          // LA CONSULTA PRINCIPAL
          // -------------------------------------------------

          if (
            reset
          ) {

            this.barbershops =
              [];


            this.total =
              0;

          }


          if (
            error.status ===
            401
          ) {

            this.error =
              'Tu sesión ha expirado.';

          }

          else if (
            error.status ===
            403
          ) {

            this.error =
              'No tienes permisos para consultar barberías.';

          }

          else {

            this.error =
              'No fue posible cargar las barberías.';

          }


          this.loading =
            false;


          this.loadingMore =
            false;


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // CARGAR MÁS
  // =====================================================

  loadMore(): void {

    this.loadBarbershops(
      false
    );

  }


  // =====================================================
  // BÚSQUEDA
  // =====================================================

  onSearch(
    event: Event
  ): void {

    const target =
      event.target;


    // -----------------------------------------------------
    // VALIDAR INPUT
    // -----------------------------------------------------

    if (
      !(
        target instanceof
        HTMLInputElement
      )
    ) {

      return;

    }


    this.search =
      target.value;


    // -----------------------------------------------------
    // CANCELAR BÚSQUEDA ANTERIOR
    // -----------------------------------------------------

    if (
      this.searchTimeout !==
      null
    ) {

      clearTimeout(
        this.searchTimeout
      );

    }


    // -----------------------------------------------------
    // ESPERAR 350 MS
    // -----------------------------------------------------

    this.searchTimeout =
      setTimeout(
        () => {

          this.searchTimeout =
            null;


          // -----------------------------------------------
          // UNA BÚSQUEDA SIEMPRE REINICIA LA PAGINACIÓN
          // -----------------------------------------------

          this.loadBarbershops(
            true
          );

        },
        350
      );

  }


  // =====================================================
  // CAMBIAR FILTRO
  // =====================================================

  setFilter(
    filter:
      'all'
      |
      'active'
      |
      'inactive'
  ): void {

    if (
      this.statusFilter ===
      filter
    ) {

      return;

    }


    this.statusFilter =
      filter;


    // -----------------------------------------------------
    // CAMBIAR FILTRO REINICIA PAGINACIÓN
    // -----------------------------------------------------

    this.loadBarbershops(
      true
    );

  }


  // =====================================================
  // ACTIVAR / DESACTIVAR BARBERÍA
  // =====================================================

  toggleStatus(
    shop:
      AdminBarbershopItem
  ): void {

    // -----------------------------------------------------
    // EVITAR DOS CAMBIOS SIMULTÁNEOS
    // -----------------------------------------------------

    if (
      this.updatingId !==
      null
    ) {

      return;

    }


    const newStatus =
      !shop.is_active;


    this.updatingId =
      shop.id;


    this.service
      .updateStatus(
        shop.id,
        newStatus
      )
      .subscribe({

        next: (
          response
        ) => {

          shop.is_active =
            response.is_active;


          this.updatingId =
            null;


          // -------------------------------------------------
          // SI HAY FILTRO ACTIVO, RECARGAMOS DESDE CERO
          // PORQUE ESA BARBERÍA PUEDE SALIR DEL RESULTADO
          // -------------------------------------------------

          if (
            this.statusFilter !==
            'all'
          ) {

            this.loadBarbershops(
              true
            );

            return;

          }


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error actualizando barbería:',
            error
          );


          this.updatingId =
            null;


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // FORMATO MONEDA
  // =====================================================

  formatCurrency(
    value:
      number
      |
      null
      |
      undefined
  ): string {

    return new Intl
      .NumberFormat(
        'es-CO',
        {
          style:
            'currency',

          currency:
            'COP',

          maximumFractionDigits:
            0
        }
      )
      .format(
        Number(
          value
          ??
          0
        )
      );

  }


  // =====================================================
  // FORMATO FECHA
  // =====================================================

  formatDate(
    value:
      string
      |
      null
      |
      undefined
  ): string {

    if (
      !value
    ) {

      return '—';

    }


    const date =
      new Date(
        value
      );


    if (
      Number.isNaN(
        date.getTime()
      )
    ) {

      return '—';

    }


    return new Intl
      .DateTimeFormat(
        'es-CO',
        {
          day:
            '2-digit',

          month:
            'short',

          year:
            'numeric'
        }
      )
      .format(
        date
      );

  }


  // =====================================================
  // INICIALES
  // =====================================================

  getInitials(
    name:
      string
      |
      null
      |
      undefined
  ): string {

    if (
      !name
      ||
      !name.trim()
    ) {

      return 'BG';

    }


    return name
      .trim()
      .split(
        /\s+/
      )
      .filter(
        item =>
          !!item
      )
      .slice(
        0,
        2
      )
      .map(
        item =>
          item
            .charAt(0)
      )
      .join('')
      .toUpperCase();

  }

}
