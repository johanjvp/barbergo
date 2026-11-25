import { API_URL } from '../../../../core/api';
import { Icon } from '../../../../components/icon/icon';
import {
  ChangeDetectorRef,
  Component,
  DestroyRef,
  OnInit,
  inject
} from '@angular/core';

import {
  ActivatedRoute,
  RouterLink
} from '@angular/router';

import {
  HttpClient,
  HttpErrorResponse
} from '@angular/common/http';

import {
  takeUntilDestroyed
} from '@angular/core/rxjs-interop';

import {
  AdminBarbershopService
} from '../../../../services/admin-barbershop';

import {
  BarbershopSettingsService
} from '../../../../services/barbershop-settings';

import {
  AdminBookingService
} from '../../../../services/admin-booking';

import {
  ScheduleService
} from '../../../../services/schedule';

import {
  AdminBookingCalendar
} from '../../../../components/admin-booking-calendar/admin-booking-calendar';

import {
  AdminBarbershopDetail
  as AdminBarbershopDetailModel
} from '../../../../models/admin-barbershop';

import {
  BarbershopSettings,
  BarbershopSettingsActionResponse,
  BarbershopSettingsUpdate
} from '../../../../models/barbershop-settings';

import {
  AdminBookingCancelResponse,
  AdminBookingConfirmResponse,
  AdminBookingCompleteResponse,
  AdminBookingItem,
  AdminBookingStatus
} from '../../../../models/admin-booking';
import {
  BarberWeeklyAgenda
} from '../../../../models/barber-weekly-agenda';




type AdminBarbershopDetailTab =
  'summary'
  |
  'barbers'
  |
  'agenda'
  |
  'bookings'
  |
  'settings';


  type SettingsSection =
  | 'general'
  | 'bookings'
  | 'customers'
  | 'barbers'
  | 'notifications';


interface SettingsSectionItem {

  id:
    SettingsSection;

  label:
    string;

  description:
    string;

}

interface AdminBarbershopDetailTabItem {

  id:
    AdminBarbershopDetailTab;

  label:
    string;

  description:
    string;

}


interface AdminBarbershopBarber {

  id:
    number;

  user_id:
    number;

  barbershop_id:
    number;

  first_name:
    string | null;

  last_name:
    string | null;

  bio:
    string | null;

  years_experience:
    number | null;

  accepts_home_service:
    boolean;

  is_active:
    boolean;

  service_ids:
    number[];

  created_at:
    string | null;

  updated_at:
    string | null;

}


