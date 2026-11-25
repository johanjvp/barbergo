import { API_URL } from '../core/api';
import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { BookingResponse, HomeAddressValue } from '../models/booking';
import { PaymentMethod, PaymentMethodCode } from './payment';

export interface GuestBookingPayload {
  barber_id: number;
  service_id: number;
  start_at: string;
  customer_notes: string | null;
  booking_type: 'IN_SHOP' | 'HOME';
  home: HomeAddressValue | null;
  payment_method: PaymentMethodCode | null;
  name: string;
  email: string;
  phone: string;
  code: string;
  accept_terms: boolean;
}

export interface GuestBookingCreated extends BookingResponse {
  manage_token: string;
}

export interface GuestBookingView {
  id: number;
  status_code: string;
  start_at: string;
  end_at: string;
  guest_name: string | null;
  barbershop_name: string;
  barbershop_address: string | null;
  barbershop_phone: string | null;
  service_name: string;
  barber_name: string;
  service_price: number | string;
  home_fee: number | string;
  booking_type: 'IN_SHOP' | 'HOME';
  home_address: string | null;
  can_cancel: boolean;
  cancel_deadline: string | null;
  cancellation_hours_before: number;
  payment_method: PaymentMethodCode | null;
  payment_status: 'PENDING' | 'REPORTED' | 'PAID';
  payment_reference: string | null;
  payment_details: Partial<PaymentMethod> | null;
}

@Injectable({ providedIn: 'root' })
export class GuestBookingService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${API_URL}/guest`;

  requestCode(email: string): Observable<{ sent: boolean; expires_in_minutes: number }> {
    return this.http.post<{ sent: boolean; expires_in_minutes: number }>(
      `${this.apiUrl}/verification-code`,
      { email }
    );
  }

  create(payload: GuestBookingPayload): Observable<GuestBookingCreated> {
    return this.http.post<GuestBookingCreated>(`${this.apiUrl}/bookings`, payload);
  }

  get(token: string): Observable<GuestBookingView> {
    return this.http.get<GuestBookingView>(`${this.apiUrl}/bookings/${encodeURIComponent(token)}`);
  }

  cancel(token: string): Observable<GuestBookingView> {
    return this.http.post<GuestBookingView>(
      `${this.apiUrl}/bookings/${encodeURIComponent(token)}/cancel`,
      {}
    );
  }
}
