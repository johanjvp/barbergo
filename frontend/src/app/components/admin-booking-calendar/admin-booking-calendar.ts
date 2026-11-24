import {
  Component,
  EventEmitter,
  Input,
  Output
} from '@angular/core';

import {
  AdminBookingItem
} from '../../models/admin-booking';

import {
  AgendaBlock,
  AgendaBreak,
  BarberAgendaDay,
  BarberWeeklyAgenda
} from '../../models/barber-weekly-agenda';


interface CalendarDay {

  date:
    Date;

  isoDate:
    string;

  dayName:
    string;

  dayNumber:
    string;

  monthName:
    string;

  isToday:
    boolean;

}


@Component({
  selector:
    'app-admin-booking-calendar',

  imports: [],

  templateUrl:
    './admin-booking-calendar.html',

  styleUrl:
    './admin-booking-calendar.scss'
})
export class AdminBookingCalendar {


  // =====================================================
  // INPUTS
  // =====================================================

  @Input()
  bookings:
    AdminBookingItem[] =
      [];


  @Input()
  barberName =
    '';


  @Input()
  weekStart:
    Date =
      this.getMonday(
        new Date()
      );


  // =====================================================
  // AGENDA REAL DEL BARBERO
  // =====================================================

  @Input()
  agenda:
    BarberWeeklyAgenda | null =
      null;


  // =====================================================
  // ESTADOS AGENDA
  // =====================================================

  @Input()
  loadingAgenda =
    false;


  @Input()
  agendaError =
    '';


  // =====================================================
  // OUTPUTS
  // =====================================================

  @Output()
  bookingSelected =
    new EventEmitter<
      AdminBookingItem
    >();


  @Output()
  previousWeek =
    new EventEmitter<void>();


  @Output()
  nextWeek =
    new EventEmitter<void>();


  @Output()
  currentWeek =
    new EventEmitter<void>();


  // =====================================================
  // CONFIGURACIÓN CALENDARIO
  // =====================================================

  readonly startHour =
    7;


  readonly endHour =
    21;


  readonly hourHeight =
    72;


  // =====================================================
  // HORAS
  // =====================================================

  get hours():
    number[] {

    const result:
      number[] =
        [];


    for (
      let hour =
        this.startHour;
      hour <
        this.endHour;
      hour++
    ) {

      result.push(
        hour
      );

    }


    return result;

  }


  // =====================================================
  // DÍAS DE LA SEMANA
  // =====================================================

  get days():
    CalendarDay[] {

    const result:
      CalendarDay[] =
        [];


    for (
      let index = 0;
      index < 7;
      index++
    ) {

      const date =
        new Date(
          this.weekStart
        );


      date.setDate(
        this.weekStart.getDate()
        +
        index
      );


      result.push({

        date,

        isoDate:
          this.toIsoDate(
            date
          ),

        dayName:
          new Intl
            .DateTimeFormat(
              'es-CO',
              {
                weekday:
                  'short'
              }
            )
            .format(
              date
            ),

        dayNumber:
          new Intl
            .DateTimeFormat(
              'es-CO',
              {
                day:
                  '2-digit'
              }
            )
            .format(
              date
            ),

        monthName:
          new Intl
            .DateTimeFormat(
              'es-CO',
              {
                month:
                  'short'
              }
            )
            .format(
              date
            ),

        isToday:
          this.toIsoDate(
            date
          )
          ===
          this.toIsoDate(
            new Date()
          )

      });

    }


    return result;

  }


  // =====================================================
  // AGENDA DE UN DÍA
  // =====================================================

  getAgendaDay(
    day:
      CalendarDay
  ):
    BarberAgendaDay | null {

    if (
      !this.agenda
    ) {

      return null;

    }


    return (
      this.agenda.days
        .find(
          agendaDay =>
            agendaDay.date ===
            day.isoDate
        )
      ??
      null
    );

  }


  // =====================================================
  // BARBERÍA ABIERTA
  // =====================================================

  isBarbershopOpen(
    day:
      CalendarDay
  ): boolean {

    const agendaDay =
      this.getAgendaDay(
        day
      );


    return (
      agendaDay?.is_barbershop_open
      ??
      false
    );

  }


  // =====================================================
  // BARBERO TRABAJA
  // =====================================================

  isBarberWorking(
    day:
      CalendarDay
  ): boolean {

    const agendaDay =
      this.getAgendaDay(
        day
      );


    return (
      agendaDay?.is_working
      ??
      false
    );

  }


  // =====================================================
  // INICIO DE JORNADA
  // =====================================================

