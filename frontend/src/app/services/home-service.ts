import { API_URL } from '../core/api';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export type HomeServiceStatus = 'NONE' | 'PENDING' | 'APPROVED' | 'REJECTED' | 'SUSPENDED';

export interface HomeServiceInfo {
  barbershop_id: number;
  barbershop_name: string;
  status: HomeServiceStatus;
  offers_home_service: boolean;
  radius_km: number | null;
  fee: number;
  min_notice_hours: number;
  zones: string | null;
  requirements: {
    hygiene_kit?: boolean;
    barbers_verified?: boolean;
    accepts_policy?: boolean;
    notes?: string | null;
    declared_barbers?: number;
    declared_services?: number;
  } | null;
  rejection_reason: string | null;
  requested_at: string | null;
  reviewed_at: string | null;
  has_coordinates: boolean;
}

export interface HomeServiceRequestPayload {
  radius_km: number;
  fee: number;
  min_notice_hours: number;
  zones: string | null;
  hygiene_kit: boolean;
  barbers_verified: boolean;
  accepts_policy: boolean;
  notes: string | null;
}

@Injectable({ providedIn: 'root' })
export class HomeServiceApi {
  private readonly http = inject(HttpClient);
  private readonly base = API_URL;

  // ---- barbería ----
  get(barbershopId: number): Observable<HomeServiceInfo> {
    return this.http.get<HomeServiceInfo>(`${this.base}/barbershop-settings/${barbershopId}/home-service`);
  }

  request(barbershopId: number, payload: HomeServiceRequestPayload): Observable<HomeServiceInfo> {
    return this.http.post<HomeServiceInfo>(
      `${this.base}/barbershop-settings/${barbershopId}/home-service/request`,
      payload
    );
  }

  updateTerms(
    barbershopId: number,
    terms: { fee: number; min_notice_hours: number; zones: string | null }
  ): Observable<HomeServiceInfo> {
    return this.http.patch<HomeServiceInfo>(
      `${this.base}/barbershop-settings/${barbershopId}/home-service/terms`,
      terms
    );
  }

  disable(barbershopId: number): Observable<HomeServiceInfo> {
    return this.http.delete<HomeServiceInfo>(`${this.base}/barbershop-settings/${barbershopId}/home-service`);
  }

  // ---- administrador de la plataforma ----
  listRequests(status?: HomeServiceStatus): Observable<HomeServiceInfo[]> {
    let params = new HttpParams();
    if (status) params = params.set('status_filter', status);
    return this.http.get<HomeServiceInfo[]>(`${this.base}/admin/home-service/requests`, { params });
  }

  approve(barbershopId: number): Observable<HomeServiceInfo> {
    return this.http.post<HomeServiceInfo>(
      `${this.base}/admin/barbershops/${barbershopId}/home-service/approve`,
      {}
    );
  }

  reject(barbershopId: number, reason: string): Observable<HomeServiceInfo> {
    return this.http.post<HomeServiceInfo>(
      `${this.base}/admin/barbershops/${barbershopId}/home-service/reject`,
      { reason }
    );
  }

  suspend(barbershopId: number, reason: string): Observable<HomeServiceInfo> {
    return this.http.post<HomeServiceInfo>(
      `${this.base}/admin/barbershops/${barbershopId}/home-service/suspend`,
      { reason }
    );
  }
}
