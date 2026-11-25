import { API_URL } from '../core/api';
import {
  inject,
  Injectable
} from '@angular/core';

import {
  HttpClient
} from '@angular/common/http';

import {
  Observable,
  tap
} from 'rxjs';

import {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  UserMeResponse,
  UserResponse
} from '../models/auth';


@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private readonly http =
    inject(HttpClient);


  private readonly apiUrl =
    `${API_URL}/auth`;


  private readonly tokenKey =
    'barbergo_access_token';


  // =====================================================
  // REGISTRO
  // =====================================================

  register(
    data: RegisterRequest
  ): Observable<UserResponse> {

    return this.http.post<UserResponse>(
      `${this.apiUrl}/register`,
      data
    );

  }


  // =====================================================
  // LOGIN
  // =====================================================

  login(
    data: LoginRequest
  ): Observable<TokenResponse> {

    return this.http
      .post<TokenResponse>(
        `${this.apiUrl}/login`,
        data
      )
      .pipe(

        tap(
          response => {

            localStorage.setItem(
              this.tokenKey,
              response.access_token
            );

          }
        )

      );

  }


  // =====================================================
  // USUARIO ACTUAL
  // =====================================================

  me():
    Observable<UserMeResponse> {

    return this.http.get<UserMeResponse>(
      `${this.apiUrl}/me`
    );

  }


  // =====================================================
  // TOKEN
  // =====================================================

  getToken():
    string | null {

    return localStorage.getItem(
      this.tokenKey
    );

  }


  // =====================================================
  // SABER SI HAY SESIÓN
  // =====================================================

  isAuthenticated():
    boolean {

    return !!this.getToken();

  }


  // =====================================================
  // CERRAR SESIÓN
  // =====================================================

  logout(): void {

    localStorage.removeItem(
      this.tokenKey
    );

  }

}
