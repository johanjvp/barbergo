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


export const barberGuard:
  CanActivateFn = () => {

  const http =
    inject(
      HttpClient
    );


  const router =
    inject(
      Router
    );


  return http
    .get<any>(
      'http://127.0.0.1:8000/api/v1/auth/me'
    )
    .pipe(

      map(
        user => {

          // =============================================
          // EXTRAER ROLES
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
          // UN SOLO STRING
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
          // ARRAY DE ROLES
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
                      role
                      &&
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
            roles
              .map(
                role =>
                  String(
                    role
                  )
                    .trim()
                    .toUpperCase()
              );


          // =============================================
          // BARBER
          // =============================================

          if (
            roles.includes(
              'BARBER'
            )
          ) {

            return true;

          }


          // =============================================
          // SIN PERMISO
          // =============================================

          console.warn(
            'Acceso denegado al panel del barbero. Roles:',
            roles
          );


          return router
            .createUrlTree(
              ['/']
            );

        }
      ),


      // ===============================================
      // SIN LOGIN
      // ===============================================

      catchError(
        error => {

          console.warn(
            'No fue posible validar el acceso del barbero:',
            error
          );


          return of(
            router
              .createUrlTree(
                ['/login'],
                {
                  queryParams: {
                    returnUrl:
                      '/barber'
                  }
                }
              )
          );

        }
      )

    );

};
