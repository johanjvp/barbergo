export interface AvailabilitySlot {
  start_time: string;
  end_time: string;
}


export interface AvailabilityResponse {
  barber_id: number;
  service_id: number;

  date: string;

  duration_minutes: number;

  available: boolean;

  slots: AvailabilitySlot[];
}
