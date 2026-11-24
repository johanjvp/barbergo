import {
  inject,
  Injectable
} from '@angular/core';

import {
  HttpClient,
  HttpParams
} from '@angular/common/http';

import {
  Observable
} from 'rxjs';

import {
  BarbershopDetail,
  BarbershopDiscoveryResponse
} from '../models/barbershop';


@Injectable({
  providedIn: 'root'
})
export class BarbershopService {

  private readonly http =
    inject(HttpClient);


  private readonly apiUrl =
    'http://127.0.0.1:8000/api/v1/barbershops';


  // =====================================================
  // DESCUBRIR BARBERÍAS
  // =====================================================

  discover(
    search?: string,
    neighborhood?: string
  ): Observable<BarbershopDiscoveryResponse> {

    let params =
      new HttpParams();


    if (
      search?.trim()
    ) {

      params =
        params.set(
          'q',
          search.trim()
        );

    }


    if (
      neighborhood?.trim()
    ) {

      params =
        params.set(
          'neighborhood',
          neighborhood.trim()
        );

    }


    return this.http
      .get<BarbershopDiscoveryResponse>(
        `${this.apiUrl}/discover`,
        {
          params
        }
      );

  }


  // =====================================================
  // OBTENER BARBERÍA POR ID
  // =====================================================

  getById(
    id: number
  ): Observable<BarbershopDetail> {

    return this.http
      .get<BarbershopDetail>(
        `${this.apiUrl}/${id}`
      );

  }

}
