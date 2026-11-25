import { API_URL } from '../core/api';
import {
  inject
} from '@angular/core';

import {
  CanActivateFn,
  Router
} from '@angular/router';

import {
  HttpClient
} from '@angular/common/http';

import {
  catchError,
  map,
  of
} from 'rxjs';


export const adminGuard:
  CanActivateFn = () => {

  const http =
    inject(HttpClient);

  const router =
    inject(Router);


  return http
    .get<any>(
      `${API_URL}/auth/me`
    )
    .pipe(

      map(
        user => {

          // =============================================
          // EXTRAER ROLES DE FORMA FLEXIBLE
          // =============================================

          const rawRoles =
            user?.roles
            ??
            user?.role_names
            ??
            user?.role_codes
            ??
            user?.role
            ??
            [];


          let roles:
            string[] = [];


          // =============================================
          // SI VIENE UN SOLO STRING
          // =============================================

          if (
            typeof rawRoles ===
            'string'
          ) {

            roles = [
              rawRoles
            ];

          }


          // =============================================
          // SI VIENE UN ARRAY
          // =============================================

          else if (
            Array.isArray(
              rawRoles
            )
          ) {

            roles =
              rawRoles
                .map(
                  role => {

                    if (
                      typeof role ===
                      'string'
                    ) {

                      return role;

                    }


                    if (
                      role &&
                      typeof role ===
                      'object'
                    ) {

                      return (
                        role.name
                        ??
                        role.code
                        ??
                        role.role
                        ??
                        ''
                      );

                    }


                    return '';

                  }
                )
                .filter(
                  role =>
                    !!role
                );

          }


          // =============================================
          // NORMALIZAR
          // =============================================

          roles =
            roles.map(
              role =>
                String(role)
                  .trim()
                  .toUpperCase()
            );


          // =============================================
          // PLATFORM ADMIN
          // =============================================

          if (
            roles.includes(
              'PLATFORM_ADMIN'
            )
          ) {

            return true;

          }


          // =============================================
          // BARBERSHOP ADMIN
          // =============================================

          if (
            roles.includes(
              'BARBERSHOP_ADMIN'
            )
          ) {

            return true;

          }


          // =============================================
          // SIN PERMISO
          // =============================================

          console.warn(
            'Acceso denegado a /admin. Roles:',
            roles
          );


          return router
            .createUrlTree(
              ['/']
            );

        }
      ),


      // ===============================================
      // SIN LOGIN / TOKEN INVÁLIDO
      // ===============================================

      catchError(
        error => {

          console.warn(
            'No fue posible validar acceso administrativo:',
            error
          );


          return of(
            router
              .createUrlTree(
                ['/login'],
                {
                  queryParams: {
                    returnUrl:
                      '/admin/configuracion'
                  }
                }
              )
          );

        }
      )

    );

};
