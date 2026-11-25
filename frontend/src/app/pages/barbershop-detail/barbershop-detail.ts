import { Confetti } from '../../components/confetti/confetti';
import { Icon } from '../../components/icon/icon';
import {
  ChangeDetectorRef,
  Component,
  OnInit,
  inject
} from '@angular/core';

import {
  ActivatedRoute,
  Router,
  RouterLink
} from '@angular/router';

import {
  forkJoin
} from 'rxjs';

import {
  Navbar
} from '../../components/navbar/navbar';

import {
  Footer
} from '../../components/footer/footer';

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
  AvailabilityService
} from '../../services/availability';

import {
  AuthService
} from '../../services/auth';

import {
  BookingService
} from '../../services/booking';

import {
  BarbershopDetail as BarbershopDetailModel
} from '../../models/barbershop';

import {
  ServiceItem
} from '../../models/service';

import {
  BarberItem
} from '../../models/barber';

import {
  AvailabilitySlot
} from '../../models/availability';

import {
  PendingBooking
} from '../../models/booking';


@Component({
  selector: 'app-barbershop-detail',

  imports: [
    Confetti,
    Icon,
    Navbar,
    Footer,
    RouterLink
  ],

  templateUrl:
    './barbershop-detail.html',

  styleUrl:
    './barbershop-detail.scss'
})
export class BarbershopDetail
  implements OnInit {


  // =====================================================
  // DEPENDENCIAS
  // =====================================================

  private readonly route =
    inject(ActivatedRoute);


  private readonly router =
    inject(Router);


  private readonly cdr =
    inject(ChangeDetectorRef);


  private readonly barbershopService =
    inject(BarbershopService);


  private readonly serviceService =
    inject(ServiceService);


  private readonly barberService =
    inject(BarberService);


  private readonly availabilityService =
    inject(AvailabilityService);


  private readonly authService =
    inject(AuthService);


  private readonly bookingService =
    inject(BookingService);


  private readonly pendingBookingKey =
    'barbergo_pending_booking';


  // =====================================================
  // DATOS
  // =====================================================

  barbershop:
    BarbershopDetailModel | null = null;


  services:
    ServiceItem[] = [];


  barbers:
    BarberItem[] = [];


  // =====================================================
  // SELECCIONES
  // =====================================================

  selectedServiceId:
    number | null = null;


  selectedBarberId:
    number | null = null;


  selectedDate =
    '';


  selectedSlot:
    AvailabilitySlot | null = null;


  // =====================================================
  // DISPONIBILIDAD
  // =====================================================

  availabilitySlots:
    AvailabilitySlot[] = [];


  loadingAvailability =
    false;


  availabilityError =
    '';


  availabilityAvailable =
    false;


  minDate =
    this.getTodayDate();


  // =====================================================
  // ESTADOS GENERALES
  // =====================================================

  loading =
    true;


  error =
    '';


  // =====================================================
  // ESTADO DE LA RESERVA
  // =====================================================

  bookingLoading =
    false;


  bookingError =
    '';


  bookingSuccess =
    '';


  createdBookingId:
    number | null = null;


  reservationNotice =
    '';


  /*
   * Controla la alerta/modal profesional
   * que aparecerá después de crear
   * correctamente la reserva.
   */
  showBookingSuccessModal =
    false;


  // =====================================================
  // INICIO
  // =====================================================

  ngOnInit(): void {

    const id =
      Number(
        this.route.snapshot
          .paramMap
          .get('id')
      );


    if (
      !Number.isInteger(id)
      ||
      id <= 0
    ) {

      this.error =
        'La barbería solicitada no es válida.';


      this.loading =
        false;


      return;

    }


    this.loadPage(
      id
    );

  }


  // =====================================================
  // CARGAR BARBERÍA, SERVICIOS Y BARBEROS
  // =====================================================

  private loadPage(
    id: number
  ): void {

    this.loading =
      true;


    this.error =
      '';


    forkJoin({

      barbershop:
        this.barbershopService
          .getById(id),

      services:
        this.serviceService
          .getByBarbershop(id),

      barbers:
        this.barberService
          .getByBarbershop(id)

    })
      .subscribe({

        next: (response) => {

          this.barbershop =
            response.barbershop;


          this.services =
            response.services
              .filter(
                service =>
                  service.is_active
              );


          this.barbers =
            response.barbers
              .filter(
                barber =>
                  barber.is_active
              );


          this.loading =
            false;


          /*
           * Si el usuario viene de iniciar sesión
           * o registrarse, intentamos recuperar
           * la reserva que estaba preparando.
           */
          this.restorePendingBooking(
            id
          );


          this.cdr
            .detectChanges();

        },


        error: (error) => {

          console.error(
            'Error cargando detalle de barbería:',
            error
          );


          this.error =
            'No pudimos cargar la información de esta barbería.';


          this.loading =
            false;


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // BARBEROS COMPATIBLES CON EL SERVICIO
  // =====================================================

  get compatibleBarbers():
    BarberItem[] {

    if (
      this.selectedServiceId === null
    ) {

      return [];

    }


    const serviceId =
      this.selectedServiceId;


    return this.barbers
      .filter(
        barber =>
          barber.service_ids
            .includes(
              serviceId
            )
      );

  }


  // =====================================================
  // SELECCIONAR SERVICIO
  // =====================================================

  selectService(
    service: ServiceItem
  ): void {

    this.selectedServiceId =
      service.id;


    /*
     * Si cambia el servicio,
     * reiniciamos todas las selecciones
     * posteriores.
     */
    this.selectedBarberId =
      null;


    this.selectedDate =
      '';


    this.selectedSlot =
      null;


    this.availabilitySlots =
      [];


    this.availabilityAvailable =
      false;


    this.availabilityError =
      '';


    this.reservationNotice =
      '';


    this.resetBookingFeedback();

  }


  // =====================================================
  // VERIFICAR SERVICIO SELECCIONADO
  // =====================================================

  isServiceSelected(
    serviceId: number
  ): boolean {

    return (
      this.selectedServiceId
      ===
      serviceId
    );

  }


  // =====================================================
  // SELECCIONAR BARBERO
  // =====================================================

  selectBarber(
    barber: BarberItem
  ): void {

    this.selectedBarberId =
      barber.id;


    /*
     * Al cambiar de barbero
     * debemos volver a consultar
     * disponibilidad.
     */
    this.selectedDate =
      '';


    this.selectedSlot =
      null;


    this.availabilitySlots =
      [];


    this.availabilityAvailable =
      false;


    this.availabilityError =
      '';


    this.reservationNotice =
      '';


    this.resetBookingFeedback();

  }


  // =====================================================
  // VERIFICAR BARBERO SELECCIONADO
  // =====================================================

  isBarberSelected(
    barberId: number
  ): boolean {

    return (
      this.selectedBarberId
      ===
      barberId
    );

  }


  // =====================================================
  // IR A LA SECCIÓN DE BARBEROS
  // =====================================================

  goToBarbers(): void {

    setTimeout(
      () => {

        document
          .getElementById(
            'barbers-section'
          )
          ?.scrollIntoView({

            behavior:
              'smooth',

            block:
              'start'

          });

      },
      0
    );

  }


  // =====================================================
  // IR A FECHA Y HORA
  // =====================================================

  goToAvailability(): void {

    setTimeout(
      () => {

        document
          .getElementById(
            'availability-section'
          )
          ?.scrollIntoView({

            behavior:
              'smooth',

            block:
              'start'

          });

      },
      0
    );

  }


  // =====================================================
  // CAMBIO DE FECHA
  // =====================================================

  onDateChange(
    event: Event
  ): void {

    const input =
      event.target as HTMLInputElement;


    this.selectedDate =
      input.value;


    this.selectedSlot =
      null;


    this.availabilitySlots =
      [];


    this.availabilityAvailable =
      false;


    this.availabilityError =
      '';


    this.reservationNotice =
      '';


    this.resetBookingFeedback();


    if (
      !this.selectedDate
      ||
      this.selectedBarberId === null
      ||
      this.selectedServiceId === null
    ) {

      return;

    }


    this.loadAvailability();

  }


  // =====================================================
  // CONSULTAR DISPONIBILIDAD
  // =====================================================

  private loadAvailability(
    preferredStartTime:
      string | null = null
  ): void {

    if (
      this.selectedBarberId === null
      ||
      this.selectedServiceId === null
      ||
      !this.selectedDate
    ) {

      return;

    }


    this.loadingAvailability =
      true;


    this.availabilityError =
      '';


    this.availabilitySlots =
      [];


    this.selectedSlot =
      null;


    this.availabilityService
      .getAvailability(
        this.selectedBarberId,
        this.selectedServiceId,
        this.selectedDate
      )
      .subscribe({

        next: (response) => {

          this.availabilityAvailable =
            response.available;


          this.availabilitySlots =
            response.slots;


          this.loadingAvailability =
            false;


          /*
           * Si venimos del Login o Registro
           * buscamos nuevamente la hora guardada.
           *
           * No confiamos directamente en sessionStorage
           * porque otra persona pudo tomar ese horario.
           */
          if (
            preferredStartTime
          ) {

            const restoredSlot =
              response.slots
                .find(
                  slot =>
                    slot.start_time ===
                    preferredStartTime
                );


            if (
              restoredSlot
            ) {

              this.selectedSlot =
                restoredSlot;


              this.reservationNotice =
                'Recuperamos la reserva que estabas preparando.';


              this.cdr
                .detectChanges();


              setTimeout(
                () => {

                  document
                    .getElementById(
                      'review-section'
                    )
                    ?.scrollIntoView({

                      behavior:
                        'smooth',

                      block:
                        'start'

                    });

                },
                100
              );

            }

            else {

              this.selectedSlot =
                null;


              this.reservationNotice =
                'El horario que habías seleccionado ya no está disponible. Elige otro horario.';


              this.cdr
                .detectChanges();


              setTimeout(
                () => {

                  document
                    .getElementById(
                      'availability-section'
                    )
                    ?.scrollIntoView({

                      behavior:
                        'smooth',

                      block:
                        'start'

                    });

                },
                100
              );

            }

          }


          this.cdr
            .detectChanges();

        },


        error: (error) => {

          console.error(
            'Error consultando disponibilidad:',
            error
          );


          this.availabilityError =
            error?.error?.detail
            ||
            'No pudimos consultar la disponibilidad para esta fecha.';


          this.availabilityAvailable =
            false;


          this.availabilitySlots =
            [];


          this.selectedSlot =
            null;


          this.loadingAvailability =
            false;


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // SELECCIONAR HORARIO
  // =====================================================

  selectSlot(
    slot: AvailabilitySlot
  ): void {

    this.selectedSlot =
      slot;


    this.reservationNotice =
      '';


    this.resetBookingFeedback();

  }


  // =====================================================
  // VERIFICAR HORARIO SELECCIONADO
  // =====================================================

  isSlotSelected(
    slot: AvailabilitySlot
  ): boolean {

    return (
      this.selectedSlot
        ?.start_time
      ===
      slot.start_time
    );

  }


  // =====================================================
  // SERVICIO SELECCIONADO
  // =====================================================

  get selectedService():
    ServiceItem | null {

    if (
      this.selectedServiceId === null
    ) {

      return null;

    }


    return (
      this.services
        .find(
          service =>
            service.id ===
            this.selectedServiceId
        )
      ??
      null
    );

  }


  // =====================================================
  // BARBERO SELECCIONADO
  // =====================================================

  get selectedBarber():
    BarberItem | null {

    if (
      this.selectedBarberId === null
    ) {

      return null;

    }


    return (
      this.barbers
        .find(
          barber =>
            barber.id ===
            this.selectedBarberId
        )
      ??
      null
    );

  }


  // =====================================================
  // IR AL RESUMEN DE RESERVA
  // =====================================================

  goToReview(): void {

    setTimeout(
      () => {

        document
          .getElementById(
            'review-section'
          )
          ?.scrollIntoView({

            behavior:
              'smooth',

            block:
              'start'

          });

      },
      0
    );

  }


  // =====================================================
  // CONFIRMAR RESERVA
  // =====================================================

  confirmBooking(): void {

    this.resetBookingFeedback();


    this.reservationNotice =
      '';


    if (
      !this.barbershop
      ||
      this.selectedServiceId === null
      ||
      this.selectedBarberId === null
      ||
      !this.selectedDate
      ||
      !this.selectedSlot
    ) {

      this.bookingError =
        'La información de la reserva está incompleta.';


      return;

    }


    const pendingBooking:
      PendingBooking = {

      barbershop_id:
        this.barbershop.id,

      service_id:
        this.selectedServiceId,

      barber_id:
        this.selectedBarberId,

      date:
        this.selectedDate,

      start_time:
        this.selectedSlot.start_time,

      end_time:
        this.selectedSlot.end_time

    };


    // ===================================================
    // USUARIO NO AUTENTICADO
    // ===================================================

    if (
      !this.authService
        .isAuthenticated()
    ) {

      /*
       * Conservamos temporalmente
       * la selección.
       */
      this.savePendingBooking(
        pendingBooking
      );


      /*
       * Enviamos al Login y guardamos
       * la barbería a la que debe regresar.
       */
      this.router.navigate(
        ['/login'],
        {

          queryParams: {

            returnUrl:
              `/barberias/${this.barbershop.id}`

          }

        }
      );


      return;

    }


    // ===================================================
    // USUARIO AUTENTICADO
    // ===================================================

    this.createBooking(
      pendingBooking
    );

  }


  // =====================================================
  // CREAR RESERVA EN BACKEND
  // =====================================================

  private createBooking(
    pendingBooking:
      PendingBooking
  ): void {

    this.bookingLoading =
      true;


    this.bookingError =
      '';


    this.bookingSuccess =
      '';


    /*
     * FastAPI espera datetime
     * sin zona horaria.
     *
     * Ejemplo:
     * 2026-10-27T14:30:00
     */
    const startAt =
      `${pendingBooking.date}T${pendingBooking.start_time}`;


    this.bookingService
      .create({

        barber_id:
          pendingBooking.barber_id,

        service_id:
          pendingBooking.service_id,

        start_at:
          startAt,

        customer_notes:
          null

      })
      .subscribe({

        // ===============================================
        // RESERVA CREADA
        // ===============================================

        next: (booking) => {

          this.bookingLoading =
            false;


          this.createdBookingId =
            booking.id;


          /*
           * Ya existe una reserva real
           * en MySQL. Eliminamos la copia
           * temporal.
           */
          sessionStorage
            .removeItem(
              this.pendingBookingKey
            );


          if (
            booking.status_code ===
            'PENDING'
          ) {

            this.bookingSuccess =
              'Tu reserva fue registrada correctamente y está pendiente de confirmación por la barbería.';

          }

          else {

            this.bookingSuccess =
              'Tu reserva fue creada correctamente.';

          }


          /*
           * Mostramos el modal profesional
           * de reserva exitosa.
           */
          this.showBookingSuccessModal =
            true;


          this.cdr
            .detectChanges();

        },


        // ===============================================
        // ERROR CREANDO RESERVA
        // ===============================================

        error: (error) => {

          console.error(
            'Error creando reserva:',
            error
          );


          this.bookingLoading =
            false;


          /*
           * Si el token expiró durante
           * el proceso, conservamos la
           * selección y mandamos al Login.
           */
          if (
            error.status === 401
          ) {

            this.savePendingBooking(
              pendingBooking
            );


            this.authService
              .logout();


            this.router.navigate(
              ['/login'],
              {

                queryParams: {

                  returnUrl:
                    `/barberias/${pendingBooking.barbershop_id}`

                }

              }
            );


            return;

          }


          /*
           * Aquí también puede llegar,
           * por ejemplo, un error porque
           * otro usuario tomó el horario
           * antes de confirmar.
           */
          this.bookingError =
            error?.error?.detail
            ||
            'No fue posible crear la reserva. Verifica que el horario continúe disponible.';


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // GUARDAR RESERVA PENDIENTE
  // =====================================================

  private savePendingBooking(
    booking: PendingBooking
  ): void {

    sessionStorage
      .setItem(
        this.pendingBookingKey,
        JSON.stringify(
          booking
        )
      );

  }


  // =====================================================
  // RECUPERAR RESERVA DESPUÉS DEL LOGIN / REGISTRO
  // =====================================================

  private restorePendingBooking(
    barbershopId: number
  ): void {

    const rawBooking =
      sessionStorage
        .getItem(
          this.pendingBookingKey
        );


    if (
      !rawBooking
    ) {

      return;

    }


    try {

      const pendingBooking =
        JSON.parse(
          rawBooking
        ) as PendingBooking;


      /*
       * Solo restauramos si la reserva
       * pertenece a la barbería actual.
       */
      if (
        Number(
          pendingBooking.barbershop_id
        )
        !==
        barbershopId
      ) {

        return;

      }


      const serviceId =
        Number(
          pendingBooking.service_id
        );


      const barberId =
        Number(
          pendingBooking.barber_id
        );


      // ===============================================
      // VALIDAR SERVICIO
      // ===============================================

      const serviceExists =
        this.services
          .some(
            service =>
              service.id ===
              serviceId
          );


      // ===============================================
      // VALIDAR BARBERO
      // ===============================================

      const barber =
        this.barbers
          .find(
            currentBarber =>
              currentBarber.id ===
              barberId
          );


      // ===============================================
      // VALIDAR QUE EL BARBERO SIGA HACIENDO EL SERVICIO
      // ===============================================

      const barberSupportsService =
        !!barber
        &&
        barber.service_ids
          .includes(
            serviceId
          );


      if (
        !serviceExists
        ||
        !barberSupportsService
      ) {

        sessionStorage
          .removeItem(
            this.pendingBookingKey
          );


        this.reservationNotice =
          'No pudimos recuperar la reserva anterior porque el servicio o el profesional ya no están disponibles.';


        return;

      }


      // ===============================================
      // RESTAURAR SELECCIONES
      // ===============================================

      this.selectedServiceId =
        serviceId;


      this.selectedBarberId =
        barberId;


      this.selectedDate =
        pendingBooking.date;


      this.selectedSlot =
        null;


      /*
       * Muy importante:
       *
       * volvemos a consultar al backend.
       *
       * Solo recuperaremos el horario
       * si continúa realmente disponible.
       */
      this.loadAvailability(
        pendingBooking.start_time
      );

    }

    catch (error) {

      console.error(
        'Reserva pendiente inválida:',
        error
      );


      sessionStorage
        .removeItem(
          this.pendingBookingKey
        );

    }

  }


  // =====================================================
  // MODAL - IR A MIS RESERVAS
  // =====================================================

  goToMyBookings(): void {

    this.showBookingSuccessModal =
      false;


    /*
     * Esta ruta la crearemos
     * posteriormente.
     */
    this.router.navigate(
      ['/mis-reservas']
    );

  }


  // =====================================================
  // MODAL - SEGUIR EXPLORANDO
  // =====================================================

  closeBookingSuccessModal(): void {

    this.showBookingSuccessModal =
      false;

  }


  // =====================================================
  // LIMPIAR MENSAJES DE RESERVA
  // =====================================================

  private resetBookingFeedback(): void {

    this.bookingError =
      '';


    this.bookingSuccess =
      '';


    this.createdBookingId =
      null;


    this.showBookingSuccessModal =
      false;

  }


  // =====================================================
  // FORMATEAR HORA
  // =====================================================

  formatTime(
    value: string
  ): string {

    if (
      !value
    ) {

      return '';

    }


    const parts =
      value.split(':');


    const hours =
      Number(
        parts[0]
      );


    const minutes =
      Number(
        parts[1]
      );


    if (
      !Number.isFinite(hours)
      ||
      !Number.isFinite(minutes)
    ) {

      return value;

    }


    const date =
      new Date();


    date.setHours(
      hours,
      minutes,
      0,
      0
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
  // FORMATEAR FECHA
  // =====================================================

  formatDate(
    value: string
  ): string {

    if (
      !value
    ) {

      return '';

    }


    const [
      year,
      month,
      day
    ] =
      value
        .split('-')
        .map(
          Number
        );


    const date =
      new Date(
        year,
        month - 1,
        day
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
  // FECHA MÍNIMA
  // =====================================================

  private getTodayDate():
    string {

    const today =
      new Date();


    const year =
      today.getFullYear();


    const month =
      String(
        today.getMonth() + 1
      )
        .padStart(
          2,
          '0'
        );


    const day =
      String(
        today.getDate()
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
  // INICIALES DEL BARBERO
  // =====================================================

  getBarberInitials(
    barber: BarberItem
  ): string {

    const first =
      barber.first_name
        ?.charAt(0)
        ?.toUpperCase()
      ||
      '';


    const last =
      barber.last_name
        ?.charAt(0)
        ?.toUpperCase()
      ||
      '';


    return (
      `${first}${last}`
    );

  }


  // =====================================================
  // EXPERIENCIA DEL BARBERO
  // =====================================================

  getExperience(
    years:
      number | null
  ): string {

    if (
      years === null
    ) {

      return (
        'Experiencia no especificada'
      );

    }


    if (
      years === 1
    ) {

      return (
        '1 año de experiencia'
      );

    }


    return (
      `${years} años de experiencia`
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


  // =====================================================
  // DURACIÓN DEL SERVICIO
  // =====================================================

  getDuration(
    minutes: number
  ): string {

    if (
      minutes < 60
    ) {

      return (
        `${minutes} min`
      );

    }


    const hours =
      Math.floor(
        minutes / 60
      );


    const remainingMinutes =
      minutes % 60;


    if (
      remainingMinutes === 0
    ) {

      return (
        `${hours} h`
      );

    }


    return (
      `${hours} h ${remainingMinutes} min`
    );

  }


  // =====================================================
  // ETIQUETAS DE LA BARBERÍA
  // =====================================================

  getTags():
    string[] {

    if (
      !this.barbershop
    ) {

      return [];

    }


    const tags:
      string[] = [];


    if (
      this.barbershop
        .offers_vip
    ) {

      tags.push(
        'Experiencia VIP'
      );

    }


    if (
      this.barbershop
        .offers_home_service
    ) {

      tags.push(
        'Servicio a domicilio'
      );

    }


    if (
      this.barbershop
        .only_men
    ) {

      tags.push(
        'Especializada en hombres'
      );

    }


    return tags;

  }

}
