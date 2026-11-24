export interface AgendaBreak {

  id: number;

  name: string;

  start_time: string;

  end_time: string;

}


export interface AgendaBlock {

  id: number;

  start_at: string;

  end_at: string;

  reason:
    string | null;

}


export interface BarberAgendaDay {

  date: string;

  day_of_week: number;


  // =====================================================
  // BARBERÍA
  // =====================================================

  is_barbershop_open: boolean;

  barbershop_open_time:
    string | null;

  barbershop_close_time:
    string | null;


  // =====================================================
  // BARBERO
  // =====================================================

  is_working: boolean;

  start_time:
    string | null;

  end_time:
    string | null;


  // =====================================================
  // DESCANSOS Y BLOQUEOS
  // =====================================================

  breaks:
    AgendaBreak[];

  blocks:
    AgendaBlock[];

}


export interface BarberWeeklyAgenda {

  barber_id: number;

  barbershop_id: number;

  week_start: string;

  week_end: string;

  days:
    BarberAgendaDay[];

}
