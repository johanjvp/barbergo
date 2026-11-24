export type AdminUserRole =
  'CLIENT'
  |
  'BARBER'
  |
  'BARBERSHOP_ADMIN'
  |
  'PLATFORM_ADMIN';


export interface AdminUserItem {

  id: number;

  first_name:
    string | null;

  last_name:
    string | null;

  full_name:
    string;

  email:
    string;

  phone:
    string | null;

  email_verified:
    boolean;

  phone_verified:
    boolean;

  is_active:
    boolean;

  roles:
    string[];

  created_at:
    string | null;

  updated_at:
    string | null;

  bookings_count:
    number;

  completed_bookings:
    number;

  cancelled_bookings:
    number;

  booked_value:
    number;

  last_booking_at:
    string | null;

}


export interface AdminUserSummary {

  total: number;

  active: number;

  inactive: number;

  new_this_month: number;

  clients: number;

  barbers: number;

  barbershop_admins: number;

  platform_admins: number;

}


export interface AdminUserListResponse {

  summary:
    AdminUserSummary;

  total: number;

  limit: number;

  offset: number;

  items:
    AdminUserItem[];

}

export interface AdminUserStatusResponse {
  id: number;
  is_active: boolean;
  message: string;
}
