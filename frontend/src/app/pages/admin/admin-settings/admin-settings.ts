import { HomeServicePanel } from '../../../components/home-service-panel/home-service-panel';
import { PaymentMethodsPanel } from '../../../components/payment-methods-panel/payment-methods-panel';
import { Icon } from '../../../components/icon/icon';
import {
  ChangeDetectorRef,
  Component,
  OnInit,
  inject
} from '@angular/core';

import {
  HttpErrorResponse
} from '@angular/common/http';

import {
  AccessibleBarbershop,
  BarbershopAdmin,
  BarbershopSettingsService
} from '../../../services/barbershop-settings';

import {
  BarbershopSettings,
  BarbershopSettingsActionResponse,
  BarbershopSettingsUpdate
} from '../../../models/barbershop-settings';


// =====================================================
// SECCIONES DE CONFIGURACIÓN
// =====================================================

type SettingsSection =
  | 'general'
  | 'bookings'
  | 'customers'
  | 'barbers'
  | 'notifications' | 'home' | 'payments' | 'admins';


// =====================================================
// OPCIÓN DEL MENÚ DE CONFIGURACIÓN
// =====================================================

interface SettingsSectionItem {

  id: SettingsSection;

  label: string;

  description: string;

}


@Component({
  selector: 'app-admin-settings',

  imports: [ Icon, HomeServicePanel, PaymentMethodsPanel,],

  templateUrl:
    './admin-settings.html',

  styleUrl:
    './admin-settings.scss'
})
export class AdminSettings
  implements OnInit {


  // =====================================================
  // DEPENDENCIAS
  // =====================================================

  private readonly settingsService =
    inject(
      BarbershopSettingsService
    );


  private readonly cdr =
    inject(
      ChangeDetectorRef
    );


  // =====================================================
  // SECCIONES BASE
  // =====================================================

  readonly settingsSections:
    SettingsSectionItem[] = [

      {
        id:
          'general',

        label:
          'General',

        description:
          'Operación'
      },

      {
        id:
          'bookings',

        label:
          'Reservas',

        description:
          'Agenda y reglas'
      },

      {
        id:
          'customers',

        label:
          'Clientes',

        description:
          'Experiencia'
      },

      {
        id:
          'barbers',

        label:
          'Barberos',

        description:
          'Permisos'
      },

      {
        id: 'notifications', label: 'Notificaciones', description: 'Avisos' },
      { id: 'home', label: 'Domicilio', description: 'Servicio especial' },
      { id: 'payments', label: 'Pagos', description: 'Cobro directo' }

    ];


  // =====================================================
  // SECCIÓN ADMINISTRADORES
  // =====================================================

  private readonly adminsSection:
    SettingsSectionItem = {

      id:
        'admins',

      label:
        'Administradores',

      description:
        'Accesos'

    };


  activeSection:
    SettingsSection =
      'general';


  // =====================================================
  // BARBERÍAS ACCESIBLES
  // =====================================================

  barbershops:
    AccessibleBarbershop[] = [];


  selectedBarbershopId:
    number | null = null;


  // =====================================================
  // CONFIGURACIÓN
  // =====================================================

  settings:
    BarbershopSettings | null = null;


  // =====================================================
  // ADMINISTRADORES
  // =====================================================

  admins:
    BarbershopAdmin[] = [];


  loadingAdmins =
    false;


  savingAdmin =
    false;


  removingAdminUserId:
    number | null = null;


  adminError =
    '';


  adminSuccess =
    '';


  // =====================================================
  // ESTADOS GENERALES
  // =====================================================

  loadingBarbershops =
    true;


  loadingSettings =
    false;


  error =
    '';


  settingsError =
    '';


  successMessage =
    '';


  // =====================================================
  // ESTADOS DE GUARDADO
  // =====================================================

  savingAutoConfirm =
    false;


  savingSetting =
    false;


  // =====================================================
  // INICIO
  // =====================================================

  ngOnInit(): void {

    this.loadBarbershops();

  }


  // =====================================================
  // SECCIONES VISIBLES
  // =====================================================

  get visibleSettingsSections():
    SettingsSectionItem[] {

    if (
      this.canManageAdmins
    ) {

      return [
        ...this.settingsSections,
        this.adminsSection
      ];

    }


    return this.settingsSections;

  }


  // =====================================================
  // PUEDE GESTIONAR ADMINISTRADORES
  // =====================================================

  get canManageAdmins(): boolean {

    return (
      this.selectedBarbershop
        ?.can_manage_admins
      ??
      false
    );

  }


  // =====================================================
  // CAMBIAR SECCIÓN
  // =====================================================

  setActiveSection(
    section: SettingsSection
  ): void {

    // ---------------------------------------------------
    // EVITAR ACCESO VISUAL A ADMINISTRADORES
    // ---------------------------------------------------

    if (
      section ===
        'admins'
      &&
      !this.canManageAdmins
    ) {

      return;

    }


    this.activeSection =
      section;


    this.clearFeedback();


    // ---------------------------------------------------
    // CARGAR ADMINISTRADORES AL ENTRAR A LA SECCIÓN
    // ---------------------------------------------------

    if (
      section ===
        'admins'
      &&
      this.selectedBarbershopId !==
        null
    ) {

      this.loadAdmins();

    }

  }


  // =====================================================
  // VALIDAR SECCIÓN ACTIVA
  // =====================================================

  isSectionActive(
    section: SettingsSection
  ): boolean {

    return (
      this.activeSection ===
      section
    );

  }


  // =====================================================
  // CARGAR BARBERÍAS ACCESIBLES
  // =====================================================

  loadBarbershops(): void {

    this.loadingBarbershops =
      true;


    this.error =
      '';


    this.settings =
      null;


    this.admins =
      [];


    this.selectedBarbershopId =
      null;


    this.activeSection =
      'general';


    this.settingsService
      .getAccessibleBarbershops()
      .subscribe({

        next: (
          response
        ) => {

          this.barbershops =
            response.items
            ??
            [];


          this.loadingBarbershops =
            false;


          // -----------------------------------------------
          // SELECCIONAR BARBERÍA INICIAL
          // -----------------------------------------------

          if (
            this.barbershops.length >
            0
          ) {

            const firstActive =
              this.barbershops
                .find(
                  shop =>
                    shop.is_active
                );


            const initialShop =
              firstActive
              ??
              this.barbershops[0];


            this.selectedBarbershopId =
              initialShop.id;


            this.loadSettings(
              initialShop.id
            );

          }


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error cargando barberías accesibles:',
            error
          );


          this.barbershops =
            [];


          this.loadingBarbershops =
            false;


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
              'No tienes permisos para administrar barberías.';

          }

          else {

            this.error =
              'No fue posible cargar las barberías disponibles.';

          }


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // CARGAR CONFIGURACIÓN
  // =====================================================

  loadSettings(
    barbershopId: number
  ): void {

    if (
      !Number.isInteger(
        barbershopId
      )
      ||
      barbershopId <= 0
    ) {

      return;

    }


    this.loadingSettings =
      true;


    this.settingsError =
      '';


    this.successMessage =
      '';


    this.settings =
      null;


    this.settingsService
      .getSettings(
        barbershopId
      )
      .subscribe({

        next: (
          response:
            BarbershopSettings
        ) => {

          this.settings =
            response;


          this.loadingSettings =
            false;


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error cargando configuración:',
            error
          );


          this.settings =
            null;


          this.loadingSettings =
            false;


          if (
            error.status ===
            401
          ) {

            this.settingsError =
              'Tu sesión ha expirado.';

          }

          else if (
            error.status ===
            403
          ) {

            this.settingsError =
              'No tienes permisos para consultar esta configuración.';

          }

          else if (
            error.status ===
            404
          ) {

            this.settingsError =
              'La barbería seleccionada no existe.';

          }

          else {

            this.settingsError =
              'No fue posible cargar la configuración de la barbería.';

          }


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // CAMBIAR BARBERÍA
  // =====================================================

  onBarbershopChange(
    event: Event
  ): void {

    const target =
      event.target as
        HTMLSelectElement;


    const barbershopId =
      Number(
        target.value
      );


    if (
      !Number.isInteger(
        barbershopId
      )
      ||
      barbershopId <= 0
    ) {

      this.selectedBarbershopId =
        null;


      this.settings =
        null;


      this.admins =
        [];


      return;

    }


    this.selectedBarbershopId =
      barbershopId;


    this.settings =
      null;


    this.admins =
      [];


    this.adminError =
      '';


    this.adminSuccess =
      '';


    this.activeSection =
      'general';


    this.loadSettings(
      barbershopId
    );

  }


  // =====================================================
  // CONFIRMACIÓN AUTOMÁTICA
  // =====================================================

  toggleAutoConfirmation(): void {

    if (
      !this.settings
      ||
      this.selectedBarbershopId ===
        null
      ||
      this.savingAutoConfirm
    ) {

      return;

    }


    const newValue =
      !this.settings
        .auto_confirm_bookings;


    this.savingAutoConfirm =
      true;


    this.settingsError =
      '';


    this.successMessage =
      '';


    this.settingsService
      .updateAutoConfirmation(
        this.selectedBarbershopId,
        newValue
      )
      .subscribe({

        next: (
          response:
            BarbershopSettingsActionResponse
        ) => {

          this.settings =
            response.settings;


          this.successMessage =
            response.message;


          this.savingAutoConfirm =
            false;


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error cambiando confirmación automática:',
            error
          );


          this.savingAutoConfirm =
            false;


          this.settingsError =
            this.getErrorMessage(
              error,
              'No fue posible actualizar la confirmación automática.'
            );


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // ACTUALIZAR UN AJUSTE BOOLEANO
  // =====================================================

  updateBooleanSetting(
    field:
      keyof BarbershopSettingsUpdate,
    value: boolean
  ): void {

    if (
      !this.settings
      ||
      this.selectedBarbershopId ===
        null
      ||
      this.savingSetting
    ) {

      return;

    }


    const payload:
      BarbershopSettingsUpdate = {

        [field]:
          value

      };


    this.updateSettings(
      payload
    );

  }


  // =====================================================
  // ACTUALIZAR UN AJUSTE NUMÉRICO
  // =====================================================

  updateNumberSetting(
    field:
      keyof BarbershopSettingsUpdate,
    value: number
  ): void {

    if (
      !this.settings
      ||
      this.selectedBarbershopId ===
        null
      ||
      this.savingSetting
    ) {

      return;

    }


    if (
      !Number.isFinite(
        value
      )
    ) {

      return;

    }


    const payload:
      BarbershopSettingsUpdate = {

        [field]:
          value

      };


    this.updateSettings(
      payload
    );

  }


  // =====================================================
  // ACTUALIZAR CONFIGURACIÓN
  // =====================================================

  private updateSettings(
    payload:
      BarbershopSettingsUpdate
  ): void {

    if (
      this.selectedBarbershopId ===
      null
    ) {

      return;

    }


    this.savingSetting =
      true;


    this.settingsError =
      '';


    this.successMessage =
      '';


    this.settingsService
      .updateSettings(
        this.selectedBarbershopId,
        payload
      )
      .subscribe({

        next: (
          response:
            BarbershopSettingsActionResponse
        ) => {

          this.settings =
            response.settings;


          this.successMessage =
            response.message;


          this.savingSetting =
            false;


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error actualizando configuración:',
            error
          );


          this.savingSetting =
            false;


          this.settingsError =
            this.getErrorMessage(
              error,
              'No fue posible actualizar la configuración.'
            );


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // CARGAR ADMINISTRADORES
  // =====================================================

  loadAdmins(): void {

    if (
      this.selectedBarbershopId ===
        null
      ||
      !this.canManageAdmins
    ) {

      return;

    }


    this.loadingAdmins =
      true;


    this.adminError =
      '';


    this.adminSuccess =
      '';


    this.settingsService
      .getAdmins(
        this.selectedBarbershopId
      )
      .subscribe({

        next: (
          response:
            BarbershopAdmin[]
        ) => {

          this.admins =
            response
            ??
            [];


          this.loadingAdmins =
            false;


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error cargando administradores:',
            error
          );


          this.admins =
            [];


          this.loadingAdmins =
            false;


          this.adminError =
            this.getAdminErrorMessage(
              error,
              'No fue posible cargar los administradores.'
            );


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // ASIGNAR ADMINISTRADOR
  // =====================================================

  assignAdmin(
    userId: number
  ): void {

    if (
      this.selectedBarbershopId ===
        null
      ||
      !this.canManageAdmins
      ||
      this.savingAdmin
    ) {

      return;

    }


    if (
      !Number.isInteger(
        userId
      )
      ||
      userId <= 0
    ) {

      this.adminError =
        'Debes indicar un usuario válido.';

      return;

    }


    this.savingAdmin =
      true;


    this.adminError =
      '';


    this.adminSuccess =
      '';


    this.settingsService
      .assignAdmin(
        this.selectedBarbershopId,
        userId
      )
      .subscribe({

        next: () => {

          this.savingAdmin =
            false;


          this.adminSuccess =
            'Administrador asignado correctamente.';


          this.reloadAdminsPreservingMessage();


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error asignando administrador:',
            error
          );


          this.savingAdmin =
            false;


          this.adminError =
            this.getAdminErrorMessage(
              error,
              'No fue posible asignar el administrador.'
            );


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // ASIGNAR DESDE INPUT
  // =====================================================

  assignAdminFromInput(
    event: Event
  ): void {

    const target =
      event.target as
        HTMLInputElement;


    const userId =
      Number(
        target.value
      );


    this.assignAdmin(
      userId
    );


    if (
      Number.isInteger(
        userId
      )
      &&
      userId > 0
    ) {

      target.value =
        '';

    }

  }


  // =====================================================
  // DESASIGNAR ADMINISTRADOR
  // =====================================================

  removeAdmin(
    userId: number
  ): void {

    if (
      this.selectedBarbershopId ===
        null
      ||
      !this.canManageAdmins
      ||
      this.removingAdminUserId !==
        null
    ) {

      return;

    }


    this.removingAdminUserId =
      userId;


    this.adminError =
      '';


    this.adminSuccess =
      '';


    this.settingsService
      .removeAdmin(
        this.selectedBarbershopId,
        userId
      )
      .subscribe({

        next: (
          response
        ) => {

          this.removingAdminUserId =
            null;


          this.adminSuccess =
            response.message;


          this.admins =
            this.admins.filter(
              admin =>
                admin.user_id !==
                  userId
            );


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error desasignando administrador:',
            error
          );


          this.removingAdminUserId =
            null;


          this.adminError =
            this.getAdminErrorMessage(
              error,
              'No fue posible retirar el administrador.'
            );


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // RECARGAR ADMINISTRADORES CONSERVANDO MENSAJE
  // =====================================================

  private reloadAdminsPreservingMessage(): void {

    if (
      this.selectedBarbershopId ===
        null
    ) {

      return;

    }


    const message =
      this.adminSuccess;


    this.loadingAdmins =
      true;


    this.settingsService
      .getAdmins(
        this.selectedBarbershopId
      )
      .subscribe({

        next: (
          response:
            BarbershopAdmin[]
        ) => {

          this.admins =
            response
            ??
            [];


          this.loadingAdmins =
            false;


          this.adminSuccess =
            message;


          this.cdr
            .detectChanges();

        },


        error: (
          error:
            HttpErrorResponse
        ) => {

          console.error(
            'Error recargando administradores:',
            error
          );


          this.loadingAdmins =
            false;


          this.adminSuccess =
            '';


          this.adminError =
            this.getAdminErrorMessage(
              error,
              'El administrador fue asignado, pero no fue posible actualizar la lista.'
            );


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // BARBERÍA SELECCIONADA
  // =====================================================

  get selectedBarbershop():
    AccessibleBarbershop | null {

    if (
      this.selectedBarbershopId ===
      null
    ) {

      return null;

    }


    return (
      this.barbershops
        .find(
          shop =>
            shop.id ===
            this.selectedBarbershopId
        )
      ??
      null
    );

  }


  // =====================================================
  // SECCIÓN SELECCIONADA
  // =====================================================

  get selectedSettingsSection():
    SettingsSectionItem {

    const section =
      this.visibleSettingsSections
        .find(
          item =>
            item.id ===
            this.activeSection
        );


    return (
      section
      ??
      this.visibleSettingsSections[0]
    );

  }


  // =====================================================
  // MENSAJE DE ERROR CONFIGURACIÓN
  // =====================================================

  private getErrorMessage(
    error:
      HttpErrorResponse,
    fallback:
      string
  ): string {

    if (
      error.status ===
      401
    ) {

      return (
        'Tu sesión ha expirado.'
      );

    }


    if (
      error.status ===
      403
    ) {

      return (
        'No tienes permisos para modificar esta configuración.'
      );

    }


    if (
      error.status ===
      404
    ) {

      return (
        'La barbería seleccionada ya no existe.'
      );

    }


    if (
      error.status ===
        400
      ||
      error.status ===
        409
      ||
      error.status ===
        422
    ) {

      const detail =
        error?.error?.detail;


      if (
        typeof detail ===
        'string'
      ) {

        return detail;

      }

    }


    return fallback;

  }


  // =====================================================
  // MENSAJE DE ERROR ADMINISTRADORES
  // =====================================================

  private getAdminErrorMessage(
    error:
      HttpErrorResponse,
    fallback:
      string
  ): string {

    if (
      error.status ===
        401
    ) {

      return (
        'Tu sesión ha expirado.'
      );

    }


    if (
      error.status ===
        403
    ) {

      return (
        'No tienes permisos para gestionar administradores de esta barbería.'
      );

    }


    if (
      error.status ===
        404
    ) {

      const detail =
        error?.error?.detail;


      if (
        typeof detail ===
          'string'
      ) {

        return detail;

      }


      return (
        'No se encontró el usuario o la barbería solicitada.'
      );

    }


    if (
      error.status ===
        400
      ||
      error.status ===
        409
      ||
      error.status ===
        422
    ) {

      const detail =
        error?.error?.detail;


      if (
        typeof detail ===
          'string'
      ) {

        return detail;

      }

    }


    return fallback;

  }


  // =====================================================
  // LIMPIAR MENSAJES
  // =====================================================

  clearFeedback(): void {

    this.settingsError =
      '';


    this.successMessage =
      '';


    this.adminError =
      '';


    this.adminSuccess =
      '';

  }

}
