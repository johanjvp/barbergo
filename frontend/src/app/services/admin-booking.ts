import {
  Injectable,
  inject
} from '@angular/core';

import {
  HttpClient,
  HttpParams
} from '@angular/common/http';

import {
  Observable
} from 'rxjs';

import {
  AdminBookingCancelResponse,
  AdminBookingConfirmResponse,
  AdminBookingCompleteResponse,
  AdminBookingListResponse
} from '../models/admin-booking';


@Injectable({
  providedIn: 'root'
})
export class AdminBookingService {

  private readonly http =
    inject(
      HttpClient
    );


  private readonly apiUrl =
    'http://127.0.0.1:8000/api/v1/admin/bookings';


  // =====================================================
  // LISTAR RESERVAS
  // =====================================================

  getAll(
    search = '',
    statusFilter = 'all',
    barbershopId: number | null = null,
    barberId: number | null = null,
    dateFrom = '',
    dateTo = '',
    limit = 20,
    offset = 0
  ): Observable<AdminBookingListResponse> {

    let params =
      new HttpParams()
        .set(
          'status_filter',
          statusFilter
        )
        .set(
          'limit',
          String(
            limit
          )
        )
        .set(
          'offset',
          String(
            offset
          )
        );


    // =================================================
    // BÚSQUEDA
    // =================================================

    if (
      search.trim()
    ) {

      params =
        params.set(
          'search',
          search.trim()
        );

    }


    // =================================================
    // BARBERÍA
    // =================================================

    if (
      barbershopId !==
        null
      &&
      barbershopId >
        0
    ) {

      params =
        params.set(
          'barbershop_id',
          String(
            barbershopId
          )
        );

    }


    // =================================================
    // BARBERO
    // =================================================

    if (
      barberId !==
        null
      &&
      barberId >
        0
    ) {

      params =
        params.set(
          'barber_id',
          String(
            barberId
          )
        );

    }


    // =================================================
    // FECHA DESDE
    // =================================================

    if (
      dateFrom
    ) {

      params =
        params.set(
          'date_from',
          dateFrom
        );

    }


    // =================================================
    // FECHA HASTA
    // =================================================

    if (
      dateTo
    ) {

      params =
        params.set(
          'date_to',
          dateTo
        );

    }


    // =================================================
    // CONSULTA
    // =================================================

    return this.http.get<
      AdminBookingListResponse
    >(
      this.apiUrl,
      {
        params
      }
    );

  }


  // =====================================================
  // CANCELAR RESERVA COMO ADMINISTRADOR
  // =====================================================

  cancelBooking(
    bookingId: number
  ): Observable<AdminBookingCancelResponse> {

    return this.http.patch<
      AdminBookingCancelResponse
    >(
      `${this.apiUrl}/${bookingId}/cancel`,
      {}
    );

  }


  // =====================================================
  // CONFIRMAR RESERVA COMO ADMINISTRADOR
  // =====================================================

  confirmBooking(
    bookingId: number
  ): Observable<AdminBookingConfirmResponse> {

    return this.http.patch<
      AdminBookingConfirmResponse
    >(
      `${this.apiUrl}/${bookingId}/confirm`,
      {}
    );

  }


  // =====================================================
  // COMPLETAR RESERVA COMO ADMINISTRADOR
  // =====================================================

  completeBooking(
    bookingId: number
  ): Observable<AdminBookingCompleteResponse> {

    return this.http.patch<
      AdminBookingCompleteResponse
    >(
      `${this.apiUrl}/${bookingId}/complete`,
      {}
    );

  }

}
