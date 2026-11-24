export interface BarberAgendaProfile {
  id: number;
  user_id: number;

  first_name: string;
  last_name: string;

  barbershop_id: number;
  barbershop_name: string;

  barbershop_address: string;
  barbershop_city: string;

  is_active: boolean;
}


export interface BarberAgendaBooking {
  id: number;

  client_user_id: number;
  client_name: string;
  client_phone: string | null;

  service_id: number;
  service_name: string;

  duration_minutes: number;
  service_price: number;

  status_id: number;
  status_code: string;
  status_name: string;

  start_at: string;
  end_at: string;

  customer_notes: string | null;
  barber_notes: string | null;
}


export interface BarberAgendaResponse {
  barber: BarberAgendaProfile;

  date_from: string;
  date_to: string;

  total: number;

  items: BarberAgendaBooking[];
}
