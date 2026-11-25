import { Icon } from '../../components/icon/icon';
import {
  Component,
  inject
} from '@angular/core';

import {
  FormsModule
} from '@angular/forms';

import {
  ActivatedRoute,
  Router,
  RouterLink
} from '@angular/router';

import {
  AuthService
} from '../../services/auth';


@Component({
  selector: 'app-login',

  imports: [
    Icon,
    FormsModule,
    RouterLink
  ],

  templateUrl:
    './login.html',

  styleUrl:
    './login.scss'
})
export class Login {

  private readonly authService =
    inject(AuthService);


  private readonly router =
    inject(Router);


  private readonly route =
    inject(ActivatedRoute);


  email =
    '';


  password =
    '';


  loading =
    false;


  error =
    '';


  // =====================================================
  // LOGIN
  // =====================================================

  submit(): void {

    this.error =
      '';


    if (
      !this.email
      ||
      !this.password
    ) {

      this.error =
        'Ingresa tu correo electrónico y contraseña.';

      return;

    }


    if (
      this.password.length < 8
    ) {

      this.error =
        'La contraseña debe tener mínimo 8 caracteres.';

      return;

    }


    this.loading =
      true;


    this.authService
      .login({

        email:
          this.email.trim(),

        password:
          this.password

      })
      .subscribe({

        next: () => {

          this.loading =
            false;


          const requestedReturnUrl =
            this.route.snapshot
              .queryParamMap
              .get(
                'returnUrl'
              );


          const returnUrl =
            requestedReturnUrl
            &&
            requestedReturnUrl
              .startsWith('/')

              ? requestedReturnUrl

              : '/';


          this.router
            .navigateByUrl(
              returnUrl
            );

        },


        error: (error) => {

          console.error(
            'Error iniciando sesión:',
            error
          );


          this.loading =
            false;


          this.error =
            error?.error?.detail
            ||
            'Correo o contraseña incorrectos.';

        }

      });

  }

}
