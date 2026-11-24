// =====================================================
// CONFIGURACIÓN DE BARBERÍA
// =====================================================

export interface BarbershopSettings {

  // ===================================================
  // IDENTIFICACIÓN
  // ===================================================

  id: number;

  barbershop_id: number;

  barbershop_name: string;

  barbershop_is_active: boolean;


  // ===================================================
  // CONTROL GENERAL
  // ===================================================

  bookings_enabled: boolean;


  // ===================================================
  // RESERVAS
  // ===================================================

  auto_confirm_bookings: boolean;

  allow_same_day_booking: boolean;

  min_booking_notice_minutes: number;

  max_booking_days_ahead: number;

  booking_interval_minutes: number;

  buffer_between_bookings_minutes: number;

  allow_overbooking: boolean;


  // ===================================================
  // CANCELACIONES
  // ===================================================

  allow_customer_cancellation: boolean;

  cancellation_limit_minutes: number;


  // ===================================================
  // REPROGRAMACIONES
  // ===================================================

  allow_reschedule: boolean;

  reschedule_limit_minutes: number;


  // ===================================================
  // SELECCIÓN DE BARBERO
  // ===================================================

  customer_can_choose_barber: boolean;

  allow_any_available_barber: boolean;


  // ===================================================
  // CLIENTES
  // ===================================================

  require_customer_account: boolean;

  require_customer_phone: boolean;

  allow_customer_notes: boolean;


  // ===================================================
  // PERMISOS DEL BARBERO
  // ===================================================

  barber_can_confirm_bookings: boolean;

  barber_can_cancel_bookings: boolean;

  barber_can_start_service: boolean;

  barber_can_complete_service: boolean;

  barber_can_block_schedule: boolean;

  barber_can_edit_schedule: boolean;


  // ===================================================
  // OPERACIÓN
  // ===================================================

  tolerance_minutes: number;


  // ===================================================
  // NOTIFICACIONES
  // ===================================================

  notify_barber_new_booking: boolean;

  notify_barber_cancellation: boolean;

  notify_customer_confirmation: boolean;

  notify_customer_cancellation: boolean;

  send_booking_reminders: boolean;

  reminder_minutes_before: number;


  // ===================================================
  // AUDITORÍA
  // ===================================================

  created_at: string | null;

  updated_at: string | null;
}


// =====================================================
// ACTUALIZAR CONFIGURACIÓN
// =====================================================

export interface BarbershopSettingsUpdate {

  // ===================================================
  // CONTROL GENERAL
  // ===================================================

  bookings_enabled?: boolean;


  // ===================================================
  // RESERVAS
  // ===================================================

  auto_confirm_bookings?: boolean;

  allow_same_day_booking?: boolean;

  min_booking_notice_minutes?: number;

  max_booking_days_ahead?: number;

  booking_interval_minutes?: number;

  buffer_between_bookings_minutes?: number;

  allow_overbooking?: boolean;


  // ===================================================
  // CANCELACIONES
  // ===================================================

  allow_customer_cancellation?: boolean;

  cancellation_limit_minutes?: number;


  // ===================================================
  // REPROGRAMACIONES
  // ===================================================

  allow_reschedule?: boolean;

  reschedule_limit_minutes?: number;


  // ===================================================
  // SELECCIÓN DE BARBERO
  // ===================================================

  customer_can_choose_barber?: boolean;

  allow_any_available_barber?: boolean;


  // ===================================================
  // CLIENTES
  // ===================================================

  require_customer_account?: boolean;

  require_customer_phone?: boolean;

  allow_customer_notes?: boolean;


  // ===================================================
  // PERMISOS DEL BARBERO
  // ===================================================

  barber_can_confirm_bookings?: boolean;

  barber_can_cancel_bookings?: boolean;

  barber_can_start_service?: boolean;

  barber_can_complete_service?: boolean;

  barber_can_block_schedule?: boolean;

  barber_can_edit_schedule?: boolean;


  // ===================================================
  // OPERACIÓN
  // ===================================================

  tolerance_minutes?: number;


  // ===================================================
  // NOTIFICACIONES
  // ===================================================

  notify_barber_new_booking?: boolean;

  notify_barber_cancellation?: boolean;

  notify_customer_confirmation?: boolean;

  notify_customer_cancellation?: boolean;

  send_booking_reminders?: boolean;

  reminder_minutes_before?: number;
}


// =====================================================
// CONFIRMACIÓN AUTOMÁTICA
// =====================================================

export interface AutoConfirmBookingUpdate {

  enabled: boolean;
}


// =====================================================
// RESPUESTA DE ACTUALIZACIÓN
// =====================================================

export interface BarbershopSettingsActionResponse {

  barbershop_id: number;

  updated: boolean;

  message: string;

  settings: BarbershopSettings;
}
