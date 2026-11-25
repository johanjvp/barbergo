export type PaymentCode =
  | 'CASH'
  | 'BANK_TRANSFER'
  | 'DEPOSIT'
  | 'NEQUI'
  | 'DAVIPLATA';

export interface HomeAddressValue {
  address: string;
  latitude: number;
  longitude: number;
  access_notes: string | null;
}

export interface BookingCreate {
  barber_id: number;
  service_id: number;
  start_at: string;
  customer_notes: string | null;
  booking_type?: 'IN_SHOP' | 'HOME';
  home?: HomeAddressValue | null;
  payment_method?: PaymentCode | null;
}

export interface BookingResponse {
  id: number;
  client_user_id: number | null;
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
  guest_name?: string | null;
  guest_email?: string | null;
  booking_type?: 'IN_SHOP' | 'HOME';
  home_address?: string | null;
  home_latitude?: number | string | null;
  home_longitude?: number | string | null;
  home_access_notes?: string | null;
  home_fee?: number | string;
  payment_method?: string | null;
  payment_status?: string;
  payment_reference?: string | null;
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
