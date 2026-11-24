export interface BookingCreate {

  barber_id: number;

  service_id: number;

  start_at: string;

  customer_notes: string | null;

}


export interface BookingResponse {

  id: number;

  client_user_id: number;

  barbershop_id: number;

  barber_id: number;

  service_id: number;

  status_id: number;

  status_code: string;

  start_at: string;

  end_at: string;

  service_price: number | string;

  customer_notes: string | null;

  barber_notes: string | null;

  created_at: string;

  updated_at: string;

}


/*
 * Se usa únicamente para conservar
 * una reserva cuando el usuario todavía
 * no ha iniciado sesión.
 */

export interface PendingBooking {

  barbershop_id: number;

  service_id: number;

  barber_id: number;

  date: string;

  start_time: string;

  end_time: string;

}
