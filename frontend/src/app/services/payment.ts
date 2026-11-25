import { API_URL } from '../core/api';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export type PaymentMethodCode = 'CASH' | 'BANK_TRANSFER' | 'DEPOSIT' | 'NEQUI' | 'DAVIPLATA';

export interface PaymentMethod {
  method: PaymentMethodCode;
  bank_name: string | null;
  account_type: string | null;
  account_number: string | null;
  account_holder: string | null;
  holder_document: string | null;
  instructions: string | null;
  is_active: boolean;
}

export interface PaymentRow {
  id: number;
  start_at: string;
  total: number;
  payment_method: PaymentMethodCode;
  payment_status: 'PENDING' | 'REPORTED' | 'PAID';
  payment_reference: string | null;
  payment_reported_at: string | null;
  client_name: string | null;
  service_name: string;
  booking_status: string;
}

export const PAYMENT_LABELS: Record<PaymentMethodCode, string> = {
  CASH: 'Efectivo',
  BANK_TRANSFER: 'Transferencia bancaria',
  DEPOSIT: 'Consignación',
  NEQUI: 'Nequi',
  DAVIPLATA: 'Daviplata'
};

export const PAYMENT_HINTS: Record<PaymentMethodCode, string> = {
  CASH: 'Pagas al recibir el servicio',
  BANK_TRANSFER: 'Desde tu app o banca en línea',
  DEPOSIT: 'En sucursal o corresponsal',
  NEQUI: 'Envía a un número Nequi',
  DAVIPLATA: 'Envía a un número Daviplata'
};

@Injectable({ providedIn: 'root' })
export class PaymentApi {
  private readonly http = inject(HttpClient);
  private readonly base = API_URL;

  /** Métodos que acepta una barbería (público). */
  forBarbershop(barbershopId: number): Observable<PaymentMethod[]> {
    return this.http.get<PaymentMethod[]>(`${this.base}/barbershops/${barbershopId}/payment-methods`);
  }

  // ---- barbería ----
  getSettings(barbershopId: number): Observable<PaymentMethod[]> {
    return this.http.get<PaymentMethod[]>(`${this.base}/barbershop-settings/${barbershopId}/payment-methods`);
  }

  saveSettings(barbershopId: number, methods: PaymentMethod[]): Observable<PaymentMethod[]> {
    return this.http.put<PaymentMethod[]>(`${this.base}/barbershop-settings/${barbershopId}/payment-methods`, { methods });
  }

  listPayments(barbershopId: number, state: 'OPEN' | 'PAID' | 'ALL' = 'OPEN'): Observable<PaymentRow[]> {
    return this.http.get<PaymentRow[]>(`${this.base}/barbershop-settings/${barbershopId}/payments`, {
      params: new HttpParams().set('state', state)
    });
  }

  setStatus(barbershopId: number, bookingId: number, status: 'PAID' | 'PENDING'): Observable<unknown> {
    return this.http.patch(`${this.base}/barbershop-settings/${barbershopId}/payments/${bookingId}`, { status });
  }

  // ---- cliente ----
  reportReference(bookingId: number, reference: string): Observable<unknown> {
    return this.http.post(`${this.base}/bookings/${bookingId}/payment-reference`, { reference });
  }

  reportGuestReference(token: string, reference: string): Observable<unknown> {
    return this.http.post(`${this.base}/guest/bookings/${encodeURIComponent(token)}/payment-reference`, { reference });
  }
}
