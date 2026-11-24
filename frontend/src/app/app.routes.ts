import {
  Routes
} from '@angular/router';

import {
  Home
} from './pages/home/home';

import {
  adminGuard
} from './guards/admin.guard';

import {
  barberGuard
} from './guards/barber.guard';

import {
  Barbershops
} from './pages/barbershops/barbershops';

import {
  BarbershopDetail
} from './pages/barbershop-detail/barbershop-detail';

import {
  Login
} from './pages/login/login';

import {
  Register
} from './pages/register/register';

import {
  MyBookings
} from './pages/my-bookings/my-bookings';

import {
  AdminLayout
} from './pages/admin/admin-layout/admin-layout';

import {
  AdminDashboard
} from './pages/admin/dashboard/admin-dashboard';

import {
  AdminBarbershops
} from './pages/admin/barbershops/admin-barbershops';

import {
  AdminBarbershopDetail
} from './pages/admin/barbershops/detail/admin-barbershop-detail';

import {
  AdminUsers
} from './pages/admin/users/admin-users';

import {
  AdminBookings
} from './pages/admin/bookings/admin-bookings';

import {
  AdminSettings
} from './pages/admin/admin-settings/admin-settings';

import {
  BarberDashboard
} from './pages/barber/barber-dashboard';


export const routes:
  Routes = [

    // =====================================================
    // HOME
    // =====================================================

    {
      path: '',
      component: Home
    },


    // =====================================================
    // BARBERÍAS PÚBLICAS
    // =====================================================

    {
      path: 'barberias',
      component: Barbershops
    },


    {
      path: 'barberias/:id',
      component: BarbershopDetail
    },


    // =====================================================
    // AUTENTICACIÓN
    // =====================================================

    {
      path: 'login',
      component: Login
    },


    {
      path: 'registro',
      component: Register
    },


    // =====================================================
    // CLIENTE
    // =====================================================

    {
      path: 'mis-reservas',
      component: MyBookings
    },


    // =====================================================
    // PANEL DEL BARBERO
    // =====================================================

    {
      path: 'barber',

      component:
        BarberDashboard,

      canActivate: [
        barberGuard
      ]
    },


    // =====================================================
    // ADMINISTRACIÓN
    // =====================================================

    {
      path: 'admin',

      component:
        AdminLayout,

      canActivate: [
        adminGuard
      ],

      children: [

        // =================================================
        // DASHBOARD
        // =================================================

        {
          path: '',
          component:
            AdminDashboard
        },


        // =================================================
        // BARBERÍAS
        // =================================================

        {
          path: 'barberias',
          component:
            AdminBarbershops
        },


        // =================================================
        // DETALLE ADMINISTRATIVO DE BARBERÍA
        // =================================================

        {
          path: 'barberias/:id',
          component:
            AdminBarbershopDetail
        },


        // =================================================
        // USUARIOS
        // =================================================

        {
          path: 'usuarios',
          component:
            AdminUsers
        },


        // =================================================
        // RESERVAS
        // =================================================

        {
          path: 'reservas',
          component:
            AdminBookings
        },


        // =================================================
        // CONFIGURACIÓN
        // =================================================

        {
          path: 'configuracion',
          component:
            AdminSettings
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
