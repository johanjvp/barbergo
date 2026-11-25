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
  ServiceItem
} from '../models/service';


@Injectable({
  providedIn: 'root'
})
export class ServiceService {

  private readonly http =
    inject(HttpClient);


  private readonly apiUrl =
    API_URL;


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
