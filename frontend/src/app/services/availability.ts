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
  AvailabilityResponse
} from '../models/availability';


@Injectable({
  providedIn: 'root'
})
export class AvailabilityService {

  private readonly http =
    inject(HttpClient);


  private readonly apiUrl =
    'http://127.0.0.1:8000/api/v1';


  getAvailability(
    barberId: number,
    serviceId: number,
    date: string
  ): Observable<AvailabilityResponse> {

    const params =
      new HttpParams()
        .set(
          'service_id',
          serviceId.toString()
        )
        .set(
          'date',
          date
        );


    return this.http.get<AvailabilityResponse>(
      `${this.apiUrl}/barbers/${barberId}/availability`,
      {
        params
      }
    );

  }

}
