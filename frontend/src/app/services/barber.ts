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
  BarberItem
} from '../models/barber';


@Injectable({
  providedIn: 'root'
})
export class BarberService {

  private readonly http =
    inject(HttpClient);


  private readonly apiUrl =
    'http://127.0.0.1:8000/api/v1';


  // =====================================================
  // LISTAR BARBEROS DE UNA BARBERÍA
  // =====================================================

  getByBarbershop(
    barbershopId: number
  ): Observable<BarberItem[]> {

    return this.http
      .get<BarberItem[]>(
        `${this.apiUrl}/barbershops/${barbershopId}/barbers`
      );

  }

}
