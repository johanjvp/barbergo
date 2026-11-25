import { API_URL } from '../core/api';
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
  BarberAgendaResponse
} from '../models/barber-agenda';


@Injectable({
  providedIn: 'root'
})
export class BarberAgendaService {


  private readonly http =
    inject(
      HttpClient
    );


  private readonly apiUrl =
    `${API_URL}/barber-agenda`;


  // =====================================================
  // MI AGENDA
  // =====================================================

  getMyAgenda(
    dateFrom?: string,
    dateTo?: string
  ): Observable<BarberAgendaResponse> {

    let params =
      new HttpParams();


    if (
      dateFrom
    ) {

      params =
        params.set(
          'date_from',
          dateFrom
        );

    }


    if (
      dateTo
    ) {

      params =
        params.set(
          'date_to',
          dateTo
        );

    }


    return this.http
      .get<BarberAgendaResponse>(
        `${this.apiUrl}/me`,
        {
          params
        }
      );

  }

}
