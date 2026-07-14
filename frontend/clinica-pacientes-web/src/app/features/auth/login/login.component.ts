import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import {
  ActivatedRoute,
  Router,
} from '@angular/router';
import { finalize } from 'rxjs';

import { AuthService } from '../../../core/services/auth.service';
import { ApiErrorResponse } from '../../../models/api-response.model';


@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  private readonly formBuilder = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  isSubmitting = false;
  errorMessage = '';
  passwordVisible = false;

  readonly loginForm = this.formBuilder.nonNullable.group({
    usuario: [
      '',
      [
        Validators.required,
        Validators.minLength(3),
        Validators.maxLength(50),
      ],
    ],
    password: [
      '',
      [
        Validators.required,
        Validators.minLength(6),
        Validators.maxLength(100),
      ],
    ],
  });

  get usuarioControl() {
    return this.loginForm.controls.usuario;
  }

  get passwordControl() {
    return this.loginForm.controls.password;
  }

  submit(): void {
    this.errorMessage = '';

    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.isSubmitting = true;

    this.authService
      .login(this.loginForm.getRawValue())
      .pipe(
        finalize(() => {
          this.isSubmitting = false;
        }),
      )
      .subscribe({
        next: () => {
          const returnUrl =
            this.route.snapshot.queryParamMap.get(
              'returnUrl',
            ) ?? '/dashboard';

          void this.router.navigateByUrl(returnUrl);
        },
        error: (error: HttpErrorResponse) => {
          this.errorMessage =
            this.extractErrorMessage(error);
        },
      });
  }

  togglePasswordVisibility(): void {
    this.passwordVisible = !this.passwordVisible;
  }

  private extractErrorMessage(
    error: HttpErrorResponse,
  ): string {
    const response =
      error.error as Partial<ApiErrorResponse> | null;

    if (response?.message) {
      return response.message;
    }

    if (error.status === 0) {
      return (
        'No fue posible conectar con el servidor. '
        + 'Verifica que el backend esté en ejecución.'
      );
    }

    return 'No fue posible iniciar sesión.';
  }
}