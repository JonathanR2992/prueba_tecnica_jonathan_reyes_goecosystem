import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import {
  Component,
  OnInit,
  inject,
} from '@angular/core';

import {
  AbstractControl,
  FormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  Validators,
} from '@angular/forms';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';

import {
  ActivatedRoute,
  Router,
  RouterLink,
} from '@angular/router';

import {
  finalize,
  forkJoin,
} from 'rxjs';

import { CatalogService } from '../../../core/services/catalog.service';
import { PatientService } from '../../../core/services/patient.service';

import { ApiErrorResponse } from '../../../models/api-response.model';
import { CatalogsResponse } from '../../../models/catalog.model';
import {
  Patient,
  PatientPayload,
} from '../../../models/patient.model';


function noFutureDateValidator(
  control: AbstractControl,
): ValidationErrors | null {
  if (!control.value) {
    return null;
  }

  const selectedDate = new Date(
    `${control.value}T00:00:00`,
  );

  const today = new Date();

  today.setHours(0, 0, 0, 0);

  return selectedDate > today
    ? { futureDate: true }
    : null;
}


@Component({
  selector: 'app-patient-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl: './patient-form.component.html',
  styleUrl: './patient-form.component.scss',
})
export class PatientFormComponent implements OnInit {
  private readonly formBuilder = inject(FormBuilder);
  private readonly patientService = inject(PatientService);
  private readonly catalogService = inject(CatalogService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly snackBar = inject(MatSnackBar);

  patientId: number | null = null;
  patient: Patient | null = null;
  catalogs: CatalogsResponse | null = null;

  isLoading = false;
  isSubmitting = false;
  loadErrorMessage = '';
  generalErrorMessage = '';

  readonly patientForm =
    this.formBuilder.nonNullable.group({
      tipo_documento: [
        '',
        [
          Validators.required,
          Validators.maxLength(3),
        ],
      ],

      documento: [
        '',
        [
          Validators.required,
          Validators.minLength(3),
          Validators.maxLength(20),
        ],
      ],

      nombre_completo: [
        '',
        [
          Validators.required,
          Validators.minLength(3),
          Validators.maxLength(150),
        ],
      ],

      fecha_nacimiento: [
        '',
        [
          Validators.required,
          noFutureDateValidator,
        ],
      ],

      genero: [
        '',
        Validators.required,
      ],

      telefono: [
        '',
        [
          Validators.required,
          Validators.minLength(7),
          Validators.maxLength(20),
          Validators.pattern(
            /^[0-9+\-\s()]{7,20}$/,
          ),
        ],
      ],

      correo: [
        '',
        [
          Validators.email,
          Validators.maxLength(150),
        ],
      ],

      eps_codigo: [
        '',
        Validators.required,
      ],

      ciudad: [
        '',
        Validators.maxLength(80),
      ],

      prioridad: [
        '',
        Validators.required,
      ],

      estado: [
        '',
        Validators.required,
      ],
    });


  get isEditMode(): boolean {
    return this.patientId !== null;
  }


  get pageTitle(): string {
    return this.isEditMode
      ? 'Editar paciente'
      : 'Nuevo paciente';
  }


  get pageDescription(): string {
    return this.isEditMode
      ? 'Actualiza la información y el estado asistencial del paciente.'
      : 'Registra un nuevo paciente en la lista de atención.';
  }


  get maximumBirthDate(): string {
    const today = new Date();

    const year = today.getFullYear();
    const month = String(
      today.getMonth() + 1,
    ).padStart(2, '0');

    const day = String(
      today.getDate(),
    ).padStart(2, '0');

    return `${year}-${month}-${day}`;
  }


  ngOnInit(): void {
    this.resolvePatientId();
    this.loadInitialData();
  }


  submit(): void {
    this.generalErrorMessage = '';

    if (this.patientForm.invalid) {
      this.patientForm.markAllAsTouched();

      this.snackBar.open(
        'Revisa los campos marcados antes de continuar.',
        'Cerrar',
        {
          duration: 4000,
        },
      );

      return;
    }

    const payload = this.buildPayload();

    this.isSubmitting = true;

    const request$ = this.isEditMode
      ? this.patientService.updatePatient(
          this.patientId!,
          payload,
        )
      : this.patientService.createPatient(
          payload,
        );

    request$
      .pipe(
        finalize(() => {
          this.isSubmitting = false;
        }),
      )
      .subscribe({
        next: (response) => {
          this.snackBar.open(
            response.message
              ?? (
                this.isEditMode
                  ? 'Paciente actualizado correctamente'
                  : 'Paciente creado correctamente'
              ),
            'Cerrar',
            {
              duration: 3500,
            },
          );

          void this.router.navigate([
            '/patients',
          ]);
        },

        error: (error: HttpErrorResponse) => {
          this.processApiError(error);
        },
      });
  }


  retryLoad(): void {
    this.loadInitialData();
  }


  cancel(): void {
    void this.router.navigate([
      '/patients',
    ]);
  }


  hasError(
    fieldName: keyof typeof this.patientForm.controls,
    errorName: string,
  ): boolean {
    const control =
      this.patientForm.controls[fieldName];

    return (
      control.touched
      && control.hasError(errorName)
    );
  }


  private resolvePatientId(): void {
    const rawPatientId =
      this.route.snapshot.paramMap.get('id');

    if (!rawPatientId) {
      this.patientId = null;
      return;
    }

    const parsedPatientId = Number(rawPatientId);

    if (
      !Number.isInteger(parsedPatientId)
      || parsedPatientId <= 0
    ) {
      this.patientId = null;

      void this.router.navigate([
        '/patients',
      ]);

      return;
    }

    this.patientId = parsedPatientId;
  }


  private loadInitialData(): void {
    this.isLoading = true;
    this.loadErrorMessage = '';

    if (this.isEditMode) {
      forkJoin({
        catalogs: this.catalogService.getCatalogs(),
        patientResponse:
          this.patientService.getPatient(
            this.patientId!,
          ),
      })
        .pipe(
          finalize(() => {
            this.isLoading = false;
          }),
        )
        .subscribe({
          next: ({
            catalogs,
            patientResponse,
          }) => {
            this.catalogs = catalogs;
            this.patient = patientResponse.patient;

            this.populateForm(
              patientResponse.patient,
            );
          },

          error: (error: HttpErrorResponse) => {
            this.loadErrorMessage =
              this.extractErrorMessage(error);
          },
        });

      return;
    }

    this.catalogService
      .getCatalogs()
      .pipe(
        finalize(() => {
          this.isLoading = false;
        }),
      )
      .subscribe({
        next: (catalogs) => {
          this.catalogs = catalogs;

          this.patientForm.patchValue({
            prioridad: 'Media',
            estado: 'Pendiente',
          });
        },

        error: (error: HttpErrorResponse) => {
          this.loadErrorMessage =
            this.extractErrorMessage(error);
        },
      });
  }


  private populateForm(
    patient: Patient,
  ): void {
    this.patientForm.patchValue({
      tipo_documento:
        patient.tipo_documento,

      documento:
        patient.documento,

      nombre_completo:
        patient.nombre_completo,

      fecha_nacimiento:
        patient.fecha_nacimiento,

      genero:
        patient.genero,

      telefono:
        patient.telefono,

      correo:
        patient.correo ?? '',

      eps_codigo:
        patient.eps_codigo,

      ciudad:
        patient.ciudad ?? '',

      prioridad:
        patient.prioridad,

      estado:
        patient.estado,
    });
  }


  private buildPayload(): PatientPayload {
    const formValue =
      this.patientForm.getRawValue();

    return {
      tipo_documento:
        formValue.tipo_documento.trim(),

      documento:
        formValue.documento.trim(),

      nombre_completo:
        formValue.nombre_completo.trim(),

      fecha_nacimiento:
        formValue.fecha_nacimiento,

      genero:
        formValue.genero,

      telefono:
        formValue.telefono.trim(),

      correo:
        formValue.correo.trim() || null,

      eps_codigo:
        formValue.eps_codigo,

      ciudad:
        formValue.ciudad.trim() || null,

      prioridad:
        formValue.prioridad,

      estado:
        formValue.estado,
    };
  }


  private processApiError(
    error: HttpErrorResponse,
  ): void {
    const response =
      error.error as Partial<ApiErrorResponse> | null;

    if (
      response?.details
      && typeof response.details === 'object'
    ) {
      Object.entries(
        response.details,
      ).forEach(
        ([fieldName, message]) => {
          const control =
            this.patientForm.get(fieldName);

          if (control) {
            control.setErrors({
              ...control.errors,
              server: message,
            });

            control.markAsTouched();
          }
        },
      );
    }

    this.generalErrorMessage =
      response?.message
      ?? this.extractErrorMessage(error);

    this.snackBar.open(
      this.generalErrorMessage,
      'Cerrar',
      {
        duration: 5000,
      },
    );
  }


  private extractErrorMessage(
    error: HttpErrorResponse,
  ): string {
    if (error.status === 0) {
      return (
        'No fue posible conectar con el backend. '
        + 'Verifica que Flask esté en ejecución.'
      );
    }

    if (error.error?.message) {
      return error.error.message;
    }

    return 'No fue posible completar la operación.';
  }
}