  getWorkingTop(
    day:
      CalendarDay
  ): number {

    const agendaDay =
      this.getAgendaDay(
        day
      );


    if (
      !agendaDay
      ||
      !agendaDay.is_working
      ||
      !agendaDay.start_time
    ) {

      return 0;

    }


    return this.getTimeTop(
      agendaDay.start_time
    );

  }


  // =====================================================
  // ALTURA DE JORNADA
  // =====================================================

  getWorkingHeight(
    day:
      CalendarDay
  ): number {

    const agendaDay =
      this.getAgendaDay(
        day
      );


    if (
      !agendaDay
      ||
      !agendaDay.is_working
      ||
      !agendaDay.start_time
      ||
      !agendaDay.end_time
    ) {

      return 0;

    }


    return this.getTimeRangeHeight(
      agendaDay.start_time,
      agendaDay.end_time
    );

  }


  // =====================================================
  // DESCANSOS DEL DÍA
  // =====================================================

  getBreaksForDay(
    day:
      CalendarDay
  ):
    AgendaBreak[] {

    const agendaDay =
      this.getAgendaDay(
        day
      );


    if (
      !agendaDay
    ) {

      return [];

    }


    return (
      agendaDay.breaks
      ??
      []
    );

  }


  // =====================================================
  // POSICIÓN DESCANSO
  // =====================================================

  getBreakTop(
    breakItem:
      AgendaBreak
  ): number {

    return this.getTimeTop(
      breakItem.start_time
    );

  }


  // =====================================================
  // ALTURA DESCANSO
  // =====================================================

  getBreakHeight(
    breakItem:
      AgendaBreak
  ): number {

    return Math.max(
      24,
      this.getTimeRangeHeight(
        breakItem.start_time,
        breakItem.end_time
      )
    );

  }


  // =====================================================
  // BLOQUEOS DEL DÍA
  // =====================================================

  getBlocksForDay(
    day:
      CalendarDay
  ):
    AgendaBlock[] {

    const agendaDay =
      this.getAgendaDay(
        day
      );


    if (
      !agendaDay
    ) {

      return [];

    }


    return (
      agendaDay.blocks
      ??
      []
    );

  }


  // =====================================================
  // POSICIÓN BLOQUEO
  // =====================================================

  getBlockTop(
    block:
      AgendaBlock,
    day:
      CalendarDay
  ): number {

    const start =
      new Date(
        block.start_at
      );


    const dayStart =
      new Date(
        `${day.isoDate}T00:00:00`
      );


    const dayEnd =
      new Date(
        `${day.isoDate}T23:59:59`
      );


    const effectiveStart =
      start < dayStart
        ? dayStart
        : start > dayEnd
          ? dayEnd
          : start;


    return this.getDateTop(
      effectiveStart
    );

  }


  // =====================================================
  // ALTURA BLOQUEO
  // =====================================================

  getBlockHeight(
    block:
      AgendaBlock,
    day:
      CalendarDay
  ): number {

    const start =
      new Date(
        block.start_at
      );


    const end =
      new Date(
        block.end_at
      );


    const dayStart =
      new Date(
        `${day.isoDate}T00:00:00`
      );


    const nextDay =
      new Date(
        dayStart
      );


    nextDay.setDate(
      nextDay.getDate()
      +
      1
    );


    const effectiveStart =
      start < dayStart
        ? dayStart
        : start;


    const effectiveEnd =
      end > nextDay
        ? nextDay
        : end;


    const minutes =
      Math.max(
        0,
        (
          effectiveEnd.getTime()
          -
          effectiveStart.getTime()
        )
        /
        60000
      );


    return Math.max(
      24,
      (
        minutes
        /
        60
      )
      *
      this.hourHeight
    );

  }


  // =====================================================
  // FORMATEAR HORARIO AGENDA
  // =====================================================