@Component({
  selector:
    'app-admin-barbershop-detail',

  imports: [
    Icon,
    RouterLink,
    AdminBookingCalendar
  ],

  templateUrl:
    './admin-barbershop-detail.html',

  styleUrl:
    './admin-barbershop-detail.scss'
})
export class AdminBarbershopDetail
implements OnInit {


  // =====================================================
  // DEPENDENCIAS
  // =====================================================



  private readonly route =
    inject(
      ActivatedRoute
    );


  private readonly http =
    inject(
      HttpClient
    );



  private readonly barbershopService =
    inject(
      AdminBarbershopService
    );


  private readonly bookingService =
    inject(
      AdminBookingService
    );


  private readonly scheduleService =
    inject(
      ScheduleService
    );

    private readonly settingsService =
  inject(
    BarbershopSettingsService
  );



  private readonly destroyRef =
    inject(
      DestroyRef
    );

  private readonly cdr =
    inject(
      ChangeDetectorRef
    );


  // =====================================================
  // API
  // =====================================================

  private readonly apiUrl =
    API_URL;


  // =====================================================
  // ID DE BARBERÍA
  // =====================================================

  barbershopId:
    number | null =
      null;


  // =====================================================
  // DATOS DE BARBERÍA
  // =====================================================

  barbershop:
    AdminBarbershopDetailModel
    | null =
      null;


  // =====================================================
  // BARBEROS
  // =====================================================

  barbers:
    AdminBarbershopBarber[] =
      [];


  loadingBarbers =
    false;


  barbersError =
    '';


  barbersLoaded =
    false;


  // =====================================================
  // BARBERO SELECCIONADO
  // =====================================================

  selectedBarberId:
    number | null =
      null;


  // =====================================================
  // SEMANA DE AGENDA
  // =====================================================

  weekStart:
    Date =
      this.getMonday(
        new Date()
      );


  // =====================================================
  // AGENDA SEMANAL
  // =====================================================

  weeklyAgenda:
    BarberWeeklyAgenda
    | null =
      null;


  loadingAgenda =
    false;


  agendaError =
    '';


  // =====================================================
  // RESERVAS PARA EL CALENDARIO
  // =====================================================

  agendaBookings:
    AdminBookingItem[] =
      [];


  loadingAgendaBookings =
    false;


  agendaBookingsError =
    '';

    // =====================================================
// RESERVAS DE LA BARBERÍA
// =====================================================

shopBookings:
  AdminBookingItem[] =
    [];


shopBookingsTotal =
  0;


loadingShopBookings =
  false;


shopBookingsError =
  '';


shopBookingsSearch =
  '';


shopBookingsStatus =
  'all';


shopBookingsLoaded =
  false;




  // =====================================================
  // ESTADOS GENERALES
  // =====================================================

  loading =
    true;


  error =
    '';


  // =====================================================
  // PESTAÑA ACTIVA
  // =====================================================

  activeTab:
    AdminBarbershopDetailTab =
      'summary';


  // =====================================================
  // PESTAÑAS
  // =====================================================

  readonly tabs:
    AdminBarbershopDetailTabItem[] = [

      {
        id:
          'summary',

        label:
          'Resumen',

        description:
          'Información general de la barbería'
      },

      {
        id:
          'barbers',

        label:
          'Barberos',

        description:
          'Profesionales asociados'
      },

      {
        id:
          'agenda',

        label:
          'Agenda',

        description:
          'Horarios y disponibilidad'
      },

      {
        id:
          'bookings',

        label:
          'Reservas',

        description:
          'Gestión de citas'
      },

      {
        id:
          'settings',

        label:
          'Configuración',

        description:
          'Ajustes de la barbería'
      }

    ];


  // =====================================================
  // INICIALIZAR
  // =====================================================

  ngOnInit(): void {

    this.route
      .paramMap
      .pipe(
        takeUntilDestroyed(
          this.destroyRef
        )
      )
      .subscribe(
        params => {

          const rawId =
            params.get(
              'id'
            );


          const id =
            Number(
              rawId
            );


          if (
            !rawId
            ||
            !Number.isInteger(
              id
            )
            ||
            id <= 0
          ) {

            this.loading =
              false;


            this.error =
              'La barbería indicada no es válida.';


            this.barbershopId =
              null;


            this.barbershop =
              null;


            this.resetBarbers();


            this.resetSettings();


            this.cdr
              .detectChanges();


            return;

          }


          this.barbershopId =
            id;


          this.loadBarbershop();

        }
      );

  }


  // =====================================================
  // CARGAR BARBERÍA
  // =====================================================

  loadBarbershop(): void {

    if (
      this.barbershopId ===
      null
    ) {

      return;

    }


    this.loading =
      true;


    this.error =
      '';


    this.barbershop =
      null;


    this.resetBarbers();


    this.resetSettings();


    this.barbershopService
      .getById(
        this.barbershopId
      )
      .pipe(
        takeUntilDestroyed(
          this.destroyRef
        )
      )
      .subscribe({

        next: (
          response:
            AdminBarbershopDetailModel
        ) => {

          this.barbershop =
            response;


          this.loading =
            false;


          this.cdr
            .detectChanges();


          this.loadBarbers();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error cargando detalle de barbería:',
            error
          );


          this.barbershop =
            null;


          this.loading =
            false;


          this.error =
            this.getErrorMessage(
              error
            );


          this.resetBarbers();


          this.resetSettings();


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // CARGAR BARBEROS
  // =====================================================

  loadBarbers(): void {

    if (
      this.barbershopId ===
      null
    ) {

      return;

    }


    this.loadingBarbers =
      true;


    this.barbersError =
      '';


    this.barbersLoaded =
      false;


    this.barbers =
      [];


    this.selectedBarberId =
      null;


    this.resetAgenda();


    this.http
      .get<
        AdminBarbershopBarber[]
      >(
        `${
          this.apiUrl
        }/barbershops/${
          this.barbershopId
        }/barbers`
      )
      .pipe(
        takeUntilDestroyed(
          this.destroyRef
        )
      )
      .subscribe({

        next: (
          response:
            AdminBarbershopBarber[]
        ) => {

          this.barbers =
            Array.isArray(
              response
            )
              ? response
              : [];


          this.loadingBarbers =
            false;


          this.barbersLoaded =
            true;


          const firstActiveBarber =
            this.barbers
              .find(
                barber =>
                  barber.is_active
              );


          if (
            firstActiveBarber
          ) {

            this.selectedBarberId =
              firstActiveBarber.id;


            if (
              this.activeTab ===
              'agenda'
            ) {

              this.loadAgenda();

            }

          }


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error cargando barberos de la barbería:',
            error
          );


          this.barbers =
            [];


          this.selectedBarberId =
            null;


          this.loadingBarbers =
            false;


          this.barbersLoaded =
            true;


          this.barbersError =
            this.getBarbersErrorMessage(
              error
            );


          this.resetAgenda();


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // CARGAR AGENDA COMPLETA
  // =====================================================

  loadAgenda(): void {

    if (
      this.selectedBarberId ===
      null
      ||
      this.barbershopId ===
      null
    ) {

      this.resetAgenda();

      return;

    }


    this.loadWeeklyAgenda();


    this.loadAgendaBookings();

  }


  // =====================================================
  // CARGAR HORARIO SEMANAL
  // =====================================================

  loadWeeklyAgenda(): void {

    if (
      this.selectedBarberId ===
      null
    ) {

      return;

    }


    this.loadingAgenda =
      true;


    this.agendaError =
      '';


    this.weeklyAgenda =
      null;


    const weekStartIso =
      this.toIsoDate(
        this.weekStart
      );


    this.scheduleService
      .getWeeklyAgenda(
        this.selectedBarberId,
        weekStartIso
      )
      .pipe(
        takeUntilDestroyed(
          this.destroyRef
        )
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


          this.agendaError =
            this.getAgendaErrorMessage(
              error
            );


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // CARGAR RESERVAS DE LA SEMANA
  // =====================================================

  loadAgendaBookings(): void {

    if (
      this.selectedBarberId ===
      null
      ||
      this.barbershopId ===
      null
    ) {

      return;

    }


    this.loadingAgendaBookings =
      true;


    this.agendaBookingsError =
      '';


    this.agendaBookings =
      [];


    const dateFrom =
      this.toIsoDate(
        this.weekStart
      );


    const weekEnd =
      new Date(
        this.weekStart
      );


    weekEnd.setDate(
      weekEnd.getDate()
      +
      6
    );


    const dateTo =
      this.toIsoDate(
        weekEnd
      );


    this.bookingService
      .getAll(
        '',
        'all',
        this.barbershopId,
        this.selectedBarberId,
        dateFrom,
        dateTo,
        100,
        0
      )
      .pipe(
        takeUntilDestroyed(
          this.destroyRef
        )
      )
      .subscribe({

        next: (
          response
        ) => {

          this.agendaBookings =
            response.items
            ??
            [];


          this.loadingAgendaBookings =
            false;


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error cargando reservas de agenda:',
            error
          );


          this.agendaBookings =
            [];


          this.loadingAgendaBookings =
            false;


          this.agendaBookingsError =
            this.getAgendaBookingsErrorMessage(
              error
            );


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // REINICIAR BARBEROS
  // =====================================================

  private resetBarbers(): void {

    this.barbers =
      [];


    this.loadingBarbers =
      false;


    this.barbersError =
      '';


    this.barbersLoaded =
      false;


    this.selectedBarberId =
      null;


    this.resetAgenda();

  }


  // =====================================================
  // REINICIAR AGENDA
  // =====================================================

  private resetAgenda(): void {

    this.weeklyAgenda =
      null;


    this.loadingAgenda =
      false;


    this.agendaError =
      '';


    this.agendaBookings =
      [];


    this.loadingAgendaBookings =
      false;


    this.agendaBookingsError =
      '';

  }


  // =====================================================
  // CAMBIAR PESTAÑA
  // =====================================================

  setActiveTab(
    tab:
      AdminBarbershopDetailTab
  ): void {

    if (
      this.activeTab ===
      tab
    ) {

      return;

    }


    this.activeTab =
      tab;


    if (
      (
        tab ===
        'barbers'
        ||
        tab ===
        'agenda'
      )
      &&
      !this.barbersLoaded
      &&
      !this.loadingBarbers
    ) {

      this.loadBarbers();

    }


    if (
      tab ===
      'agenda'
      &&
      this.selectedBarberId !==
        null
      &&
      !this.weeklyAgenda
      &&
      !this.loadingAgenda
    ) {

      this.loadAgenda();

    }

    if (
  tab ===
  'bookings'
  &&
  !this.shopBookingsLoaded
  &&
  !this.loadingShopBookings
) {

  this.loadShopBookings();

}

if (
  tab ===
  'settings'
  &&
  !this.settingsLoaded
  &&
  !this.loadingSettings
) {

  this.loadSettings();

}



  }




  // =====================================================
  // VALIDAR PESTAÑA ACTIVA
  // =====================================================

  isActiveTab(
    tab:
      AdminBarbershopDetailTab
  ): boolean {

    return (
      this.activeTab ===
      tab
    );

  }


  // =====================================================
  // CAMBIAR BARBERO
  // =====================================================

  onBarberChange(
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


    const barberId =
      Number(
        target.value
      );


    if (
      Number.isInteger(
        barberId
      )
      &&
      barberId > 0
    ) {

      this.selectedBarberId =
        barberId;


      this.goToCurrentWeek();


      return;

    }


    this.selectedBarberId =
      null;


    this.resetAgenda();

  }


  // =====================================================
  // VER AGENDA DE BARBERO
  // =====================================================

  openBarberAgenda(
    barberId:
      number
  ): void {

    this.selectedBarberId =
      barberId;


    this.activeTab =
      'agenda';


    this.weekStart =
      this.getMonday(
        new Date()
      );


    this.loadAgenda();

  }


  // =====================================================
  // SEMANA ANTERIOR
  // =====================================================

  goToPreviousWeek(): void {

    const previous =
      new Date(
        this.weekStart
      );


    previous.setDate(
      previous.getDate()
      -
      7
    );


    this.weekStart =
      previous;


    this.loadAgenda();

  }


  // =====================================================
  // SEMANA SIGUIENTE
  // =====================================================

  goToNextWeek(): void {

    const next =
      new Date(
        this.weekStart
      );


    next.setDate(
      next.getDate()
      +
      7
    );


    this.weekStart =
      next;


    this.loadAgenda();

  }


  // =====================================================
  // SEMANA ACTUAL
  // =====================================================

  goToCurrentWeek(): void {

    this.weekStart =
      this.getMonday(
        new Date()
      );


    this.loadAgenda();

  }


  // =====================================================
// ABRIR RESERVA
// =====================================================

openBooking(
  booking:
    AdminBookingItem
): void {

  this.clearBookingActionMessages();


  this.selectedBooking =
    booking;


  this.cdr
    .detectChanges();

}


// =====================================================
// CERRAR RESERVA
// =====================================================

closeBooking(): void {

  this.selectedBooking =
    null;


  this.clearBookingActionMessages();


  this.cdr
    .detectChanges();

}


// =====================================================
// LIMPIAR MENSAJES
// =====================================================

private clearBookingActionMessages(): void {

  this.confirmSuccess =
    '';

  this.confirmError =
    '';

  this.cancelSuccess =
    '';

  this.cancelError =
    '';

  this.completeSuccess =
    '';

  this.completeError =
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
// ESTADOS DE PROCESO
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


isCancellingBooking(
  bookingId:
    number
): boolean {

  return (
    this.cancellingBookingId ===
    bookingId
  );

}


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


  this.clearBookingActionMessages();


  this.confirmingBookingId =
    booking.id;


  this.bookingService
    .confirmBooking(
      booking.id
    )
    .pipe(
      takeUntilDestroyed(
        this.destroyRef
      )
    )
    .subscribe({

      next: (
        response:
          AdminBookingConfirmResponse
      ) => {

        const updatedBooking =
          this.buildUpdatedBooking(
            booking,
            response.status_id,
            response.status_code,
            response.status_name
          );


        this.updateBookingLocally(
          updatedBooking
        );


        this.confirmSuccess =
          response.message;


        this.confirmingBookingId =
          null;


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


        this.confirmError =
          this.getBookingActionError(
            error,
            'No fue posible confirmar la reserva.'
          );


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


  this.clearBookingActionMessages();


  this.cancellingBookingId =
    booking.id;


  this.bookingService
    .cancelBooking(
      booking.id
    )
    .pipe(
      takeUntilDestroyed(
        this.destroyRef
      )
    )
    .subscribe({

      next: (
        response:
          AdminBookingCancelResponse
      ) => {

        const updatedBooking =
          this.buildUpdatedBooking(
            booking,
            response.status_id,
            response.status_code,
            response.status_name
          );


        this.updateBookingLocally(
          updatedBooking
        );


        this.cancelSuccess =
          response.message;


        this.cancellingBookingId =
          null;


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


        this.cancelError =
          this.getBookingActionError(
            error,
            'No fue posible cancelar la reserva.'
          );


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
      `¿Confirmas que el servicio de la reserva #${booking.id} fue completado?`
    );


  if (
    !confirmed
  ) {

    return;

  }


  this.clearBookingActionMessages();


  this.completingBookingId =
    booking.id;


  this.bookingService
    .completeBooking(
      booking.id
    )
    .pipe(
      takeUntilDestroyed(
        this.destroyRef
      )
    )
    .subscribe({

      next: (
        response:
          AdminBookingCompleteResponse
      ) => {

        const updatedBooking =
          this.buildUpdatedBooking(
            booking,
            response.status_id,
            response.status_code,
            response.status_name
          );


        this.updateBookingLocally(
          updatedBooking
        );


        this.completeSuccess =
          response.message;


        this.completingBookingId =
          null;


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


        this.completeError =
          this.getBookingActionError(
            error,
            'No fue posible completar la reserva.'
          );


        this.cdr
          .detectChanges();

      }

    });

}


// =====================================================
// CONSTRUIR RESERVA ACTUALIZADA
// =====================================================

private buildUpdatedBooking(
  booking:
    AdminBookingItem,
  statusId:
    number,
  statusCode:
    AdminBookingStatus,
  statusName:
    string
): AdminBookingItem {

  return {

    ...booking,

    status_id:
      statusId,

    status_code:
      statusCode,

    status_name:
      statusName,

    updated_at:
      new Date()
        .toISOString()

  };

}

// =====================================================
// ACTUALIZAR RESERVA EN TODAS LAS VISTAS
// =====================================================

private updateBookingLocally(
  updatedBooking:
    AdminBookingItem
): void {

  this.shopBookings =
    this.shopBookings
      .map(
        booking =>
          booking.id ===
            updatedBooking.id
            ? updatedBooking
            : booking
      );


  this.agendaBookings =
    this.agendaBookings
      .map(
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
// ERROR ACCIONES
// =====================================================

private getBookingActionError(
  error:
    HttpErrorResponse,
  fallback:
    string
): string {

  const detail =
    error.error
      ?.detail;


  if (
    typeof detail ===
      'string'
    &&
    detail.trim()
  ) {

    return detail;

  }


  if (
    error.status ===
    401
  ) {

    return (
      'Tu sesión ha expirado.'
    );

  }


  if (
    error.status ===
    403
  ) {

    return (
      'No tienes permisos para realizar esta acción.'
    );

  }


  if (
    error.status ===
    404
  ) {

    return (
      'La reserva ya no existe.'
    );

  }


  if (
    error.status ===
    409
  ) {

    return (
      'La reserva ya no permite esta acción desde su estado actual.'
    );

  }


  return fallback;

}

// =====================================================
// CONFIGURACIÓN DE BARBERÍA
// =====================================================

settings:
  BarbershopSettings | null =
    null;


loadingSettings =
  false;


settingsLoaded =
  false;


settingsError =
  '';


settingsSuccess =
  '';


savingSetting =
  false;


savingAutoConfirm =
  false;


// =====================================================
// SUBSECCIÓN ACTIVA DE CONFIGURACIÓN
// =====================================================

activeSettingsSection:
  SettingsSection =
    'general';


// =====================================================
// SUBSECCIONES DE CONFIGURACIÓN
// =====================================================

readonly settingsSections:
  SettingsSectionItem[] = [

    {
      id:
        'general',

      label:
        'General',

      description:
        'Operación'
    },

    {
      id:
        'bookings',

      label:
        'Reservas',

      description:
        'Agenda y reglas'
    },

    {
      id:
        'customers',

      label:
        'Clientes',

      description:
        'Experiencia'
    },

    {
      id:
        'barbers',

      label:
        'Barberos',

      description:
        'Permisos'
    },

    {
      id:
        'notifications',

      label:
        'Notificaciones',

      description:
        'Avisos'
    }

  ];


// =====================================================
// CARGAR CONFIGURACIÓN
// =====================================================

loadSettings(): void {

  if (
    this.barbershopId ===
    null
  ) {

    return;

  }


  this.loadingSettings =
    true;


  this.settingsError =
    '';


  this.settingsSuccess =
    '';


  this.settingsService
    .getSettings(
      this.barbershopId
    )
    .pipe(
      takeUntilDestroyed(
        this.destroyRef
      )
    )
    .subscribe({

      next: (
        response:
          BarbershopSettings
      ) => {

        this.settings =
          response;


        this.loadingSettings =
          false;


        this.settingsLoaded =
          true;


        this.cdr
          .detectChanges();

      },


      error: (
        error:
          HttpErrorResponse
      ) => {

        console.error(
          'Error cargando configuración de barbería:',
          error
        );


        this.settings =
          null;


        this.loadingSettings =
          false;


        this.settingsLoaded =
          true;


        this.settingsError =
          this.getSettingsErrorMessage(
            error,
            'No fue posible cargar la configuración de esta barbería.'
          );


        this.cdr
          .detectChanges();

      }

    });

}


// =====================================================
// CAMBIAR SUBSECCIÓN DE CONFIGURACIÓN
// =====================================================

setActiveSettingsSection(
  section:
    SettingsSection
): void {

  if (
    this.activeSettingsSection ===
    section
  ) {

    return;

  }


  this.activeSettingsSection =
    section;


  this.clearSettingsFeedback();

}


// =====================================================
// VALIDAR SUBSECCIÓN ACTIVA
// =====================================================

isSettingsSectionActive(
  section:
    SettingsSection
): boolean {

  return (
    this.activeSettingsSection ===
    section
  );

}


// =====================================================
// SUBSECCIÓN SELECCIONADA
// =====================================================

get selectedSettingsSection():
  SettingsSectionItem {

  const section =
    this.settingsSections
      .find(
        item =>
          item.id ===
          this.activeSettingsSection
      );


  return (
    section
    ??
    this.settingsSections[0]
  );

}


// =====================================================
// CONFIRMACIÓN AUTOMÁTICA
// =====================================================

toggleAutoConfirmation(): void {

  if (
    !this.settings
    ||
    this.barbershopId ===
      null
    ||
    this.savingAutoConfirm
    ||
    this.savingSetting
  ) {

    return;

  }


  const newValue =
    !this.settings
      .auto_confirm_bookings;


  this.savingAutoConfirm =
    true;


  this.clearSettingsFeedback();


  this.settingsService
    .updateAutoConfirmation(
      this.barbershopId,
      newValue
    )
    .pipe(
      takeUntilDestroyed(
        this.destroyRef
      )
    )
    .subscribe({

      next: (
        response:
          BarbershopSettingsActionResponse
      ) => {

        this.settings =
          response.settings;


        this.settingsSuccess =
          response.message;


        this.savingAutoConfirm =
          false;


        this.cdr
          .detectChanges();

      },


      error: (
        error:
          HttpErrorResponse
      ) => {

        console.error(
          'Error cambiando confirmación automática:',
          error
        );


        this.savingAutoConfirm =
          false;


        this.settingsError =
          this.getSettingsErrorMessage(
            error,
            'No fue posible actualizar la confirmación automática.'
          );


        this.cdr
          .detectChanges();

      }

    });

}


// =====================================================
// ACTUALIZAR AJUSTE BOOLEANO
// =====================================================

updateBooleanSetting(
  field:
    keyof BarbershopSettingsUpdate,
  value:
    boolean
): void {

  if (
    !this.settings
    ||
    this.barbershopId ===
      null
    ||
    this.savingSetting
    ||
    this.savingAutoConfirm
  ) {

    return;

  }


  const payload = {

    [field]:
      value

  } as BarbershopSettingsUpdate;


  this.updateBarbershopSettings(
    payload
  );

}


// =====================================================
// ACTUALIZAR AJUSTE NUMÉRICO
// =====================================================

updateNumberSetting(
  field:
    keyof BarbershopSettingsUpdate,
  value:
    number
): void {

  if (
    !this.settings
    ||
    this.barbershopId ===
      null
    ||
    this.savingSetting
    ||
    this.savingAutoConfirm
  ) {

    return;

  }


  if (
    !Number.isFinite(
      value
    )
  ) {

    return;

  }


  const payload = {

    [field]:
      value

  } as BarbershopSettingsUpdate;


  this.updateBarbershopSettings(
    payload
  );

}


// =====================================================
// GUARDAR CONFIGURACIÓN
// =====================================================

private updateBarbershopSettings(
  payload:
    BarbershopSettingsUpdate
): void {

  if (
    this.barbershopId ===
    null
  ) {

    return;

  }


  this.savingSetting =
    true;


  this.clearSettingsFeedback();


  this.settingsService
    .updateSettings(
      this.barbershopId,
      payload
    )
    .pipe(
      takeUntilDestroyed(
        this.destroyRef
      )
    )
    .subscribe({

      next: (
        response:
          BarbershopSettingsActionResponse
      ) => {

        this.settings =
          response.settings;


        this.settingsSuccess =
          response.message;


        this.savingSetting =
          false;


        this.cdr
          .detectChanges();

      },


      error: (
        error:
          HttpErrorResponse
      ) => {

        console.error(
          'Error actualizando configuración:',
          error
        );


        this.savingSetting =
          false;


        this.settingsError =
          this.getSettingsErrorMessage(
            error,
            'No fue posible actualizar la configuración.'
          );


        this.cdr
          .detectChanges();

      }

    });

}


// =====================================================
// LIMPIAR MENSAJES DE CONFIGURACIÓN
// =====================================================

clearSettingsFeedback(): void {

  this.settingsError =
    '';


  this.settingsSuccess =
    '';

}


// =====================================================
// REINICIAR CONFIGURACIÓN
// =====================================================

private resetSettings(): void {

  this.settings =
    null;


  this.loadingSettings =
    false;


  this.settingsLoaded =
    false;


  this.settingsError =
    '';


  this.settingsSuccess =
    '';


  this.savingSetting =
    false;


  this.savingAutoConfirm =
    false;


  this.activeSettingsSection =
    'general';

}


// =====================================================
// ERROR DE CONFIGURACIÓN
// =====================================================

private getSettingsErrorMessage(
  error:
    HttpErrorResponse,
  fallback:
    string
): string {

  const backendDetail =
    error.error
      ?.detail;


  if (
    typeof backendDetail ===
      'string'
    &&
    backendDetail.trim()
  ) {

    return backendDetail;

  }


  if (
    error.status ===
    401
  ) {

    return (
      'Tu sesión ha expirado.'
    );

  }


  if (
    error.status ===
    403
  ) {

    return (
      'No tienes permisos para administrar la configuración de esta barbería.'
    );

  }


  if (
    error.status ===
    404
  ) {

    return (
      'La barbería seleccionada no existe.'
    );

  }


  if (
    error.status ===
    422
  ) {

    return (
      'El valor enviado para esta configuración no es válido.'
    );

  }


  if (
    error.status ===
    0
  ) {

    return (
      'No fue posible conectar con el servidor.'
    );

  }


  return fallback;

}


// =====================================================
// INICIALES DEL CLIENTE
// =====================================================

getClientInitials(
  booking:
    AdminBookingItem
): string {

  const firstName =
    booking.client_first_name
      ?.trim()
    ??
    '';


  const lastName =
    booking.client_last_name
      ?.trim()
    ??
    '';


  if (
    firstName
    &&
    lastName
  ) {

    return (
      `${
        firstName.charAt(0)
      }${
        lastName.charAt(0)
      }`
        .toUpperCase()
    );

  }


  if (
    firstName
  ) {

    return (
      firstName
        .substring(
          0,
          2
        )
        .toUpperCase()
    );

  }


  return 'CL';

}


// =====================================================
// DURACIÓN
// =====================================================

getBookingDuration(
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


  const difference =
    end.getTime()
    -
    start.getTime();


  if (
    Number.isNaN(
      difference
    )
    ||
    difference <= 0
  ) {

    return (
      booking.service_duration_minutes
      ??
      0
    );

  }


  return Math.round(
    difference
    /
    60000
  );

}



  // =====================================================
  // BARBERO SELECCIONADO
  // =====================================================

  get selectedBarber():
    AdminBarbershopBarber
    | null {

    if (
      this.selectedBarberId ===
      null
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
  // NOMBRE BARBERO SELECCIONADO
  // =====================================================

  get selectedBarberName():
    string {

    if (
      !this.selectedBarber
    ) {

      return '';

    }


    return this.getBarberFullName(
      this.selectedBarber
    );

  }


  // =====================================================
  // NOMBRE COMPLETO BARBERO
  // =====================================================

  getBarberFullName(
    barber:
      AdminBarbershopBarber
  ): string {

    const fullName =
      `${
        barber.first_name
        ?? ''
      } ${
        barber.last_name
        ?? ''
      }`
        .trim();


    if (
      fullName
    ) {

      return fullName;

    }


    return (
      `Barbero #${
        barber.id
      }`
    );

  }


  // =====================================================
  // INICIALES BARBERO
  // =====================================================

  getBarberInitials(
    barber:
      AdminBarbershopBarber
  ): string {

    const firstName =
      barber.first_name
        ?.trim()
      ??
      '';


    const lastName =
      barber.last_name
        ?.trim()
      ??
      '';


    if (
      firstName
      &&
      lastName
    ) {

      return (
        `${
          firstName.charAt(
            0
          )
        }${
          lastName.charAt(
            0
          )
        }`
        .toUpperCase()
      );

    }


    if (
      firstName
    ) {

      return (
        firstName
          .substring(
            0,
            2
          )
          .toUpperCase()
      );

    }


    return 'B';

  }


  // =====================================================
  // EXPERIENCIA BARBERO
  // =====================================================

  getBarberExperience(
    barber:
      AdminBarbershopBarber
  ): string {

    const years =
      barber.years_experience;


    if (
      years ===
      null
      ||
      years ===
      undefined
    ) {

      return (
        'Experiencia no registrada'
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
      `${
        years
      } años de experiencia`
    );

  }


  // =====================================================
  // BARBEROS ACTIVOS
  // =====================================================

  get activeBarbers():
    AdminBarbershopBarber[] {

    return (
      this.barbers
        .filter(
          barber =>
            barber.is_active
        )
    );

  }


  // =====================================================
  // BARBEROS INACTIVOS
  // =====================================================

  get inactiveBarbers():
    AdminBarbershopBarber[] {

    return (
      this.barbers
        .filter(
          barber =>
            !barber.is_active
        )
    );

  }


  // =====================================================
  // INICIALES BARBERÍA
  // =====================================================

  getBarbershopInitials(): string {

    const name =
      this.barbershop
        ?.name
        ?.trim();


    if (
      !name
    ) {

      return 'BG';

    }


    const words =
      name
        .split(
          /\s+/
        )
        .filter(
          Boolean
        );


    if (
      words.length === 1
    ) {

      return (
        words[0]
          .substring(
            0,
            2
          )
          .toUpperCase()
      );

    }


    return (
      `${
        words[0]
          .charAt(
            0
          )
      }${
        words[1]
          .charAt(
            0
          )
      }`
      .toUpperCase()
    );

  }


  // =====================================================
  // UBICACIÓN
  // =====================================================

  getLocation(): string {

    if (
      !this.barbershop
    ) {

      return (
        'Ubicación no disponible'
      );

    }


    const parts =
      [
        this.barbershop
          .neighborhood,

        this.barbershop
          .city
      ]
      .filter(
        (
          value
        ):
          value is string =>
            Boolean(
              value
              &&
              value.trim()
            )
      );


    if (
      parts.length === 0
    ) {

      return (
        'Ubicación no disponible'
      );

    }


    return parts.join(
      ', '
    );

  }


  // =====================================================
// CARGAR RESERVAS DE LA BARBERÍA
// =====================================================

loadShopBookings(): void {

  if (
    this.barbershopId ===
    null
  ) {

    return;

  }


  this.loadingShopBookings =
    true;


  this.shopBookingsError =
    '';


  this.bookingService
    .getAll(
      this.shopBookingsSearch,
      this.shopBookingsStatus,
      this.barbershopId,
      null,
      '',
      '',
      100,
      0
    )
    .pipe(
      takeUntilDestroyed(
        this.destroyRef
      )
    )
    .subscribe({

      next: (
        response
      ) => {

        this.shopBookings =
          response.items
          ??
          [];


        this.shopBookingsTotal =
          response.total
          ??
          this.shopBookings.length;


        this.loadingShopBookings =
          false;


        this.shopBookingsLoaded =
          true;


        this.cdr
          .detectChanges();

      },


      error: (
        error:
          HttpErrorResponse
      ) => {

        console.error(
          'Error cargando reservas de barbería:',
          error
        );


        this.shopBookings =
          [];


        this.shopBookingsTotal =
          0;


        this.loadingShopBookings =
          false;


        this.shopBookingsLoaded =
          true;


        const backendDetail =
          error.error
            ?.detail;


        this.shopBookingsError =
          typeof backendDetail ===
            'string'
            &&
            backendDetail.trim()
            ? backendDetail
            : 'No fue posible cargar las reservas de esta barbería.';


        this.cdr
          .detectChanges();

      }

    });

}


// =====================================================
// BUSCAR RESERVAS
// =====================================================

onShopBookingsSearch(
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


  this.shopBookingsSearch =
    target.value;

}


// =====================================================
// FILTRO ESTADO RESERVAS
// =====================================================

onShopBookingsStatusChange(
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


  this.shopBookingsStatus =
    target.value;


  this.loadShopBookings();

}


// =====================================================
// LIMPIAR FILTROS RESERVAS
// =====================================================

clearShopBookingsFilters(): void {

  this.shopBookingsSearch =
    '';


  this.shopBookingsStatus =
    'all';


  this.loadShopBookings();

}

// =====================================================
// RESERVA SELECCIONADA
// =====================================================

selectedBooking:
  AdminBookingItem | null =
    null;


// =====================================================
// ACCIONES SOBRE RESERVA
// =====================================================

confirmingBookingId:
  number | null =
    null;


cancellingBookingId:
  number | null =
    null;


completingBookingId:
  number | null =
    null;


confirmSuccess =
  '';


confirmError =
  '';


cancelSuccess =
  '';


cancelError =
  '';


completeSuccess =
  '';


completeError =
  '';


// =====================================================
// FECHA RESERVA
// =====================================================

formatBookingDate(
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

    return (
      'Fecha no disponible'
    );

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

    return (
      'Fecha no disponible'
    );

  }


  return new Intl
    .DateTimeFormat(
      'es-CO',
      {
        weekday:
          'short',

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
// HORA RESERVA
// =====================================================

formatBookingTime(
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

    return '--:--';

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

    return '--:--';

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
      date
    );

}


// =====================================================
// CLASE DE ESTADO
// =====================================================

getBookingStatusClass(
  booking:
    AdminBookingItem
): string {

  switch (
    booking.status_code
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
      return 'default';

  }

}


  // =====================================================
  // FORMATEAR MONEDA
  // =====================================================

  formatCurrency(
    value:
      number
      | null
      | undefined
  ): string {

    const amount =
      Number(
        value
        ?? 0
      );


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
        amount
      );

  }


  // =====================================================
  // FORMATEAR FECHA
  // =====================================================

  formatDate(
    value:
      string
      | null
      | undefined
  ): string {

    if (
      !value
    ) {

      return (
        'No disponible'
      );

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

      return (
        'No disponible'
      );

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
  // ISO LOCAL
  // =====================================================

  private toIsoDate(
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
  // LUNES DE LA SEMANA
  // =====================================================

  private getMonday(
    date:
      Date
  ): Date {

    const result =
      new Date(
        date
      );


    const currentDay =
      result.getDay();


    const difference =
      currentDay ===
        0
        ? -6
        : 1
          -
          currentDay;


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
  // ERROR BARBERÍA
  // =====================================================

  private getErrorMessage(
    error:
      HttpErrorResponse
  ): string {

    if (
      error.status === 404
    ) {

      return (
        'La barbería que intentas consultar '
        +
        'no existe.'
      );

    }


    if (
      error.status === 401
      ||
      error.status === 403
    ) {

      return (
        'No tienes permisos para consultar '
        +
        'esta barbería.'
      );

    }


    if (
      error.status === 0
    ) {

      return (
        'No fue posible conectar con el servidor.'
      );

    }


    const backendDetail =
      error.error
        ?.detail;


    if (
      typeof backendDetail ===
      'string'
      &&
      backendDetail.trim()
    ) {

      return backendDetail;

    }


    return (
      'No fue posible cargar la información '
      +
      'de la barbería.'
    );

  }


  // =====================================================
  // ERROR BARBEROS
  // =====================================================

  private getBarbersErrorMessage(
    error:
      HttpErrorResponse
  ): string {

    if (
      error.status === 0
    ) {

      return (
        'No fue posible conectar con el servidor.'
      );

    }


    return (
      'No fue posible cargar '
      +
      'el equipo de la barbería.'
    );

  }


  // =====================================================
  // ERROR AGENDA
  // =====================================================

  private getAgendaErrorMessage(
    error:
      HttpErrorResponse
  ): string {

    if (
      error.status === 0
    ) {

      return (
        'No fue posible conectar con el servidor.'
      );

    }


    const backendDetail =
      error.error
        ?.detail;


    if (
      typeof backendDetail ===
      'string'
      &&
      backendDetail.trim()
    ) {

      return backendDetail;

    }


    return (
      'No fue posible cargar '
      +
      'la agenda semanal del barbero.'
    );

  }


  // =====================================================
  // ERROR RESERVAS AGENDA
  // =====================================================

  private getAgendaBookingsErrorMessage(
    error:
      HttpErrorResponse
  ): string {

    if (
      error.status === 0
    ) {

      return (
        'No fue posible conectar con el servidor.'
      );

    }


    const backendDetail =
      error.error
        ?.detail;


    if (
      typeof backendDetail ===
      'string'
      &&
      backendDetail.trim()
    ) {

      return backendDetail;

    }


    if (
      Array.isArray(
        backendDetail
      )
      &&
      backendDetail.length > 0
    ) {

      return backendDetail
        .map(
          item =>
            item?.msg
            ??
            String(
              item
            )
        )
        .join(
          ' · '
        );

    }


    return (
      'No fue posible cargar '
      +
      'las reservas de esta semana.'
    );

  }

}
