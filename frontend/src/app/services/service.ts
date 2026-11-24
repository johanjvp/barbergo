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
  ServiceItem
} from '../models/service';


@Injectable({
  providedIn: 'root'
})
export class ServiceService {

  private readonly http =
    inject(HttpClient);


  private readonly apiUrl =
    'http://127.0.0.1:8000/api/v1';


  // =====================================================
  // LISTAR SERVICIOS DE UNA BARBERÍA
  // =====================================================

  getByBarbershop(
    barbershopId: number
  ): Observable<ServiceItem[]> {

    return this.http
      .get<ServiceItem[]>(
        `${this.apiUrl}/barbershops/${barbershopId}/services`
      );

  }

}
