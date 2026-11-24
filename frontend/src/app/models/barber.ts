export interface BarberItem {

  id: number;

  user_id: number;

  barbershop_id: number;

  first_name: string;

  last_name: string;

  bio: string | null;

  years_experience: number | null;

  accepts_home_service: boolean;

  is_active: boolean;

  service_ids: number[];

  created_at: string;

  updated_at: string;

}
