import { Icon } from '../../../components/icon/icon';
import {
  ChangeDetectorRef,
  Component,
  OnDestroy,
  OnInit,
  inject
} from '@angular/core';

import {
  HttpClient,
  HttpErrorResponse
} from '@angular/common/http';

import {
  AdminBookingService
} from '../../../services/admin-booking';

import {
  ScheduleService
} from '../../../services/schedule';

import {
  AdminBookingCalendar
} from '../../../components/admin-booking-calendar/admin-booking-calendar';

import {
  AdminBookingCancelResponse,
  AdminBookingConfirmResponse,
  AdminBookingCompleteResponse,
  AdminBookingItem,
  AdminBookingListResponse,
  AdminBookingStatus,
  AdminBookingSummary
} from '../../../models/admin-booking';

import {
  BarberWeeklyAgenda
} from '../../../models/barber-weekly-agenda';


interface AdminBarbershopOption {

  id: number;

  name: string;

  city:
    string | null;

  neighborhood:
    string | null;

  is_active:
    boolean;

}


interface AdminBarbershopListResponse {

  items:
    AdminBarbershopOption[];

  total:
    number;

}


interface AdminBarberOption {

  id:
    number;

  user_id:
    number;

  barbershop_id:
    number;

  first_name:
    string;

  last_name:
    string;

  is_active:
    boolean;

  service_ids:
    number[];

}


