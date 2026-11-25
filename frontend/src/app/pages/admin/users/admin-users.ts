import { Icon } from '../../../components/icon/icon';
import {
  ChangeDetectorRef,
  Component,
  OnDestroy,
  OnInit,
  inject
} from '@angular/core';

import {
  HttpErrorResponse
} from '@angular/common/http';

import {
  AdminUserService
} from '../../../services/admin-user';

import {
  AdminUserItem,
  AdminUserListResponse,
  AdminUserSummary
} from '../../../models/admin-user';


@Component({
  selector: 'app-admin-users',

  imports: [
    Icon,],

  templateUrl:
    './admin-users.html',

  styleUrl:
    './admin-users.scss'
})
export class AdminUsers
  implements OnInit, OnDestroy {


  // =====================================================
  // DEPENDENCIAS
  // =====================================================

  private readonly service =
    inject(
      AdminUserService
    );


  private readonly cdr =
    inject(
      ChangeDetectorRef
    );


  // =====================================================
  // DATOS
  // =====================================================

  users:
    AdminUserItem[] = [];


  summary:
    AdminUserSummary = {

      total: 0,

      active: 0,

      inactive: 0,

      new_this_month: 0,

      clients: 0,

      barbers: 0,

      barbershop_admins: 0,

      platform_admins: 0

    };


  total =
    0;


  // =====================================================
  // PAGINACIÓN PROGRESIVA
  // =====================================================

  readonly pageSize =
    12;


  offset =
    0;


  loadingMore =
    false;


  // =====================================================
  // ESTADOS GENERALES
  // =====================================================

  loading =
    true;


  error =
    '';


  // =====================================================
  // FILTROS
  // =====================================================

  search =
    '';


  roleFilter =
    'all';


  statusFilter =
    'all';


  // =====================================================
  // USUARIO SELECCIONADO
  // =====================================================

  selectedUser:
    AdminUserItem | null =
      null;


  // =====================================================
  // CAMBIO DE ESTADO
  // =====================================================

  statusConfirmOpen =
    false;


  updatingUserId:
    number | null =
      null;


  statusActionError =
    '';


  // =====================================================
  // DEBOUNCE
  // =====================================================

  private searchTimeout:
    ReturnType<typeof setTimeout>
    |
    null =
      null;


  // =====================================================
  // PAGINACIÓN - HAY MÁS
  // =====================================================

  get hasMore(): boolean {

    return (
      this.users.length
      <
      this.total
    );

  }


  // =====================================================
  // PAGINACIÓN - RESTANTES
  // =====================================================

  get remainingCount(): number {

    return Math.max(
      0,
      this.total
      -
      this.users.length
    );

  }


  // =====================================================
  // PAGINACIÓN - PROGRESO
  // =====================================================

  get loadProgress(): number {

    if (
      this.total <= 0
    ) {

      return 0;

    }


    return Math.min(
      100,
      (
        this.users.length
        /
        this.total
      )
      *
      100
    );

  }


  // =====================================================
  // INICIO
  // =====================================================

  ngOnInit(): void {

    this.loadUsers(
      true
    );

  }


  // =====================================================
  // DESTRUIR
  // =====================================================

  ngOnDestroy(): void {

    if (
      this.searchTimeout !==
      null
    ) {

      clearTimeout(
        this.searchTimeout
      );


      this.searchTimeout =
        null;

    }

  }


  // =====================================================
  // CARGAR USUARIOS
  // =====================================================

  loadUsers(
    reset = true
  ): void {


    // -----------------------------------------------------
    // NUEVA CONSULTA
    // -----------------------------------------------------

    if (
      reset
    ) {

      this.offset =
        0;


      this.loading =
        true;


      this.loadingMore =
        false;


      this.error =
        '';

    }


    // -----------------------------------------------------
    // CARGAR MÁS
    // -----------------------------------------------------

    else {

      if (
        this.loadingMore
        ||
        !this.hasMore
      ) {

        return;

      }


      this.loadingMore =
        true;

    }


    this.service
      .getAll(
        this.search,
        this.roleFilter,
        this.statusFilter,
        this.pageSize,
        this.offset
      )
      .subscribe({

        next: (
          response:
            AdminUserListResponse
        ) => {


          // -------------------------------------------------
          // NUEVA CONSULTA
          // -------------------------------------------------

          if (
            reset
          ) {

            this.users =
              response.items;

          }


          // -------------------------------------------------
          // AGREGAR NUEVOS RESULTADOS
          // -------------------------------------------------

          else {

            this.users = [
              ...this.users,
              ...response.items
            ];

          }


          this.summary =
            response.summary;


          this.total =
            response.total;


          // -------------------------------------------------
          // SIGUIENTE OFFSET
          // -------------------------------------------------

          this.offset =
            this.users.length;


          this.loading =
            false;


          this.loadingMore =
            false;


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error cargando usuarios:',
            error
          );


          if (
            reset
          ) {

            this.users =
              [];


            this.total =
              0;

          }


          if (
            error.status ===
            401
          ) {

            this.error =
              'Tu sesión ha expirado.';

          }

          else if (
            error.status ===
            403
          ) {

            this.error =
              'No tienes permisos para consultar usuarios.';

          }

          else {

            this.error =
              'No fue posible cargar los usuarios.';

          }


          this.loading =
            false;


          this.loadingMore =
            false;


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // CARGAR MÁS
  // =====================================================

  loadMore(): void {

    this.loadUsers(
      false
    );

  }


  // =====================================================
  // BÚSQUEDA
  // =====================================================

  onSearch(
    event: Event
  ): void {

    const target =
      event.target;


    if (
      !(
        target instanceof
        HTMLInputElement
      )
    ) {

      return;

    }


    this.search =
      target.value;


    if (
      this.searchTimeout !==
      null
    ) {

      clearTimeout(
        this.searchTimeout
      );

    }


    this.searchTimeout =
      setTimeout(
        () => {

          this.searchTimeout =
            null;


          this.loadUsers(
            true
          );

        },
        350
      );

  }


  // =====================================================
  // FILTRO POR ROL
  // =====================================================

  setRoleFilter(
    role: string
  ): void {

    if (
      this.roleFilter ===
      role
    ) {

      return;

    }


    this.roleFilter =
      role;


    this.closeUser();


    this.loadUsers(
      true
    );

  }


  // =====================================================
  // FILTRO POR ESTADO
  // =====================================================

  setStatusFilter(
    status: string
  ): void {

    if (
      this.statusFilter ===
      status
    ) {

      return;

    }


    this.statusFilter =
      status;


    this.closeUser();


    this.loadUsers(
      true
    );

  }


  // =====================================================
  // ABRIR DETALLE
  // =====================================================

  openUser(
    user:
      AdminUserItem
  ): void {

    this.selectedUser =
      user;


    this.statusConfirmOpen =
      false;


    this.statusActionError =
      '';

  }


  // =====================================================
  // CERRAR DETALLE
  // =====================================================

  closeUser(): void {

    /*
     * Mientras se procesa una activación
     * o inhabilitación no permitimos
     * cerrar accidentalmente el drawer.
     */
    if (
      this.updatingUserId !==
      null
    ) {

      return;

    }


    this.selectedUser =
      null;


    this.statusConfirmOpen =
      false;


    this.statusActionError =
      '';

  }


  // =====================================================
  // SOLICITAR CAMBIO DE ESTADO
  // =====================================================

  requestStatusChange(): void {

    if (
      !this.selectedUser
    ) {

      return;

    }


    this.statusActionError =
      '';


    this.statusConfirmOpen =
      true;


    this.cdr
      .detectChanges();

  }


  // =====================================================
  // CANCELAR CAMBIO DE ESTADO
  // =====================================================

  cancelStatusChange(): void {

    if (
      this.updatingUserId !==
      null
    ) {

      return;

    }


    this.statusConfirmOpen =
      false;


    this.statusActionError =
      '';


    this.cdr
      .detectChanges();

  }


  // =====================================================
  // CONFIRMAR CAMBIO DE ESTADO
  // =====================================================

  confirmStatusChange(): void {

    if (
      !this.selectedUser
      ||
      this.updatingUserId !==
      null
    ) {

      return;

    }


    // -----------------------------------------------------
    // USUARIO ACTUAL
    // -----------------------------------------------------

    const user =
      this.selectedUser;


    // -----------------------------------------------------
    // ESTADO ANTERIOR
    // -----------------------------------------------------

    const previousStatus =
      user.is_active;


    // -----------------------------------------------------
    // NUEVO ESTADO
    // -----------------------------------------------------

    const nextStatus =
      !previousStatus;


    // -----------------------------------------------------
    // BLOQUEAR ACCIÓN
    // -----------------------------------------------------

    this.updatingUserId =
      user.id;


    this.statusActionError =
      '';


    // -----------------------------------------------------
    // BACKEND
    // -----------------------------------------------------

    this.service
      .updateStatus(
        user.id,
        nextStatus
      )
      .subscribe({

        next: (
          response
        ) => {


          // ===============================================
          // USUARIO ACTUALIZADO
          // ===============================================

          const updatedUser:
            AdminUserItem = {

            ...user,

            is_active:
              response.is_active

          };


          // ===============================================
          // ACTUALIZAR LISTADO LOCAL
          // ===============================================

          this.users =
            this.users.map(
              item => {

                if (
                  item.id ===
                  user.id
                ) {

                  return updatedUser;

                }


                return item;

              }
            );


          // ===============================================
          // ACTUALIZAR DRAWER
          // ===============================================

          this.selectedUser =
            updatedUser;


          // ===============================================
          // ACTUALIZAR KPI
          // ===============================================

          if (
            response.is_active !==
            previousStatus
          ) {


            // ---------------------------------------------
            // SE REACTIVÓ
            // ---------------------------------------------

            if (
              response.is_active
            ) {

              this.summary = {

                ...this.summary,

                active:
                  this.summary.active
                  +
                  1,

                inactive:
                  Math.max(
                    0,
                    this.summary.inactive
                    -
                    1
                  )

              };

            }


            // ---------------------------------------------
            // SE INHABILITÓ
            // ---------------------------------------------

            else {

              this.summary = {

                ...this.summary,

                active:
                  Math.max(
                    0,
                    this.summary.active
                    -
                    1
                  ),

                inactive:
                  this.summary.inactive
                  +
                  1

              };

            }

          }


          // ===============================================
          // FINALIZAR
          // ===============================================

          this.updatingUserId =
            null;


          this.statusConfirmOpen =
            false;


          this.statusActionError =
            '';


          /*
           * Si estamos viendo exclusivamente
           * activos o inactivos, el usuario
           * modificado ya no pertenece
           * necesariamente a ese filtro.
           *
           * Recargamos para mantener la lista
           * consistente con el backend.
           */
          if (
            this.statusFilter !==
            'all'
          ) {

            this.selectedUser =
              null;


            this.loadUsers(
              true
            );


            return;

          }


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error actualizando estado del usuario:',
            error
          );


          this.updatingUserId =
            null;


          if (
            error.status ===
            400
          ) {

            this.statusActionError =
              error?.error?.detail
              ||
              'La operación solicitada no es válida.';

          }

          else if (
            error.status ===
            401
          ) {

            this.statusActionError =
              'Tu sesión ha expirado.';

          }

          else if (
            error.status ===
            403
          ) {

            this.statusActionError =
              error?.error?.detail
              ||
              'No tienes permisos para modificar este usuario.';

          }

          else if (
            error.status ===
            404
          ) {

            this.statusActionError =
              'El usuario ya no existe o no fue encontrado.';

          }

          else {

            this.statusActionError =
              error?.error?.detail
              ||
              'No fue posible actualizar el estado del usuario.';

          }


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // INICIALES
  // =====================================================

  getInitials(
    user:
      AdminUserItem
  ): string {

    const first =
      (
        user.first_name
        ??
        ''
      )
        .trim();


    const last =
      (
        user.last_name
        ??
        ''
      )
        .trim();


    const initials =
      (
        first.charAt(0)
        +
        last.charAt(0)
      )
        .trim();


    if (
      initials
    ) {

      return initials
        .toUpperCase();

    }


    if (
      user.email
    ) {

      return user.email
        .charAt(0)
        .toUpperCase();

    }


    return 'U';

  }


  // =====================================================
  // ROL PRINCIPAL
  // =====================================================

  getPrimaryRole(
    user:
      AdminUserItem
  ): string {

    const priority = [

      'PLATFORM_ADMIN',

      'BARBERSHOP_ADMIN',

      'BARBER',

      'CLIENT'

    ];


    for (
      const role
      of priority
    ) {

      if (
        user.roles.includes(
          role
        )
      ) {

        return role;

      }

    }


    return (
      user.roles[0]
      ??
      'CLIENT'
    );

  }


  // =====================================================
  // NOMBRE DEL ROL
  // =====================================================

  roleLabel(
    role: string
  ): string {

    switch (
      role
    ) {

      case 'PLATFORM_ADMIN':

        return 'Administrador';


      case 'BARBERSHOP_ADMIN':

        return 'Dueño / Admin';


      case 'BARBER':

        return 'Barbero';


      case 'CLIENT':

        return 'Cliente';


      default:

        return role;

    }

  }


  // =====================================================
  // CLASE DEL ROL
  // =====================================================

  roleClass(
    role: string
  ): string {

    switch (
      role
    ) {

      case 'PLATFORM_ADMIN':

        return 'platform';


      case 'BARBERSHOP_ADMIN':

        return 'owner';


      case 'BARBER':

        return 'barber';


      default:

        return 'client';

    }

  }


  // =====================================================
  // FORMATO MONEDA
  // =====================================================

  formatCurrency(
    value:
      number
      |
      null
      |
      undefined
  ): string {

    return new Intl
      .NumberFormat(
        'es-CO',
        {

          style:
            'currency',

          currency:
            'COP',

          maximumFractionDigits:
            0

        }
      )
      .format(
        Number(
          value
          ??
          0
        )
      );

  }


  // =====================================================
  // FORMATO FECHA
  // =====================================================

  formatDate(
    value:
      string
      |
      null
      |
      undefined
  ): string {

    if (
      !value
    ) {

      return '—';

    }


    const date =
      new Date(
        value
      );


    if (
      Number.isNaN(
        date.getTime()
      )
    ) {

      return '—';

    }


    return new Intl
      .DateTimeFormat(
        'es-CO',
        {

          day:
            '2-digit',

          month:
            'short',

          year:
            'numeric'

        }
      )
      .format(
        date
      );

  }

}
