import {
  ChangeDetectorRef,
  Component,
  OnInit,
  inject
} from '@angular/core';

import {
  DatePipe,
  DecimalPipe
} from '@angular/common';

import {
  BarberAgendaService
} from '../../services/barber-agenda';

import {
  BarberAgendaBooking,
  BarberAgendaProfile,
  BarberAgendaResponse
} from '../../models/barber-agenda';


@Component({
  selector:
    'app-barber-dashboard',

  imports: [
    DatePipe,
    DecimalPipe
  ],

  templateUrl:
    './barber-dashboard.html',

  styleUrl:
    './barber-dashboard.scss'
})
export class BarberDashboard
  implements OnInit {


  // =====================================================
  // DEPENDENCIAS
  // =====================================================

  private readonly agendaService =
    inject(
      BarberAgendaService
    );


  private readonly cdr =
    inject(
      ChangeDetectorRef
    );


  // =====================================================
  // ESTADO
  // =====================================================

  loading =
    true;


  errorMessage =
    '';


  barber:
    BarberAgendaProfile | null =
      null;


  bookings:
    BarberAgendaBooking[] =
      [];


  selectedDate =
    this.getToday();


  dateFrom =
    this.selectedDate;


  dateTo =
    this.selectedDate;


  // =====================================================
  // INICIO
  // =====================================================

  ngOnInit(): void {

    this.loadToday();

  }


  // =====================================================
  // CARGAR HOY
  // =====================================================

  loadToday(): void {

    const today =
      this.getToday();


    this.selectedDate =
      today;


    this.dateFrom =
      today;


    this.dateTo =
      today;


    this.loadAgenda();

  }


  // =====================================================
  // CARGAR SEMANA
  // =====================================================

  loadWeek(): void {

    const today =
      new Date();


    const monday =
      this.getMonday(
        today
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


    this.dateFrom =
      this.formatDate(
        monday
      );


    this.dateTo =
      this.formatDate(
        sunday
      );


    this.loadAgenda();

  }


  // =====================================================
  // SELECCIONAR FECHA
  // =====================================================

  selectDate(
    event: Event
  ): void {

    const input =
      event.target as HTMLInputElement;


    if (
      !input.value
    ) {

      return;

    }


    this.selectedDate =
      input.value;


    this.dateFrom =
      input.value;


    this.dateTo =
      input.value;


    this.loadAgenda();

  }


  // =====================================================
  // CONSULTAR AGENDA
  // =====================================================

  loadAgenda(): void {

    this.loading =
      true;


    this.errorMessage =
      '';


    this.agendaService
      .getMyAgenda(
        this.dateFrom,
        this.dateTo
      )
      .subscribe({

        next: (
          response:
            BarberAgendaResponse
        ) => {

          this.barber =
            response.barber;


          this.bookings =
            response.items;


          this.loading =
            false;


          this.cdr
            .detectChanges();

        },


        error: (
          error
        ) => {

          console.error(
            'Error cargando agenda del barbero:',
            error
          );


          this.bookings =
            [];


          this.loading =
            false;


          this.errorMessage =
            this.getErrorMessage(
              error
            );


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // PRÓXIMA CITA
  // =====================================================

  get nextBooking():
    BarberAgendaBooking | null {

    const now =
      new Date();


    const candidates =
      this.bookings
        .filter(
          booking => {

            const start =
              new Date(
                booking.start_at
              );


            const status =
              booking.status_code
                .toUpperCase();


            return (
              start >= now
              &&
              status !==
                'CANCELLED_BY_CUSTOMER'
              &&
              status !==
                'CANCELLED_BY_BARBER'
              &&
              status !==
                'REJECTED'
              &&
              status !==
                'COMPLETED'
              &&
              status !==
                'NO_SHOW'
            );

          }
        )
        .sort(
          (
            a,
            b
          ) =>
            new Date(
              a.start_at
            ).getTime()
            -
            new Date(
              b.start_at
            ).getTime()
        );


    return (
      candidates[0]
      ??
      null
    );

  }


  // =====================================================
  // CITAS DE HOY
  // =====================================================

  get todayBookings():
    BarberAgendaBooking[] {

    const today =
      this.getToday();


    return this.bookings
      .filter(
        booking =>
          booking.start_at
            .slice(
              0,
              10
            )
          ===
          today
      );

  }


  // =====================================================
  // TOTAL PENDIENTES
  // =====================================================

  get pendingCount():
    number {

    return this.bookings
      .filter(
        booking => {

          const status =
            booking.status_code
              .toUpperCase();


          return (
            status ===
              'PENDING'
            ||
            status ===
              'CONFIRMED'
          );

        }
      )
      .length;

  }


  // =====================================================
  // TOTAL COMPLETADAS
  // =====================================================

  get completedCount():
    number {

    return this.bookings
      .filter(
        booking =>
          booking.status_code
            .toUpperCase()
          ===
          'COMPLETED'
      )
      .length;

  }


  // =====================================================
  // CLASE DE ESTADO
  // =====================================================

  getStatusClass(
    statusCode: string
  ): string {

    switch (
      statusCode
        .toUpperCase()
    ) {

      case 'CONFIRMED':

        return 'confirmed';


      case 'PENDING':

        return 'pending';


      case 'IN_PROGRESS':

        return 'in-progress';


      case 'COMPLETED':

        return 'completed';


      case 'NO_SHOW':

        return 'no-show';


      case 'REJECTED':

      case 'CANCELLED_BY_CUSTOMER':

      case 'CANCELLED_BY_BARBER':

        return 'cancelled';


      default:

        return 'default';

    }

  }


  // =====================================================
  // FORMATEAR PRECIO
  // =====================================================

  formatPrice(
    value: number
  ): string {

    return new Intl.NumberFormat(
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
        value
      );

  }


  // =====================================================
  // FECHA ACTUAL
  // =====================================================

  private getToday():
    string {

    return this.formatDate(
      new Date()
    );

  }


  // =====================================================
  // OBTENER LUNES
  // =====================================================

  private getMonday(
    value: Date
  ): Date {

    const date =
      new Date(
        value
      );


    const day =
      date.getDay();


    const difference =
      date.getDate()
      -
      day
      +
      (
        day === 0
          ?
          -6
          :
          1
      );


    date.setDate(
      difference
    );


    return date;

  }


  // =====================================================
  // YYYY-MM-DD
  // =====================================================

  private formatDate(
    date: Date
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
  // ERROR
  // =====================================================

  private getErrorMessage(
    error: any
  ): string {

    const detail =
      error?.error?.detail;


    if (
      typeof detail ===
      'string'
    ) {

      return detail;

    }


    if (
      error?.status === 403
    ) {

      return (
        'No tienes autorización para consultar esta agenda.'
      );

    }


    if (
      error?.status === 401
    ) {

      return (
        'Tu sesión ha vencido. Inicia sesión nuevamente.'
      );

    }


    return (
      'No fue posible cargar tu agenda.'
    );

  }

}
