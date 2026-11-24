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
  Navbar
} from '../../components/navbar/navbar';

import {
  Footer
} from '../../components/footer/footer';

import {
  AuthService
} from '../../services/auth';


@Component({
  selector: 'app-register',

  imports: [
    FormsModule,
    RouterLink,
    Navbar,
    Footer
  ],

  templateUrl:
    './register.html',

  styleUrl:
    './register.scss'
})
export class Register {

  private readonly authService =
    inject(AuthService);


  private readonly router =
    inject(Router);


  private readonly route =
    inject(ActivatedRoute);


  firstName =
    '';


  lastName =
    '';


  email =
    '';


  phone =
    '';


  password =
    '';


  confirmPassword =
    '';


  loading =
    false;


  error =
    '';


  // =====================================================
  // REGISTRAR
  // =====================================================

  submit(): void {

    this.error =
      '';


    if (
      !this.firstName
      ||
      !this.lastName
      ||
      !this.email
      ||
      !this.password
    ) {

      this.error =
        'Completa todos los campos obligatorios.';

      return;

    }


    if (
      this.firstName.trim().length < 2
      ||
      this.lastName.trim().length < 2
    ) {

      this.error =
        'Nombre y apellido deben tener mínimo 2 caracteres.';

      return;

    }


    if (
      this.password.length < 8
    ) {

      this.error =
        'La contraseña debe tener mínimo 8 caracteres.';

      return;

    }


    if (
      this.password
      !==
      this.confirmPassword
    ) {

      this.error =
        'Las contraseñas no coinciden.';

      return;

    }


    this.loading =
      true;


    const cleanEmail =
      this.email
        .trim()
        .toLowerCase();


    this.authService
      .register({

        first_name:
          this.firstName.trim(),

        last_name:
          this.lastName.trim(),

        email:
          cleanEmail,

        password:
          this.password,

        phone:
          this.phone.trim()
          ||
          null

      })
      .subscribe({

        next: () => {

          /*
           * Después de registrar,
           * iniciamos sesión automáticamente.
           */

          this.authService
            .login({

              email:
                cleanEmail,

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
                  'Usuario registrado pero falló login:',
                  error
                );


                this.loading =
                  false;


                this.error =
                  'Tu cuenta fue creada. Ahora inicia sesión.';


                this.router.navigate(
                  ['/login']
                );

              }

            });

        },


        error: (error) => {

          console.error(
            'Error registrando usuario:',
            error
          );


          this.loading =
            false;


          this.error =
            error?.error?.detail
            ||
            'No fue posible crear la cuenta.';

        }

      });

  }

}
