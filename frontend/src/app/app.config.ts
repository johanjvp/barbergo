import { registerLocaleData } from '@angular/common';
import localeEs from '@angular/common/locales/es';
import { LOCALE_ID } from '@angular/core';

registerLocaleData(localeEs);
import {
  ApplicationConfig,
  provideBrowserGlobalErrorListeners
} from '@angular/core';

import {
  provideRouter,
  withViewTransitions
} from '@angular/router';

import {
  provideHttpClient,
  withInterceptors
} from '@angular/common/http';

import {
  routes
} from './app.routes';

import {
  authInterceptor
} from './interceptors/auth.interceptor';


export const appConfig: ApplicationConfig = {

  providers: [
    { provide: LOCALE_ID, useValue: 'es' },

    provideBrowserGlobalErrorListeners(),

    provideRouter(
      routes,
      withViewTransitions()
    ),

    provideHttpClient(
      withInterceptors([
        authInterceptor
      ])
    )

  ]

};
