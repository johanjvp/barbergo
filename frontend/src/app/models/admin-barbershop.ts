export interface AdminBarbershopItem {

  id: number;

  name: string;

  city:
    string | null;

  neighborhood:
    string | null;

  address:
    string | null;

  phone:
    string | null;

  email:
    string | null;

  is_active:
    boolean;

  created_at:
    string | null;

  bookings_count:
    number;

  completed_bookings:
    number;

  cancelled_bookings:
    number;

  reserved_value:
    number;

  average_ticket:
    number;

}


/* =========================================================
   LISTADO DE BARBERÍAS
   ========================================================= */

export interface AdminBarbershopListResponse {

  total: number;

  limit: number;

  offset: number;

  items:
    AdminBarbershopItem[];

}


/* =========================================================
   CAMBIO DE ESTADO
   ========================================================= */

export interface AdminBarbershopStatusResponse {

  id: number;

  name: string;

  is_active: boolean;

}


/* =========================================================
   BARBERO DE UNA BARBERÍA
   ========================================================= */

export interface AdminBarbershopBarber {

  id: number;

  user_id:
    number | null;

  first_name:
    string | null;

  last_name:
    string | null;

  full_name:
    string;

  phone:
    string | null;

  email:
    string | null;

  bio:
    string | null;

  years_experience:
    number | null;

  accepts_home_service:
    boolean;

  is_active:
    boolean;

}


/* =========================================================
   MÉTRICAS DEL DETALLE
   ========================================================= */

export interface AdminBarbershopDetailMetrics {

  bookings_count:
    number;

  completed_bookings:
    number;

  cancelled_bookings:
    number;

  reserved_value:
    number;

  average_ticket:
    number;

  active_barbers:
    number;

}


export interface AdminBarbershopDetail {

  id: number;

  name: string;

  city:
    string | null;

  neighborhood:
    string | null;

  address:
    string | null;

  phone:
    string | null;

  email:
    string | null;

  is_active:
    boolean;

  created_at:
    string | null;

  metrics:
    AdminBarbershopDetailMetrics;

}


/* =========================================================
   DETALLE ADMINISTRATIVO DE BARBERÍA
   ========================================================= */

export interface AdminBarbershopDetail {

  id: number;

  name: string;

  description:
    string | null;

  city:
    string | null;

  neighborhood:
    string | null;

  address:
    string | null;

  phone:
    string | null;

  email:
    string | null;

  is_active:
    boolean;

  created_at:
    string | null;

  updated_at:
    string | null;

  requires_manual_confirmation:
    boolean;

  metrics:
    AdminBarbershopDetailMetrics;

  barbers:
    AdminBarbershopBarber[];

}
