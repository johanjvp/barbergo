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
  BarberWeeklyAgenda
} from '../models/barber-weekly-agenda';


@Injectable({
  providedIn: 'root'
})
export class ScheduleService {


  // =====================================================
  // DEPENDENCIAS
  // =====================================================

  private readonly http =
    inject(
      HttpClient
    );


  // =====================================================
  // API
  // =====================================================

  private readonly apiUrl =
    'http://127.0.0.1:8000/api/v1';


  // =====================================================
  // AGENDA SEMANAL BARBERO
  // =====================================================

  getWeeklyAgenda(
    barberId: number,
    weekStart: string
  ): Observable<BarberWeeklyAgenda> {

    const params =
      new HttpParams()
        .set(
          'week_start',
          weekStart
        );


    return this.http.get<BarberWeeklyAgenda>(
      `${this.apiUrl}/barbers/${barberId}/weekly-agenda`,
      {
        params
      }
    );

  }

}
