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
  AutoConfirmBookingUpdate,
  BarbershopSettings,
  BarbershopSettingsActionResponse,
  BarbershopSettingsUpdate
} from '../models/barbershop-settings';


export interface AccessibleBarbershop {

  id: number;

  name: string;

  city: string | null;

  neighborhood: string | null;

  is_active: boolean;

  can_manage_admins: boolean;

}


export interface AccessibleBarbershopsResponse {

  items: AccessibleBarbershop[];

  total: number;

}


export interface BarbershopAdmin {

  id: number;

  user_id: number;

  barbershop_id: number;

  first_name: string;

  last_name: string;

  email: string;

  is_active: boolean;

}


export interface BarbershopAdminAssignment {

  id: number;

  user_id: number;

  barbershop_id: number;

  is_active: boolean;

}


export interface BarbershopAdminAssignPayload {

  user_id: number;

}


export interface BarbershopAdminActionResponse {

  message: string;

}


@Injectable({
  providedIn: 'root'
})
export class BarbershopSettingsService {


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

  private readonly apiBaseUrl =
    API_URL;


  private readonly settingsUrl =
    `${this.apiBaseUrl}/barbershop-settings`;


  private readonly barbershopsUrl =
    `${this.apiBaseUrl}/barbershops`;


  // =====================================================
  // BARBERÍAS ACCESIBLES
  // =====================================================

  getAccessibleBarbershops():
    Observable<AccessibleBarbershopsResponse> {

    return this.http
      .get<AccessibleBarbershopsResponse>(
        `${this.settingsUrl}/accessible-barbershops`
      );

  }


  // =====================================================
  // OBTENER CONFIGURACIÓN
  // =====================================================

  getSettings(
    barbershopId: number
  ): Observable<BarbershopSettings> {

    return this.http
      .get<BarbershopSettings>(
        `${this.settingsUrl}/${barbershopId}`
      );

  }


  // =====================================================
  // ACTUALIZAR CONFIGURACIÓN GENERAL
  // =====================================================

  updateSettings(
    barbershopId: number,
    payload: BarbershopSettingsUpdate
  ): Observable<BarbershopSettingsActionResponse> {

    return this.http
      .patch<BarbershopSettingsActionResponse>(
        `${this.settingsUrl}/${barbershopId}`,
        payload
      );

  }


  // =====================================================
  // CONFIRMACIÓN AUTOMÁTICA
  // =====================================================

  updateAutoConfirmation(
    barbershopId: number,
    enabled: boolean
  ): Observable<BarbershopSettingsActionResponse> {

    const payload:
      AutoConfirmBookingUpdate = {

        enabled

      };


    return this.http
      .patch<BarbershopSettingsActionResponse>(
        `${this.settingsUrl}/${barbershopId}/auto-confirm`,
        payload
      );

  }


  // =====================================================
  // LISTAR ADMINISTRADORES DE BARBERÍA
  // =====================================================

  getAdmins(
    barbershopId: number
  ): Observable<BarbershopAdmin[]> {

    return this.http
      .get<BarbershopAdmin[]>(
        `${this.barbershopsUrl}/${barbershopId}/admins`
      );

  }


  // =====================================================
  // ASIGNAR ADMINISTRADOR
  // =====================================================

  assignAdmin(
    barbershopId: number,
    userId: number
  ): Observable<BarbershopAdminAssignment> {

    const payload:
      BarbershopAdminAssignPayload = {

        user_id: userId

      };


    return this.http
      .post<BarbershopAdminAssignment>(
        `${this.barbershopsUrl}/${barbershopId}/admins`,
        payload
      );

  }


  // =====================================================
  // DESASIGNAR ADMINISTRADOR
  // =====================================================

  removeAdmin(
    barbershopId: number,
    userId: number
  ): Observable<BarbershopAdminActionResponse> {

    return this.http
      .delete<BarbershopAdminActionResponse>(
        `${this.barbershopsUrl}/${barbershopId}/admins/${userId}`
      );

  }

}