@Component({
  selector: 'app-admin-bookings',

  imports: [
    Icon,
    AdminBookingCalendar
  ],

  templateUrl:
    './admin-bookings.html',

  styleUrl:
    './admin-bookings.scss'
})
export class AdminBookings
  implements OnInit, OnDestroy {


  // =====================================================
  // DEPENDENCIAS
  // =====================================================

  private readonly service =
    inject(
      AdminBookingService
    );


  private readonly scheduleService =
    inject(
      ScheduleService
    );


  private readonly http =
    inject(
      HttpClient
    );


  private readonly cdr =
    inject(
      ChangeDetectorRef
    );


  private readonly apiUrl =
    'http://127.0.0.1:8000/api/v1';


  // =====================================================
  // RESERVAS
  // =====================================================

  bookings:
    AdminBookingItem[] =
      [];


  total =
    0;


  summary:
    AdminBookingSummary = {

      total: 0,

      pending: 0,

      confirmed: 0,

      in_progress: 0,

      completed: 0,

      cancelled: 0,

      rejected: 0,

      no_show: 0,

      today: 0,

      reserved_value: 0

    };


  // =====================================================
  // PAGINACIÓN
  // =====================================================

  readonly pageSize =
    20;


  readonly calendarPageSize =
    100;


  offset =
    0;


  loadingMore =
    false;


  // =====================================================
  // ESTADOS GENERALES
  // =====================================================

  loading =
    true;


  error =
    '';


  // =====================================================
  // BARBERÍAS
  // =====================================================

  barbershops:
    AdminBarbershopOption[] =
      [];


  barbers:
    AdminBarberOption[] =
      [];


  loadingBarbershops =
    false;


  loadingBarbers =
    false;


  // =====================================================
  // FILTROS
  // =====================================================

  search =
    '';


  statusFilter:
    AdminBookingStatus | 'all' =
      'all';


  barbershopId:
    number | null =
      null;


  barberId:
    number | null =
      null;


  dateFrom =
    '';


  dateTo =
    '';


  // =====================================================
  // CALENDARIO
  // =====================================================

  weekStart:
    Date =
      this.getMonday(
        new Date()
      );


  weeklyAgenda:
    BarberWeeklyAgenda | null =
      null;


  loadingAgenda =
    false;


  agendaError =
    '';


  // =====================================================
  // RESERVA SELECCIONADA
  // =====================================================

  selectedBooking:
    AdminBookingItem | null =
      null;


  // =====================================================
  // CONFIRMACIÓN
  // =====================================================

  confirmingBookingId:
    number | null =
      null;


  confirmError =
    '';


  confirmSuccess =
    '';


  // =====================================================
  // CANCELACIÓN
  // =====================================================

  cancellingBookingId:
    number | null =
      null;


  cancelError =
    '';


  cancelSuccess =
    '';


  // =====================================================
  // COMPLETAR
  // =====================================================

  completingBookingId:
    number | null =
      null;


  completeError =
    '';


  completeSuccess =
    '';


  // =====================================================
  // BÚSQUEDA DEBOUNCE
  // =====================================================

  private searchTimeout:
    ReturnType<typeof setTimeout>
    |
    null =
      null;


  // =====================================================
  // INICIO
  // =====================================================

  ngOnInit(): void {

    this.loadBarbershops();


    this.loadBookings(
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
  // HAY MÁS RESULTADOS
  // =====================================================

  get hasMore(): boolean {

    return (
      this.bookings.length
      <
      this.total
    );

  }


  // =====================================================
  // RESULTADOS RESTANTES
  // =====================================================

  get remainingCount(): number {

    return Math.max(
      0,
      this.total
      -
      this.bookings.length
    );

  }


  // =====================================================
  // PROGRESO
  // =====================================================

  get loadProgress(): number {

    if (
      this.total <= 0
    ) {

      return 0;

    }


    return Math.min(
      100,
      (
        this.bookings.length
        /
        this.total
      )
      *
      100
    );

  }


  // =====================================================
  // BARBERO SELECCIONADO
  // =====================================================

  get selectedBarber():
    AdminBarberOption | null {

    if (
      this.barberId ===
      null
    ) {

      return null;

    }


    return (
      this.barbers.find(
        barber =>
          barber.id ===
          this.barberId
      )
      ??
      null
    );

  }


  // =====================================================
  // BARBERÍA SELECCIONADA
  // =====================================================

  get selectedBarbershop():
    AdminBarbershopOption | null {

    if (
      this.barbershopId ===
      null
    ) {

      return null;

    }


    return (
      this.barbershops.find(
        shop =>
          shop.id ===
          this.barbershopId
      )
      ??
      null
    );

  }


  // =====================================================
  // NOMBRE DEL BARBERO
  // =====================================================

  get selectedBarberName():
    string {

    const barber =
      this.selectedBarber;


    if (
      !barber
    ) {

      return 'Agenda';

    }


    return (
      `${barber.first_name} ${barber.last_name}`
        .trim()
    );

  }


  // =====================================================
  // CARGAR BARBERÍAS
  // =====================================================

  loadBarbershops(): void {

    this.loadingBarbershops =
      true;


    this.http
      .get<AdminBarbershopListResponse>(
        `${this.apiUrl}/admin/barbershops`,
        {
          params: {

            status_filter:
              'all',

            limit:
              100,

            offset:
              0

          }
        }
      )
      .subscribe({

        next: (
          response:
            AdminBarbershopListResponse
        ) => {

          this.barbershops =
            response.items
            ??
            [];


          this.loadingBarbershops =
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


          this.barbershops =
            [];


          this.loadingBarbershops =
            false;


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // CAMBIAR BARBERÍA
  // =====================================================

  onBarbershopChange(
    event:
      Event
  ): void {

    const target =
      event.target;


    if (
      !(
        target instanceof
        HTMLSelectElement
      )
    ) {

      return;

    }


    const value =
      Number(
        target.value
      );


    if (
      Number.isInteger(
        value
      )
      &&
      value > 0
    ) {

      this.barbershopId =
        value;

    }

    else {

      this.barbershopId =
        null;

    }


    // ---------------------------------------------------
    // REINICIAR BARBERO Y CALENDARIO
    // ---------------------------------------------------

    this.barberId =
      null;


    this.barbers =
      [];


    this.dateFrom =
      '';


    this.dateTo =
      '';


    this.weekStart =
      this.getMonday(
        new Date()
      );


    this.weeklyAgenda =
      null;


    this.loadingAgenda =
      false;


    this.agendaError =
      '';


    this.closeBooking();


    // ---------------------------------------------------
    // CARGAR BARBEROS
    // ---------------------------------------------------

    if (
      this.barbershopId !==
      null
    ) {

      this.loadBarbers(
        this.barbershopId
      );

    }


    // ---------------------------------------------------
    // CARGAR RESERVAS DE BARBERÍA
    // ---------------------------------------------------

    this.loadBookings(
      true
    );

  }


  // =====================================================
  // CARGAR BARBEROS
  // =====================================================

  loadBarbers(
    barbershopId:
      number
  ): void {

    this.loadingBarbers =
      true;


    this.barbers =
      [];


    this.http
      .get<AdminBarberOption[]>(
        `${this.apiUrl}/barbershops/${barbershopId}/barbers`
      )
      .subscribe({

        next: (
          response:
            AdminBarberOption[]
        ) => {

          this.barbers =
            response
            ??
            [];


          this.loadingBarbers =
            false;


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error cargando barberos:',
            error
          );


          this.barbers =
            [];


          this.loadingBarbers =
            false;


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // SELECCIONAR BARBERO
  // =====================================================

  selectBarber(
    barberId:
      number | null
  ): void {

    if (
      this.barberId ===
      barberId
    ) {

      return;

    }


    this.barberId =
      barberId;


    this.closeBooking();


    // ---------------------------------------------------
    // BARBERO ESPECÍFICO
    // ACTIVAR CALENDARIO SEMANAL
    // ---------------------------------------------------

    if (
      barberId !==
      null
    ) {

      this.goToCurrentWeek();

      return;

    }


    // ---------------------------------------------------
    // TODOS LOS BARBEROS
    // VOLVER A LISTADO GENERAL
    // ---------------------------------------------------

    this.dateFrom =
      '';


    this.dateTo =
      '';


    this.weekStart =
      this.getMonday(
        new Date()
      );


    this.weeklyAgenda =
      null;


    this.loadingAgenda =
      false;


    this.agendaError =
      '';


    this.loadBookings(
      true
    );

  }


  // =====================================================
  // SEMANA ANTERIOR
  // =====================================================

  goToPreviousWeek(): void {

    const previousWeek =
      new Date(
        this.weekStart
      );


    previousWeek.setDate(
      previousWeek.getDate()
      -
      7
    );


    this.setCalendarWeek(
      previousWeek
    );

  }


  // =====================================================
  // SEMANA SIGUIENTE
  // =====================================================

  goToNextWeek(): void {

    const nextWeek =
      new Date(
        this.weekStart
      );


    nextWeek.setDate(
      nextWeek.getDate()
      +
      7
    );


    this.setCalendarWeek(
      nextWeek
    );

  }


  // =====================================================
  // SEMANA ACTUAL
  // =====================================================

  goToCurrentWeek(): void {

    this.setCalendarWeek(
      new Date()
    );

  }


  // =====================================================
  // CONFIGURAR SEMANA
  // =====================================================

  private setCalendarWeek(
    referenceDate:
      Date
  ): void {

    const monday =
      this.getMonday(
        referenceDate
      );


    const sunday =
      new Date(
        monday
      );


    sunday.setDate(
      monday.getDate()
      +
      6
    );


    this.weekStart =
      monday;


    this.dateFrom =
      this.toLocalIsoDate(
        monday
      );


    this.dateTo =
      this.toLocalIsoDate(
        sunday
      );


    this.closeBooking();


    this.loadBookings(
      true
    );


    this.loadWeeklyAgenda();

  }


  // =====================================================
  // CARGAR AGENDA SEMANAL
  // =====================================================

  loadWeeklyAgenda(): void {

    if (
      this.barberId ===
      null
    ) {

      this.weeklyAgenda =
        null;


      this.loadingAgenda =
        false;


      this.agendaError =
        '';


      return;

    }


    this.loadingAgenda =
      true;


    this.agendaError =
      '';


    const weekStart =
      this.toLocalIsoDate(
        this.weekStart
      );


    this.scheduleService
      .getWeeklyAgenda(
        this.barberId,
        weekStart
      )
      .subscribe({

        next: (
          response:
            BarberWeeklyAgenda
        ) => {

          this.weeklyAgenda =
            response;


          this.loadingAgenda =
            false;


          this.agendaError =
            '';


          console.log(
            'AGENDA SEMANAL:',
            response
          );


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error cargando agenda semanal:',
            error
          );


          this.weeklyAgenda =
            null;


          this.loadingAgenda =
            false;


          if (
            error.status ===
            401
          ) {

            this.agendaError =
              'Tu sesión ha expirado.';

          }

          else if (
            error.status ===
            403
          ) {

            this.agendaError =
              'No tienes permisos para consultar esta agenda.';

          }

          else if (
            error.status ===
            404
          ) {

            this.agendaError =
              'El barbero seleccionado no fue encontrado.';

          }

          else {

            this.agendaError =
              'No fue posible cargar la agenda semanal.';

          }


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // OBTENER LUNES DE UNA SEMANA
  // =====================================================

  private getMonday(
    date:
      Date
  ): Date {

    const result =
      new Date(
        date
      );


    const day =
      result.getDay();


    const difference =
      day ===
        0
        ? -6
        : 1
          -
          day;


    result.setDate(
      result.getDate()
      +
      difference
    );


    result.setHours(
      0,
      0,
      0,
      0
    );


    return result;

  }


  // =====================================================
  // FECHA LOCAL YYYY-MM-DD
  // =====================================================

  private toLocalIsoDate(
    date:
      Date
  ): string {

    const year =
      date.getFullYear();


    const month =
      String(
        date.getMonth()
        +
        1
      )
        .padStart(
          2,
          '0'
        );


    const day =
      String(
        date.getDate()
      )
        .padStart(
          2,
          '0'
        );


    return (
      `${year}-${month}-${day}`
    );

  }


  // =====================================================
  // CARGAR RESERVAS
  // =====================================================

  loadBookings(
    reset =
      true
  ): void {

    // ---------------------------------------------------
    // NUEVA CONSULTA
    // ---------------------------------------------------

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


    // ---------------------------------------------------
    // CARGAR MÁS
    // ---------------------------------------------------

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


    // ---------------------------------------------------
    // TAMAÑO DE CONSULTA
    // ---------------------------------------------------

    const requestLimit =
      this.barberId !==
        null
        ? this.calendarPageSize
        : this.pageSize;


    // ---------------------------------------------------
    // CONSULTA
    // ---------------------------------------------------

    this.service
      .getAll(
        this.search,
        this.statusFilter,
        this.barbershopId,
        this.barberId,
        this.dateFrom,
        this.dateTo,
        requestLimit,
        this.offset
      )
      .subscribe({

        next: (
          response:
            AdminBookingListResponse
        ) => {

          // ---------------------------------------------
          // RESET
          // ---------------------------------------------

          if (
            reset
          ) {

            this.bookings =
              response.items;

          }


          // ---------------------------------------------
          // PAGINACIÓN
          // ---------------------------------------------

          else {

            this.bookings = [
              ...this.bookings,
              ...response.items
            ];

          }


          // ---------------------------------------------
          // RESUMEN
          // ---------------------------------------------

          this.summary =
            response.summary;


          this.total =
            response.total;


          // ---------------------------------------------
          // OFFSET
          // ---------------------------------------------

          this.offset =
            this.bookings.length;


          this.loading =
            false;


          this.loadingMore =
            false;


          // ---------------------------------------------
          // CALENDARIO:
          // CARGAR TODAS LAS RESERVAS DE LA SEMANA
          // ---------------------------------------------

          if (
            this.barberId !==
              null
            &&
            this.hasMore
          ) {

            this.loadBookings(
              false
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
            'Error cargando reservas:',
            error
          );


          if (
            reset
          ) {

            this.bookings =
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
              'No tienes permisos para consultar las reservas.';

          }

          else if (
            error.status ===
            422
          ) {

            this.error =
              (
                typeof error?.error?.detail ===
                  'string'
                  ? error.error.detail
                  : 'Los filtros enviados no son válidos.'
              );

          }

          else {

            this.error =
              'No fue posible cargar las reservas.';

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

    // ---------------------------------------------------
    // EN CALENDARIO LA CARGA ES AUTOMÁTICA
    // ---------------------------------------------------

    if (
      this.barberId !==
      null
    ) {

      return;

    }


    this.loadBookings(
      false
    );

  }


  // =====================================================
  // BUSCAR
  // =====================================================

  onSearch(
    event:
      Event
  ): void {

    const target =
      event.target;


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


    if (
      this.searchTimeout !==
      null
    ) {

      clearTimeout(
        this.searchTimeout
      );

    }


    this.searchTimeout =
      setTimeout(
        () => {

          this.searchTimeout =
            null;


          this.closeBooking();


          this.loadBookings(
            true
          );

        },
        350
      );

  }


  // =====================================================
  // FILTRO POR ESTADO
  // =====================================================

  setStatusFilter(
    status:
      AdminBookingStatus | 'all'
  ): void {

    if (
      this.statusFilter ===
      status
    ) {

      return;

    }


    this.statusFilter =
      status;


    this.closeBooking();


    this.loadBookings(
      true
    );

  }


  // =====================================================
  // FECHA DESDE
  // =====================================================

  onDateFromChange(
    event:
      Event
  ): void {

    const target =
      event.target;


    if (
      !(
        target instanceof
        HTMLInputElement
      )
    ) {

      return;

    }


    // ---------------------------------------------------
    // EN CALENDARIO:
    // LA FECHA SELECCIONADA DEFINE LA SEMANA
    // ---------------------------------------------------

    if (
      this.barberId !==
        null
      &&
      target.value
    ) {

      this.setCalendarWeek(
        new Date(
          `${target.value}T12:00:00`
        )
      );


      return;

    }


    this.dateFrom =
      target.value;


    this.closeBooking();


    this.loadBookings(
      true
    );

  }


  // =====================================================
  // FECHA HASTA
  // =====================================================

  onDateToChange(
    event:
      Event
  ): void {

    const target =
      event.target;


    if (
      !(
        target instanceof
        HTMLInputElement
      )
    ) {

      return;

    }


    if (
      this.barberId !==
        null
      &&
      target.value
    ) {

      this.setCalendarWeek(
        new Date(
          `${target.value}T12:00:00`
        )
      );


      return;

    }


    this.dateTo =
      target.value;


    this.closeBooking();


    this.loadBookings(
      true
    );

  }


  // =====================================================
  // LIMPIAR FILTROS
  // =====================================================

  clearFilters(): void {

    this.search =
      '';


    this.statusFilter =
      'all';


    this.barbershopId =
      null;


    this.barberId =
      null;


    this.barbers =
      [];


    this.dateFrom =
      '';


    this.dateTo =
      '';


    this.weekStart =
      this.getMonday(
        new Date()
      );


    this.weeklyAgenda =
      null;


    this.loadingAgenda =
      false;


    this.agendaError =
      '';


    this.closeBooking();


    this.loadBookings(
      true
    );

  }


  // =====================================================
  // ABRIR RESERVA
  // =====================================================

  openBooking(
    booking:
      AdminBookingItem
  ): void {

    this.confirmError =
      '';


    this.confirmSuccess =
      '';


    this.cancelError =
      '';


    this.cancelSuccess =
      '';


    this.completeError =
      '';


    this.completeSuccess =
      '';


    this.selectedBooking =
      booking;

  }


  // =====================================================
  // CERRAR RESERVA
  // =====================================================

  closeBooking(): void {

    this.selectedBooking =
      null;


    this.confirmError =
      '';


    this.confirmSuccess =
      '';


    this.cancelError =
      '';


    this.cancelSuccess =
      '';


    this.completeError =
      '';


    this.completeSuccess =
      '';

  }


  // =====================================================
  // PUEDE CONFIRMAR
  // =====================================================

  canConfirmBooking(
    booking:
      AdminBookingItem
      |
      null
  ): boolean {

    if (
      !booking
    ) {

      return false;

    }


    return (
      booking.status_code ===
      'PENDING'
    );

  }


  // =====================================================
  // PUEDE CANCELAR
  // =====================================================

  canCancelBooking(
    booking:
      AdminBookingItem
      |
      null
  ): boolean {

    if (
      !booking
    ) {

      return false;

    }


    return (
      booking.status_code ===
        'PENDING'
      ||
      booking.status_code ===
        'CONFIRMED'
    );

  }


  // =====================================================
  // PUEDE COMPLETAR
  // =====================================================

  canCompleteBooking(
    booking:
      AdminBookingItem
      |
      null
  ): boolean {

    if (
      !booking
    ) {

      return false;

    }


    return (
      booking.status_code ===
        'CONFIRMED'
      ||
      booking.status_code ===
        'IN_PROGRESS'
    );

  }


  // =====================================================
  // CONFIRMANDO
  // =====================================================

  isConfirmingBooking(
    bookingId:
      number
  ): boolean {

    return (
      this.confirmingBookingId ===
      bookingId
    );

  }


  // =====================================================
  // CANCELANDO
  // =====================================================

  isCancellingBooking(
    bookingId:
      number
  ): boolean {

    return (
      this.cancellingBookingId ===
      bookingId
    );

  }


  // =====================================================
  // COMPLETANDO
  // =====================================================

  isCompletingBooking(
    bookingId:
      number
  ): boolean {

    return (
      this.completingBookingId ===
      bookingId
    );

  }


  // =====================================================
  // CONFIRMAR RESERVA
  // =====================================================

  confirmBooking(
    booking:
      AdminBookingItem
  ): void {

    if (
      !this.canConfirmBooking(
        booking
      )
      ||
      this.confirmingBookingId !==
        null
      ||
      this.cancellingBookingId !==
        null
      ||
      this.completingBookingId !==
        null
    ) {

      return;

    }


    const confirmed =
      window.confirm(
        `¿Confirmas la reserva #${booking.id}?`
      );


    if (
      !confirmed
    ) {

      return;

    }


    this.confirmError =
      '';


    this.confirmSuccess =
      '';


    this.cancelError =
      '';


    this.completeError =
      '';


    this.confirmingBookingId =
      booking.id;


    this.service
      .confirmBooking(
        booking.id
      )
      .subscribe({

        next: (
          response:
            AdminBookingConfirmResponse
        ) => {

          const updatedBooking:
            AdminBookingItem = {

              ...booking,

              status_id:
                response.status_id,

              status_code:
                response.status_code,

              status_name:
                response.status_name,

              updated_at:
                new Date()
                  .toISOString()

            };


          this.updateLocalBooking(
            updatedBooking
          );


          this.confirmSuccess =
            response.message;


          this.confirmingBookingId =
            null;


          this.loadBookings(
            true
          );


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error confirmando reserva:',
            error
          );


          this.confirmingBookingId =
            null;


          if (
            error.status ===
            401
          ) {

            this.confirmError =
              'Tu sesión ha expirado.';

          }

          else if (
            error.status ===
            403
          ) {

            this.confirmError =
              'No tienes permisos para confirmar esta reserva.';

          }

          else if (
            error.status ===
            404
          ) {

            this.confirmError =
              'La reserva ya no existe.';

          }

          else if (
            error.status ===
            409
          ) {

            this.confirmError =
              this.getErrorDetail(
                error,
                'La reserva ya no puede ser confirmada.'
              );

          }

          else {

            this.confirmError =
              this.getErrorDetail(
                error,
                'No fue posible confirmar la reserva.'
              );

          }


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // CANCELAR RESERVA
  // =====================================================

  cancelBooking(
    booking:
      AdminBookingItem
  ): void {

    if (
      !this.canCancelBooking(
        booking
      )
      ||
      this.cancellingBookingId !==
        null
      ||
      this.confirmingBookingId !==
        null
      ||
      this.completingBookingId !==
        null
    ) {

      return;

    }


    const confirmed =
      window.confirm(
        `¿Confirmas la cancelación de la reserva #${booking.id}?`
      );


    if (
      !confirmed
    ) {

      return;

    }


    this.cancelError =
      '';


    this.cancelSuccess =
      '';


    this.confirmError =
      '';


    this.completeError =
      '';


    this.cancellingBookingId =
      booking.id;


    this.service
      .cancelBooking(
        booking.id
      )
      .subscribe({

        next: (
          response:
            AdminBookingCancelResponse
        ) => {

          const updatedBooking:
            AdminBookingItem = {

              ...booking,

              status_id:
                response.status_id,

              status_code:
                response.status_code,

              status_name:
                response.status_name,

              updated_at:
                new Date()
                  .toISOString()

            };


          this.updateLocalBooking(
            updatedBooking
          );


          this.cancelSuccess =
            response.message;


          this.cancellingBookingId =
            null;


          this.loadBookings(
            true
          );


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error cancelando reserva:',
            error
          );


          this.cancellingBookingId =
            null;


          if (
            error.status ===
            401
          ) {

            this.cancelError =
              'Tu sesión ha expirado.';

          }

          else if (
            error.status ===
            403
          ) {

            this.cancelError =
              'No tienes permisos para cancelar esta reserva.';

          }

          else if (
            error.status ===
            404
          ) {

            this.cancelError =
              'La reserva ya no existe.';

          }

          else if (
            error.status ===
            409
          ) {

            this.cancelError =
              this.getErrorDetail(
                error,
                'La reserva ya no puede ser cancelada.'
              );

          }

          else {

            this.cancelError =
              this.getErrorDetail(
                error,
                'No fue posible cancelar la reserva.'
              );

          }


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // COMPLETAR RESERVA
  // =====================================================

  completeBooking(
    booking:
      AdminBookingItem
  ): void {

    if (
      !this.canCompleteBooking(
        booking
      )
      ||
      this.completingBookingId !==
        null
      ||
      this.confirmingBookingId !==
        null
      ||
      this.cancellingBookingId !==
        null
    ) {

      return;

    }


    const confirmed =
      window.confirm(
        `¿Confirmas que el servicio de la reserva #${booking.id} fue realizado y finalizado?`
      );


    if (
      !confirmed
    ) {

      return;

    }


    this.completeError =
      '';


    this.completeSuccess =
      '';


    this.confirmError =
      '';


    this.cancelError =
      '';


    this.completingBookingId =
      booking.id;


    this.service
      .completeBooking(
        booking.id
      )
      .subscribe({

        next: (
          response:
            AdminBookingCompleteResponse
        ) => {

          const updatedBooking:
            AdminBookingItem = {

              ...booking,

              status_id:
                response.status_id,

              status_code:
                response.status_code,

              status_name:
                response.status_name,

              updated_at:
                new Date()
                  .toISOString()

            };


          this.updateLocalBooking(
            updatedBooking
          );


          this.completeSuccess =
            response.message;


          this.completingBookingId =
            null;


          this.loadBookings(
            true
          );


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error completando reserva:',
            error
          );


          this.completingBookingId =
            null;


          if (
            error.status ===
            401
          ) {

            this.completeError =
              'Tu sesión ha expirado.';

          }

          else if (
            error.status ===
            403
          ) {

            this.completeError =
              'No tienes permisos para completar esta reserva.';

          }

          else if (
            error.status ===
            404
          ) {

            this.completeError =
              'La reserva ya no existe.';

          }

          else if (
            error.status ===
            409
          ) {

            this.completeError =
              this.getErrorDetail(
                error,
                'La reserva ya no puede marcarse como completada.'
              );

          }

          else {

            this.completeError =
              this.getErrorDetail(
                error,
                'No fue posible completar la reserva.'
              );

          }


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // ACTUALIZAR RESERVA LOCAL
  // =====================================================

  private updateLocalBooking(
    updatedBooking:
      AdminBookingItem
  ): void {

    this.bookings =
      this.bookings.map(
        booking =>
          booking.id ===
            updatedBooking.id
            ? updatedBooking
            : booking
      );


    if (
      this.selectedBooking?.id ===
      updatedBooking.id
    ) {

      this.selectedBooking =
        updatedBooking;

    }

  }


  // =====================================================
  // DETALLE ERROR API
  // =====================================================

  private getErrorDetail(
    error:
      HttpErrorResponse,

    fallback:
      string
  ): string {

    return (
      typeof error?.error?.detail ===
        'string'
        ? error.error.detail
        : fallback
    );

  }


  // =====================================================
  // ETIQUETA ESTADO
  // =====================================================

  statusLabel(
    status:
      AdminBookingStatus
  ): string {

    switch (
      status
    ) {

      case 'PENDING':

        return 'Pendiente';


      case 'CONFIRMED':

        return 'Confirmada';


      case 'IN_PROGRESS':

        return 'En progreso';


      case 'COMPLETED':

        return 'Completada';


      case 'CANCELLED_BY_CUSTOMER':

        return 'Cancelada por cliente';


      case 'CANCELLED_BY_BARBER':

        return 'Cancelada por barbero';


      case 'CANCELLED_BY_ADMIN':

        return 'Cancelada por administrador';


      case 'REJECTED':

        return 'Rechazada';


      case 'NO_SHOW':

        return 'No asistió';


      default:

        return status;

    }

  }


  // =====================================================
  // CLASE ESTADO
  // =====================================================

  statusClass(
    status:
      AdminBookingStatus
  ): string {

    switch (
      status
    ) {

      case 'PENDING':

        return 'pending';


      case 'CONFIRMED':

        return 'confirmed';


      case 'IN_PROGRESS':

        return 'in-progress';


      case 'COMPLETED':

        return 'completed';


      case 'CANCELLED_BY_CUSTOMER':

      case 'CANCELLED_BY_BARBER':

      case 'CANCELLED_BY_ADMIN':

        return 'cancelled';


      case 'REJECTED':

        return 'rejected';


      case 'NO_SHOW':

        return 'no-show';


      default:

        return 'pending';

    }

  }


  // =====================================================
  // INICIALES CLIENTE
  // =====================================================

  getClientInitials(
    booking:
      AdminBookingItem
  ): string {

    const first =
      (
        booking.client_first_name
        ??
        ''
      )
        .trim();


    const last =
      (
        booking.client_last_name
        ??
        ''
      )
        .trim();


    const initials =
      (
        first.charAt(
          0
        )
        +
        last.charAt(
          0
        )
      )
        .trim();


    if (
      initials
    ) {

      return initials
        .toUpperCase();

    }


    if (
      booking.client_email
    ) {

      return booking.client_email
        .charAt(
          0
        )
        .toUpperCase();

    }


    return 'C';

  }


  // =====================================================
  // MONEDA
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
  // FECHA
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


    const currentDate =
      new Date(
        value
      );


    if (
      Number.isNaN(
        currentDate.getTime()
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
        currentDate
      );

  }


  // =====================================================
  // HORA
  // =====================================================

  formatTime(
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


    const currentDate =
      new Date(
        value
      );


    if (
      Number.isNaN(
        currentDate.getTime()
      )
    ) {

      return '—';

    }


    return new Intl
      .DateTimeFormat(
        'es-CO',
        {
          hour:
            '2-digit',

          minute:
            '2-digit',

          hour12:
            true
        }
      )
      .format(
        currentDate
      );

  }


  // =====================================================
  // DURACIÓN
  // =====================================================

  getDurationMinutes(
    booking:
      AdminBookingItem
  ): number {

    const start =
      new Date(
        booking.start_at
      );


    const end =
      new Date(
        booking.end_at
      );


    if (
      Number.isNaN(
        start.getTime()
      )
      ||
      Number.isNaN(
        end.getTime()
      )
    ) {

      return (
        booking.service_duration_minutes
        ||
        0
      );

    }


    const difference =
      end.getTime()
      -
      start.getTime();


    const minutes =
      Math.round(
        difference
        /
        60000
      );


    return (
      minutes > 0
        ? minutes
        : booking.service_duration_minutes
    );

  }

}
