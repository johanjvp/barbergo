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
  AdminBarbershopDetail,
  AdminBarbershopListResponse,
  AdminBarbershopStatusResponse
} from '../models/admin-barbershop';


@Injectable({
  providedIn:
    'root'
})
export class AdminBarbershopService {


  private readonly http =
    inject(
      HttpClient
    );


  private readonly apiUrl =
    'http://127.0.0.1:8000/api/v1/admin/barbershops';


  // =====================================================
  // LISTAR BARBERÍAS
  // =====================================================

  getAll(
    search = '',
    statusFilter = 'all',
    limit = 12,
    offset = 0
  ):
    Observable<
      AdminBarbershopListResponse
    > {

    let params =
      new HttpParams()
        .set(
          'status_filter',
          statusFilter
        )
        .set(
          'limit',
          String(limit)
        )
        .set(
          'offset',
          String(offset)
        );


    if (
      search.trim()
    ) {

      params =
        params.set(
          'search',
          search.trim()
        );

    }


    return this.http
      .get<
        AdminBarbershopListResponse
      >(
        this.apiUrl,
        {
          params
        }
      );

  }


  // =====================================================
  // OBTENER DETALLE DE BARBERÍA
  // =====================================================

  getById(
    barbershopId: number
  ):
    Observable<
      AdminBarbershopDetail
    > {

    return this.http
      .get<
        AdminBarbershopDetail
      >(
        `${
          this.apiUrl
        }/${
          barbershopId
        }`
      );

  }


  // =====================================================
  // ACTIVAR / DESACTIVAR BARBERÍA
  // =====================================================

  updateStatus(
    barbershopId: number,
    isActive: boolean
  ):
    Observable<
      AdminBarbershopStatusResponse
    > {

    return this.http
      .patch<
        AdminBarbershopStatusResponse
      >(
        `${
          this.apiUrl
        }/${
          barbershopId
        }/status`,
        {
          is_active:
            isActive
        }
      );

  }

}
