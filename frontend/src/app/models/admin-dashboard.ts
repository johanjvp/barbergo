export interface AdminGrowthPoint {
  date: string;
  total: number;
}


export interface AdminTopBarbershop {
  barbershop_id: number;
  barbershop_name: string;
  bookings_count: number;
  reserved_value: number;
}


export interface AdminTopService {
  service_id: number;
  service_name: string;
  bookings_count: number;
  booked_value: number;
}


export interface AdminTopBarber {
  barber_id: number;
  bookings_count: number;
  booked_value: number;
}


export interface AdminDashboardResponse {

  users: {
    total: number;
    today: number;
    this_week: number;
    this_month: number;
    unique_customers: number;
    returning_customers: number;
    returning_customer_rate: number;
  };


  barbershops: {
    total: number;
    active: number;
    inactive: number;
    new_this_month: number;
  };


  bookings: {
    total: number;
    today: number;
    this_week: number;
    this_month: number;

    pending: number;
    confirmed: number;
    in_progress: number;
    completed: number;

    cancelled: number;
    cancelled_by_customer: number;
    cancelled_by_barber: number;

    no_show: number;
    rejected: number;

    cancellation_rate: number;
    no_show_rate: number;
  };


  financial: {
    reserved_value: number;
    reserved_value_today: number;
    reserved_value_this_month: number;
    completed_value_this_month: number;
    average_ticket: number;
  };


  financial_simulation: {
    is_simulation: boolean;
    currency: string;

    commission_rate: number;
    commission_percentage: number;

    gross_booking_value: number;
    completed_value: number;

    projected_platform_revenue: number;
    completed_platform_revenue: number;

    projected_barbershop_payout: number;
    completed_barbershop_payout: number;

    projected_platform_revenue_this_month: number;
    projected_barbershop_payout_this_month: number;

    completed_platform_revenue_this_month: number;
    completed_barbershop_payout_this_month: number;

    cancelled_value: number;
    no_show_value: number;
    rejected_value: number;

    lost_value: number;
    lost_platform_revenue: number;
  };


  growth: {
    users: AdminGrowthPoint[];
    bookings: AdminGrowthPoint[];
  };


  rankings: {
    top_barbershops: AdminTopBarbershop[];
    top_services: AdminTopService[];
    top_barbers: AdminTopBarber[];
  };

}
