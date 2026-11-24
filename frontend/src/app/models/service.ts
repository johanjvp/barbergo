export interface ServiceItem {

  id: number;

  barbershop_id: number;

  name: string;

  description: string | null;

  price: number | string;

  duration_minutes: number;

  is_vip: boolean;

  home_service_allowed: boolean;

  is_active: boolean;

  created_at: string;

  updated_at: string;

}
