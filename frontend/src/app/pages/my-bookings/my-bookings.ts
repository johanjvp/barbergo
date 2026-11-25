import { Icon } from '../../components/icon/icon';
import {
  ChangeDetectorRef,
  Component,
  OnInit,
  inject
} from '@angular/core';

import {
  Router,
  RouterLink
} from '@angular/router';

import {
  catchError,
  forkJoin,
  map,
  of
} from 'rxjs';

import {
  Navbar
} from '../../components/navbar/navbar';

import {
  Footer
} from '../../components/footer/footer';

import {
  AuthService
} from '../../services/auth';

import {
  BookingService
} from '../../services/booking';

import {
  BarbershopService
} from '../../services/barbershop';

import {
  ServiceService
} from '../../services/service';

import {
  BarberService
} from '../../services/barber';

import {
  BookingResponse
} from '../../models/booking';


interface BookingViewItem
  extends BookingResponse {

  barbershop_name:
    string;

  service_name:
    string;

  barber_name:
    string;

  cancellation_hours_before:
    number;

}


@Component({
  selector: 'app-my-bookings',

  imports: [
    Icon,
    Navbar,
    Footer,
    RouterLink
  ],

  templateUrl:
    './my-bookings.html',

  styleUrl:
    './my-bookings.scss'
})
export class MyBookings
  implements OnInit {


  // =====================================================
  // DEPENDENCIAS
  // =====================================================

  private readonly authService =
    inject(AuthService);


  private readonly bookingService =
    inject(BookingService);


  private readonly barbershopService =
    inject(BarbershopService);


  private readonly serviceService =
    inject(ServiceService);


  private readonly barberService =
    inject(BarberService);


  private readonly router =
    inject(Router);


  private readonly cdr =
    inject(ChangeDetectorRef);


  // =====================================================
  // RESERVAS
  // =====================================================

  bookings:
    BookingViewItem[] = [];


  loading =
    true;


  error =
    '';


  // =====================================================
  // CANCELACIÓN
  // =====================================================

  selectedBookingForCancellation:
    BookingViewItem | null = null;


  showCancellationModal =
    false;


  cancellationLoading =
    false;


  cancellationError =
    '';


  cancellationSuccess =
    '';


  // =====================================================
  // INICIO
  // =====================================================

  ngOnInit(): void {

    if (
      !this.authService
        .isAuthenticated()
    ) {

      this.router.navigate(
        ['/login'],
        {

          queryParams: {

            returnUrl:
              '/mis-reservas'

          }

        }
      );


      return;

    }


    this.loadBookings();

  }


  // =====================================================
  // CARGAR RESERVAS
  // =====================================================

  private loadBookings(): void {

    this.loading =
      true;


    this.error =
      '';


    this.bookingService
      .getMyBookings()
      .subscribe({

        next: (bookings) => {

          if (
            bookings.length === 0
          ) {

            this.bookings =
              [];


            this.loading =
              false;


            this.cdr
              .detectChanges();


            return;

          }


          const requests =
            bookings.map(
              booking => {

                return forkJoin({

                  barbershop:
                    this.barbershopService
                      .getById(
                        booking.barbershop_id
                      ),

                  services:
                    this.serviceService
                      .getByBarbershop(
                        booking.barbershop_id
                      ),

                  barbers:
                    this.barberService
                      .getByBarbershop(
                        booking.barbershop_id
                      )

                })
                  .pipe(

                    map(
                      response => {

                        const service =
                          response.services
                            .find(
                              item =>
                                item.id ===
                                booking.service_id
                            );


                        const barber =
                          response.barbers
                            .find(
                              item =>
                                item.id ===
                                booking.barber_id
                            );


                        const barberName =
                          barber
                            ? `${barber.first_name} ${barber.last_name}`
                            : 'Profesional no disponible';


                        const cancellationHours =
                          Number(
                            response
                              .barbershop
                              .cancellation_hours_before
                          );


                        return {

                          ...booking,


                          barbershop_name:
                            response
                              .barbershop
                              .name,


                          service_name:
                            service?.name
                            ||
                            'Servicio no disponible',


                          barber_name:
                            barberName,


                          cancellation_hours_before:
                            Number.isFinite(
                              cancellationHours
                            )
                              ? cancellationHours
                              : 2

                        } as BookingViewItem;

                      }
                    ),


                    catchError(
                      error => {

                        console.error(
                          'Error cargando información de reserva:',
                          booking.id,
                          error
                        );


                        return of({

                          ...booking,


                          barbershop_name:
                            `Barbería #${booking.barbershop_id}`,


                          service_name:
                            `Servicio #${booking.service_id}`,


                          barber_name:
                            `Profesional #${booking.barber_id}`,


                          cancellation_hours_before:
                            2

                        } as BookingViewItem);

                      }
                    )

                  );

              }
            );


          forkJoin(
            requests
          )
            .subscribe({

              next: (
                enrichedBookings
              ) => {

                this.bookings =
                  enrichedBookings
                    .sort(
                      (
                        a,
                        b
                      ) => {

                        return (
                          new Date(
                            b.start_at
                          )
                            .getTime()
                          -
                          new Date(
                            a.start_at
                          )
                            .getTime()
                        );

                      }
                    );


                this.loading =
                  false;


                this.cdr
                  .detectChanges();

              },


              error: (error) => {

                console.error(
                  'Error preparando reservas:',
                  error
                );


                this.error =
                  'No pudimos preparar tus reservas.';


                this.loading =
                  false;


                this.cdr
                  .detectChanges();

              }

            });

        },


        error: (error) => {

          console.error(
            'Error cargando reservas:',
            error
          );


          if (
            error.status === 401
          ) {

            this.authService
              .logout();


            this.router.navigate(
              ['/login'],
              {

                queryParams: {

                  returnUrl:
                    '/mis-reservas'

                }

              }
            );


            return;

          }


          this.error =
            error?.error?.detail
            ||
            'No pudimos cargar tus reservas.';


          this.loading =
            false;


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // PRÓXIMAS RESERVAS
  // =====================================================

  get upcomingBookings():
    BookingViewItem[] {

    const now =
      Date.now();


    return this.bookings
      .filter(
        booking => {

          const bookingTime =
            new Date(
              booking.start_at
            )
              .getTime();


          return (
            bookingTime >= now
            &&
            this.isActiveStatus(
              booking.status_code
            )
          );

        }
      )
      .sort(
        (
          a,
          b
        ) => {

          return (
            new Date(
              a.start_at
            )
              .getTime()
            -
            new Date(
              b.start_at
            )
              .getTime()
          );

        }
      );

  }


  // =====================================================
  // HISTORIAL
  // =====================================================

  get historyBookings():
    BookingViewItem[] {

    const upcomingIds =
      new Set(
        this.upcomingBookings
          .map(
            booking =>
              booking.id
          )
      );


    return this.bookings
      .filter(
        booking =>
          !upcomingIds
            .has(
              booking.id
            )
      );

  }


  // =====================================================
  // ESTADOS ACTIVOS
  // =====================================================

  private isActiveStatus(
    status:
      string
  ): boolean {

    return [
      'PENDING',
      'CONFIRMED',
      'IN_PROGRESS'
    ]
      .includes(
        status
      );

  }


  // =====================================================
  // TEXTO DEL ESTADO
  // =====================================================

  getStatusLabel(
    status:
      string
  ): string {

    switch (
      status
    ) {

      case 'PENDING':

        return 'Pendiente';


      case 'CONFIRMED':

        return 'Confirmada';


      case 'REJECTED':

        return 'Rechazada';


      case 'CANCELLED_BY_CUSTOMER':

        return 'Cancelada por ti';


      case 'CANCELLED_BY_BARBER':

        return 'Cancelada por la barbería';


      case 'NO_SHOW':

        return 'No asististe';


      case 'IN_PROGRESS':

        return 'En curso';


      case 'COMPLETED':

        return 'Completada';


      default:

        return status;

    }

  }


  // =====================================================
  // CLASE CSS DEL ESTADO
  // =====================================================

  getStatusClass(
    status:
      string
  ): string {

    switch (
      status
    ) {

      case 'CONFIRMED':

        return 'confirmed';


      case 'PENDING':

        return 'pending';


      case 'IN_PROGRESS':

        return 'progress';


      case 'COMPLETED':

        return 'completed';


      case 'REJECTED':

      case 'CANCELLED_BY_CUSTOMER':

      case 'CANCELLED_BY_BARBER':

      case 'NO_SHOW':

        return 'cancelled';


      default:

        return 'neutral';

    }

  }


  // =====================================================
  // ¿PUEDE CANCELAR?
  // =====================================================

  canCancelBooking(
    booking:
      BookingViewItem
  ): boolean {

    /*
     * Solamente PENDING y CONFIRMED.
     */
    if (
      ![
        'PENDING',
        'CONFIRMED'
      ]
        .includes(
          booking.status_code
        )
    ) {

      return false;

    }


    const bookingStart =
      new Date(
        booking.start_at
      )
        .getTime();


    const now =
      Date.now();


    const cancellationLimit =
      booking
        .cancellation_hours_before
      *
      60
      *
      60
      *
      1000;


    const remainingTime =
      bookingStart
      -
      now;


    return (
      remainingTime
      >=
      cancellationLimit
    );

  }


  // =====================================================
  // TEXTO POLÍTICA
  // =====================================================

  getCancellationText(
    booking:
      BookingViewItem
  ): string {

    const hours =
      booking
        .cancellation_hours_before;


    if (
      hours === 1
    ) {

      return (
        'Puedes cancelar hasta 1 hora antes de la cita.'
      );

    }


    return (
      `Puedes cancelar hasta ${hours} horas antes de la cita.`
    );

  }


  // =====================================================
  // TEXTO BLOQUEADO
  // =====================================================

  getCancellationBlockedText(
    booking:
      BookingViewItem
  ): string {

    const hours =
      booking
        .cancellation_hours_before;


    if (
      hours === 1
    ) {

      return (
        'Esta reserva ya está dentro del período de 1 hora previo a la cita y no puede cancelarse desde BarberGo.'
      );

    }


    return (
      `Esta reserva ya está dentro del período de ${hours} horas previo a la cita y no puede cancelarse desde BarberGo.`
    );

  }


  // =====================================================
  // ABRIR MODAL DE CANCELACIÓN
  // =====================================================

  requestCancellation(
    booking:
      BookingViewItem
  ): void {

    if (
      !this.canCancelBooking(
        booking
      )
    ) {

      return;

    }


    this.selectedBookingForCancellation =
      booking;


    this.cancellationError =
      '';


    this.cancellationSuccess =
      '';


    this.showCancellationModal =
      true;


    this.cdr
      .detectChanges();

  }


  // =====================================================
  // CERRAR MODAL
  // =====================================================

  closeCancellationModal(): void {

    /*
     * No permitimos cerrar mientras
     * FastAPI está procesando.
     */
    if (
      this.cancellationLoading
    ) {

      return;

    }


    this.showCancellationModal =
      false;


    this.selectedBookingForCancellation =
      null;


    this.cancellationError =
      '';


    this.cancellationSuccess =
      '';


    this.cdr
      .detectChanges();

  }


  // =====================================================
  // CONFIRMAR CANCELACIÓN
  // =====================================================

  confirmCancellation(): void {

    const booking =
      this.selectedBookingForCancellation;


    if (
      !booking
    ) {

      return;

    }


    /*
     * Volvemos a comprobar la regla
     * justo antes de llamar al backend.
     */
    if (
      !this.canCancelBooking(
        booking
      )
    ) {

      this.cancellationError =
        this.getCancellationBlockedText(
          booking
        );


      this.cdr
        .detectChanges();


      return;

    }


    this.cancellationLoading =
      true;


    this.cancellationError =
      '';


    this.cancellationSuccess =
      '';


    this.bookingService
      .cancel(
        booking.id
      )
      .subscribe({

        // ===============================================
        // CANCELACIÓN EXITOSA
        // ===============================================

        next: (
          updatedBooking
        ) => {

          this.cancellationLoading =
            false;


          /*
           * Conservamos los nombres que
           * agregamos solamente en frontend,
           * pero sustituimos los datos que
           * vienen actualizados del backend.
           */
          this.bookings =
            this.bookings
              .map(
                currentBooking => {

                  if (
                    currentBooking.id
                    !==
                    updatedBooking.id
                  ) {

                    return currentBooking;

                  }


                  return {

                    ...currentBooking,

                    ...updatedBooking

                  };

                }
              );


          this.cancellationSuccess =
            'La reserva fue cancelada correctamente.';


          /*
           * Mantenemos el modal abierto
           * para mostrar la confirmación.
           */
          this.cdr
            .detectChanges();

        },


        // ===============================================
        // ERROR
        // ===============================================

        error: (error) => {

          console.error(
            'Error cancelando reserva:',
            error
          );


          this.cancellationLoading =
            false;


          /*
           * Sesión vencida.
           */
          if (
            error.status === 401
          ) {

            this.authService
              .logout();


            this.router.navigate(
              ['/login'],
              {

                queryParams: {

                  returnUrl:
                    '/mis-reservas'

                }

              }
            );


            return;

          }


          this.cancellationError =
            error?.error?.detail
            ||
            'No fue posible cancelar la reserva.';


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // FECHA
  // =====================================================

  formatDate(
    value:
      string
  ): string {

    const date =
      new Date(
        value
      );


    return new Intl.DateTimeFormat(
      'es-CO',
      {

        weekday:
          'long',

        day:
          'numeric',

        month:
          'long',

        year:
          'numeric'

      }
    )
      .format(
        date
      );

  }


  // =====================================================
  // HORA
  // =====================================================

  formatTime(
    value:
      string
  ): string {

    const date =
      new Date(
        value
      );


    return new Intl.DateTimeFormat(
      'es-CO',
      {

        hour:
          'numeric',

        minute:
          '2-digit',

        hour12:
          true

      }
    )
      .format(
        date
      );

  }


  // =====================================================
  // PRECIO
  // =====================================================

  getPrice(
    price:
      number | string
  ): string {

    const numericPrice =
      Number(
        price
      );


    if (
      !Number.isFinite(
        numericPrice
      )
    ) {

      return (
        'Consultar'
      );

    }


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
        numericPrice
      );

  }

}
