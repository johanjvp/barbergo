import { API_URL } from '../core/api';
import {
  Injectable,
  inject
} from '@angular/core';

import {
  HttpClient
} from '@angular/common/http';

import {
  Observable
} from 'rxjs';

import {
  AdminDashboardResponse
} from '../models/admin-dashboard';


@Injectable({
  providedIn: 'root'
})
export class AdminDashboardService {

  private readonly http =
    inject(HttpClient);


  private readonly apiUrl =
    `${API_URL}/admin/dashboard`;


  // =====================================================
  // DASHBOARD GENERAL
  // =====================================================

  getDashboard():
    Observable<AdminDashboardResponse> {

    return this.http
      .get<AdminDashboardResponse>(
        this.apiUrl
      );

  }

}