  formatAgendaTime(
    value:
      string | null | undefined
  ): string {

    if (
      !value
    ) {

      return '—';

    }


    const parts =
      value
        .split(
          ':'
        );


    const hour =
      Number(
        parts[0]
      );


    const minute =
      Number(
        parts[1]
        ??
        0
      );


    if (
      Number.isNaN(
        hour
      )
      ||
      Number.isNaN(
        minute
      )
    ) {

      return value;

    }


    const date =
      new Date();


    date.setHours(
      hour,
      minute,
      0,
      0
    );


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
  // FORMATEAR BLOQUEO
  // =====================================================

  formatBlockTime(
    value:
      string
  ): string {

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
  // RESERVAS DE UN DÍA
  // =====================================================

  getBookingsForDay(
    day:
      CalendarDay
  ):
    AdminBookingItem[] {

    return (
      this.bookings
        .filter(
          booking =>
            this.getBookingDate(
              booking
            )
            ===
            day.isoDate
        )
        .sort(
          (
            first,
            second
          ) =>
            new Date(
              first.start_at
            )
              .getTime()
            -
            new Date(
              second.start_at
            )
              .getTime()
        )
    );

  }


  // =====================================================
  // POSICIÓN VERTICAL RESERVA
  // =====================================================

  getBookingTop(
    booking:
      AdminBookingItem
  ): number {

    const start =
      new Date(
        booking.start_at
      );


    return this.getDateTop(
      start
    );

  }


  // =====================================================
  // ALTURA DE RESERVA
  // =====================================================

  getBookingHeight(
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


    const minutes =
      Math.max(
        15,
        Math.round(
          (
            end.getTime()
            -
            start.getTime()
          )
          /
          60000
        )
      );


    return Math.max(
      38,
      (
        minutes
        /
        60
      )
      *
      this.hourHeight
    );

  }


  // =====================================================
  // ALTURA TOTAL DEL DÍA
  // =====================================================

  get calendarHeight():
    number {

    return (
      (
        this.endHour
        -
        this.startHour
      )
      *
      this.hourHeight
    );

  }


  // =====================================================
  // ABRIR RESERVA
  // =====================================================

  openBooking(
    booking:
      AdminBookingItem
  ): void {

    this.bookingSelected.emit(
      booking
    );

  }


  // =====================================================
  // FORMATEAR HORA
  // =====================================================

  formatHour(
    hour:
      number
  ): string {

    const date =
      new Date();


    date.setHours(
      hour,
      0,
      0,
      0
    );


    return new Intl
      .DateTimeFormat(
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
  // HORA RESERVA
  // =====================================================

  formatBookingTime(
    value:
      string
  ): string {

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
        new Date(
          value
        )
      );

  }


  // =====================================================
  // MONEDA
  // =====================================================

  formatCurrency(
    value:
      number | null | undefined
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
  // ESTADO
  // =====================================================

  statusClass(
    status:
      string
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

        return 'default';

    }

  }


  // =====================================================
  // POSICIÓN DESDE TIME
  // =====================================================

  private getTimeTop(
    value:
      string
  ): number {

    const minutes =
      this.timeToMinutes(
        value
      );


    const calendarStart =
      this.startHour
      *
      60;


    const difference =
      minutes
      -
      calendarStart;


    const position =
      (
        difference
        /
        60
      )
      *
      this.hourHeight;


    return this.clampTop(
      position
    );

  }


  // =====================================================
  // POSICIÓN DESDE DATE
  // =====================================================

  private getDateTop(
    date:
      Date
  ): number {

    const totalMinutes =
      (
        date.getHours()
        *
        60
      )
      +
      date.getMinutes();


    const calendarStart =
      this.startHour
      *
      60;


    const difference =
      totalMinutes
      -
      calendarStart;


    const position =
      (
        difference
        /
        60
      )
      *
      this.hourHeight;


    return this.clampTop(
      position
    );

  }


  // =====================================================
  // ALTURA ENTRE DOS HORAS
  // =====================================================

  private getTimeRangeHeight(
    start:
      string,
    end:
      string
  ): number {

    const startMinutes =
      this.timeToMinutes(
        start
      );


    const endMinutes =
      this.timeToMinutes(
        end
      );


    const calendarStart =
      this.startHour
      *
      60;


    const calendarEnd =
      this.endHour
      *
      60;


    const effectiveStart =
      Math.max(
        startMinutes,
        calendarStart
      );


    const effectiveEnd =
      Math.min(
        endMinutes,
        calendarEnd
      );


    const minutes =
      Math.max(
        0,
        effectiveEnd
        -
        effectiveStart
      );


    return (
      minutes
      /
      60
    )
    *
    this.hourHeight;

  }


  // =====================================================
  // TIME A MINUTOS
  // =====================================================

  private timeToMinutes(
    value:
      string
  ): number {

    const parts =
      value
        .split(
          ':'
        );


    const hour =
      Number(
        parts[0]
        ??
        0
      );


    const minute =
      Number(
        parts[1]
        ??
        0
      );


    return (
      hour
      *
      60
    )
    +
    minute;

  }


  // =====================================================
  // LIMITAR POSICIÓN AL CALENDARIO
  // =====================================================

  private clampTop(
    value:
      number
  ): number {

    return Math.max(
      0,
      Math.min(
        value,
        this.calendarHeight
      )
    );

  }


  // =====================================================
  // FECHA RESERVA
  // =====================================================

  private getBookingDate(
    booking:
      AdminBookingItem
  ): string {

    return this.toIsoDate(
      new Date(
        booking.start_at
      )
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

}
