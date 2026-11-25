import { API_URL } from '../core/api';
import {
  inject,
  Injectable
} from '@angular/core';

import {
  HttpClient
} from '@angular/common/http';

import {
  Observable
} from 'rxjs';

import {
  BookingCreate,
  BookingResponse
} from '../models/booking';


@Injectable({
  providedIn: 'root'
})
export class BookingService {

  private readonly http =
    inject(HttpClient);


  private readonly apiUrl =
    `${API_URL}/bookings`;


  // =====================================================
  // CREAR RESERVA
  // =====================================================

  create(
    data: BookingCreate
  ): Observable<BookingResponse> {

    return this.http.post<BookingResponse>(
      this.apiUrl,
      data
    );

  }


  // =====================================================
  // MIS RESERVAS
  // =====================================================

  getMyBookings():
    Observable<BookingResponse[]> {

    return this.http.get<BookingResponse[]>(
      `${this.apiUrl}/me`
    );

  }


  // =====================================================
  // CANCELAR RESERVA COMO CLIENTE
  // =====================================================

  cancel(
    bookingId: number
  ): Observable<BookingResponse> {

    return this.http.patch<BookingResponse>(
      `${this.apiUrl}/${bookingId}/cancel`,
      {}
    );

  }

}
