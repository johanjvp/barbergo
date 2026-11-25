import {
  Routes
} from '@angular/router';

import {
  adminGuard
} from './guards/admin.guard';

import {
  barberGuard
} from './guards/barber.guard';

export const routes:
  Routes = [

    // =====================================================
    // HOME
    // =====================================================

    {
      path: '',
      loadComponent: () => import('./pages/home/home').then(m => m.Home)
    },


    // =====================================================
    // BARBERÍAS PÚBLICAS
    // =====================================================

    {
      path: 'barberias',
      loadComponent: () => import('./pages/barbershops/barbershops').then(m => m.Barbershops)
    },


    {
      path: 'barberias/:id',
      loadComponent: () => import('./pages/barbershop-detail/barbershop-detail').then(m => m.BarbershopDetail)
    },


    // =====================================================
    // AUTENTICACIÓN
    // =====================================================

    {
      path: 'login',
      loadComponent: () => import('./pages/login/login').then(m => m.Login)
    },


    {
      path: 'registro',
      loadComponent: () => import('./pages/register/register').then(m => m.Register)
    },


    // =====================================================
    // CLIENTE
    // =====================================================

    {
      path: 'mis-reservas',
      loadComponent: () => import('./pages/my-bookings/my-bookings').then(m => m.MyBookings)
    },


    // =====================================================
    // PANEL DEL BARBERO
    // =====================================================

    {
      path: 'barber',

      loadComponent: () => import('./pages/barber/barber-dashboard').then(m => m.BarberDashboard),

      canActivate: [
        barberGuard
      ]
    },


    // =====================================================
    // ADMINISTRACIÓN
    // =====================================================

    {
      path: 'admin',

      loadComponent: () => import('./pages/admin/admin-layout/admin-layout').then(m => m.AdminLayout),

      canActivate: [
        adminGuard
      ],

      children: [

        // =================================================
        // DASHBOARD
        // =================================================

        {
          path: '',
          loadComponent: () => import('./pages/admin/dashboard/admin-dashboard').then(m => m.AdminDashboard)
        },


        // =================================================
        // BARBERÍAS
        // =================================================

        {
          path: 'barberias',
          loadComponent: () => import('./pages/admin/barbershops/admin-barbershops').then(m => m.AdminBarbershops)
        },


        // =================================================
        // DETALLE ADMINISTRATIVO DE BARBERÍA
        // =================================================

        {
          path: 'barberias/:id',
          loadComponent: () => import('./pages/admin/barbershops/detail/admin-barbershop-detail').then(m => m.AdminBarbershopDetail)
        },


        // =================================================
        // USUARIOS
        // =================================================

        {
          path: 'usuarios',
          loadComponent: () => import('./pages/admin/users/admin-users').then(m => m.AdminUsers)
        },


        // =================================================
        // RESERVAS
        // =================================================

        {
          path: 'reservas',
          loadComponent: () => import('./pages/admin/bookings/admin-bookings').then(m => m.AdminBookings)
        },


        // =================================================
        // CONFIGURACIÓN
        // =================================================

        {
          path: 'configuracion',
          loadComponent: () => import('./pages/admin/admin-settings/admin-settings').then(m => m.AdminSettings)
        }

      ]

    },


    // =====================================================
    // RUTA DESCONOCIDA
    // SIEMPRE DEBE IR AL FINAL
    // =====================================================

    {
      path: '**',
      redirectTo: ''
    }

  ];
