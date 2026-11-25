export interface BarbershopDiscoveryItem {
  id: number;

  name: string;
  description: string | null;

  address: string;
  neighborhood: string | null;

  city: string;
  department: string;

  latitude: number | null;
  longitude: number | null;

  phone: string | null;
  email: string | null;

  only_men: boolean;
  offers_vip: boolean;
  offers_home_service: boolean;

  starting_price: number | null;
  distance_km: number | null;
}


export interface BarbershopDiscoveryResponse {
  total: number;
  skip: number;
  limit: number;

  items: BarbershopDiscoveryItem[];
}

export interface BarbershopDetail {

  id: number;

  owner_user_id: number;

  name: string;

  description: string | null;

  address: string;

  neighborhood: string | null;

  city: string;

  department: string;

  latitude: number | string | null;

  longitude: number | string | null;

  phone: string | null;

  email: string | null;

  only_men: boolean;

  offers_vip: boolean;

  offers_home_service: boolean;

  requires_manual_confirmation: boolean;

  cancellation_hours_before: number;

  tolerance_minutes: number;

  is_active: boolean;
  home_service_status?: string;
  home_service_radius_km?: number | null;
  home_service_fee?: number;
  home_service_min_notice_hours?: number;
  home_service_zones?: string | null;

}
