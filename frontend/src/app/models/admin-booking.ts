export type AdminBookingStatus =
  | 'PENDING'
  | 'CONFIRMED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'CANCELLED_BY_CUSTOMER'
  | 'CANCELLED_BY_BARBER'
  | 'CANCELLED_BY_ADMIN'
  | 'REJECTED'
  | 'NO_SHOW';


export interface AdminBookingItem {

  id: number;

  client_user_id: number;

  client_first_name:
    string | null;

  client_last_name:
    string | null;

  client_full_name:
    string;

  client_email:
    string;

  client_phone:
    string | null;


  barbershop_id:
    number;

  barbershop_name:
    string;


  barber_id:
    number;

  barber_first_name:
    string | null;

  barber_last_name:
    string | null;

  barber_full_name:
    string;


  service_id:
    number;

  service_name:
    string;

  service_duration_minutes:
    number;


  status_id:
    number;

  status_code:
    AdminBookingStatus;

  status_name:
    string;


  start_at:
    string;

  end_at:
    string;


  service_price:
    number;


  customer_notes:
    string | null;

  barber_notes:
    string | null;


  created_at:
    string;

  updated_at:
    string | null;

}


export interface AdminBookingSummary {

  total:
    number;

  pending:
    number;

  confirmed:
    number;

  in_progress:
    number;

  completed:
    number;

  cancelled:
    number;

  rejected:
    number;

  no_show:
    number;

  today:
    number;

  reserved_value:
    number;

}


export interface AdminBookingListResponse {

  summary:
    AdminBookingSummary;

  total:
    number;

  limit:
    number;

  offset:
    number;

  items:
    AdminBookingItem[];

}


export interface AdminBookingCancelResponse {

  id:
    number;

  cancelled:
    boolean;

  status_id:
    number;

  status_code:
    'CANCELLED_BY_ADMIN';

  status_name:
    string;

  message:
    string;

}

export interface AdminBookingConfirmResponse {

  id:
    number;

  confirmed:
    boolean;

  status_id:
    number;

  status_code:
    'CONFIRMED';

  status_name:
    string;

  message:
    string;

}

export interface AdminBookingCompleteResponse {

  id:
    number;

  completed:
    boolean;

  status_id:
    number;

  status_code:
    'COMPLETED';

  status_name:
    string;

  message:
    string;

}
