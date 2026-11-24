import {
  ChangeDetectorRef,
  Component,
  OnInit,
  inject
} from '@angular/core';

import {
  Router,
  RouterLink
} from '@angular/router';

import {
  AuthService
} from '../../services/auth';

import {
  UserMeResponse
} from '../../models/auth';


@Component({
  selector: 'app-navbar',

  imports: [
    RouterLink
  ],

  templateUrl:
    './navbar.html',

  styleUrl:
    './navbar.scss'
})
export class Navbar
  implements OnInit {


  // =====================================================
  // DEPENDENCIAS
  // =====================================================

  private readonly authService =
    inject(
      AuthService
    );


  private readonly router =
    inject(
      Router
    );


  private readonly cdr =
    inject(
      ChangeDetectorRef
    );


  // =====================================================
  // USUARIO
  // =====================================================

  currentUser:
    UserMeResponse | null = null;


  loadingSession =
    true;


  // =====================================================
  // INICIO
  // =====================================================

  ngOnInit(): void {

    this.loadCurrentUser();

  }


  // =====================================================
  // CARGAR USUARIO AUTENTICADO
  // =====================================================

  private loadCurrentUser(): void {

    // ---------------------------------------------------
    // SIN TOKEN
    // ---------------------------------------------------

    if (
      !this.authService
        .isAuthenticated()
    ) {

      this.currentUser =
        null;


      this.loadingSession =
        false;


      this.cdr
        .detectChanges();


      return;

    }


    // ---------------------------------------------------
    // CON TOKEN
    // ---------------------------------------------------

    this.authService
      .me()
      .subscribe({

        next: (
          user
        ) => {

          this.currentUser =
            user;


          this.loadingSession =
            false;


          this.cdr
            .detectChanges();

        },


        error: (
          error
        ) => {

          console.error(
            'No fue posible recuperar la sesión:',
            error
          );


          this.authService
            .logout();


          this.currentUser =
            null;


          this.loadingSession =
            false;


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // NOMBRE COMPLETO
  // =====================================================

  get userFullName():
    string {

    if (
      !this.currentUser
    ) {

      return '';

    }


    return (
      `${this.currentUser.first_name} ${this.currentUser.last_name}`
    );

  }


  // =====================================================
  // INICIALES DEL USUARIO
  // =====================================================

  get userInitials():
    string {

    if (
      !this.currentUser
    ) {

      return '';

    }


    const firstName =
      this.currentUser
        .first_name
        ?.trim()
        ??
        '';


    const lastName =
      this.currentUser
        .last_name
        ?.trim()
        ??
        '';


    const firstInitial =
      firstName
        .charAt(0)
        .toUpperCase();


    const lastInitial =
      lastName
        .charAt(0)
        .toUpperCase();


    return (
      `${firstInitial}${lastInitial}`
    );

  }


  // =====================================================
  // ROLES NORMALIZADOS
  // =====================================================

  get userRoles():
    string[] {

    if (
      !this.currentUser
    ) {

      return [];

    }


    const user:
      any =
        this.currentUser;


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


    // ---------------------------------------------------
    // UN SOLO ROL
    // ---------------------------------------------------

    if (
      typeof rawRoles ===
      'string'
    ) {

      roles = [
        rawRoles
      ];

    }


    // ---------------------------------------------------
    // VARIOS ROLES
    // ---------------------------------------------------

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


    return roles
      .map(
        role =>
          String(
            role
          )
            .trim()
            .toUpperCase()
      );

  }


  // =====================================================
  // PLATFORM ADMIN
  // =====================================================

  get isPlatformAdmin():
    boolean {

    return (
      this.userRoles
        .includes(
          'PLATFORM_ADMIN'
        )
    );

  }


  // =====================================================
  // ADMINISTRADOR DE BARBERÍA
  // =====================================================

  get isBarbershopAdmin():
    boolean {

    return (
      this.userRoles
        .includes(
          'BARBERSHOP_ADMIN'
        )
    );

  }


  // =====================================================
  // TIENE ACCESO ADMINISTRATIVO
  // =====================================================

  get hasAdminAccess():
    boolean {

    return (
      this.isPlatformAdmin
      ||
      this.isBarbershopAdmin
    );

  }


  // =====================================================
  // ETIQUETA DE ROL
  // =====================================================

  get adminLabel():
    string {

    if (
      this.isPlatformAdmin
    ) {

      return (
        'Administrador general'
      );

    }


    if (
      this.isBarbershopAdmin
    ) {

      return (
        'Administrador de barbería'
      );

    }


    return '';

  }


  // =====================================================
  // RUTA DEL PANEL
  // =====================================================

  get adminPanelRoute():
    string {

    if (
      this.isPlatformAdmin
    ) {

      return (
        '/admin'
      );

    }


    if (
      this.isBarbershopAdmin
    ) {

      return (
        '/admin/configuracion'
      );

    }


    return (
      '/'
    );

  }


  // =====================================================
  // IR AL PANEL ADMINISTRATIVO
  // =====================================================

  goToAdminPanel(): void {

    if (
      !this.hasAdminAccess
    ) {

      return;

    }


    this.router
      .navigateByUrl(
        this.adminPanelRoute
      );

  }


  // =====================================================
  // CERRAR SESIÓN
  // =====================================================

  logout(): void {

    this.authService
      .logout();


    this.currentUser =
      null;


    this.loadingSession =
      false;


    this.cdr
      .detectChanges();


    this.router
      .navigateByUrl(
        '/'
      );

  }

  // =====================================================
// BARBERO
// =====================================================

get isBarber():
  boolean {

  return (
    this.userRoles
      .includes(
        'BARBER'
      )
  );

}

}
