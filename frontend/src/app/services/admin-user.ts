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
  AdminUserListResponse,
  AdminUserStatusResponse
} from '../models/admin-user';


@Injectable({
  providedIn: 'root'
})
export class AdminUserService {


  private readonly http =
    inject(
      HttpClient
    );


  private readonly apiUrl =
    `${API_URL}/admin/users`;


  getAll(
    search = '',
    roleFilter = 'all',
    statusFilter = 'all',
    limit = 12,
    offset = 0
  ):
    Observable<
      AdminUserListResponse
    > {

    let params =
      new HttpParams()
        .set(
          'role_filter',
          roleFilter
        )
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
        AdminUserListResponse
      >(
        this.apiUrl,
        {
          params
        }
      );

  }

  updateStatus(
  userId: number,
  isActive: boolean
): Observable<AdminUserStatusResponse> {

  return this.http.patch<AdminUserStatusResponse>(
    `${this.apiUrl}/${userId}/status`,
    {
      is_active: isActive
    }
  );

}

}


