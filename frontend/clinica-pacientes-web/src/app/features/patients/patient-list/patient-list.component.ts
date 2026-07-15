import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import {
  Component,
  OnInit,
  ViewChild,
  inject,
} from '@angular/core';

import {
  FormBuilder,
  ReactiveFormsModule,
} from '@angular/forms';

import { Router, RouterLink } from '@angular/router';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import {
  MatPaginator,
  MatPaginatorModule,
  PageEvent,
} from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';

import {
  debounceTime,
  distinctUntilChanged,
  finalize,
} from 'rxjs';

import { CatalogService } from '../../../core/services/catalog.service';
import { PatientService } from '../../../core/services/patient.service';
import { CatalogsResponse } from '../../../models/catalog.model';
import {
  Patient,
  PatientPagination,
} from '../../../models/patient.model';

import {
  ConfirmDialogComponent,
  ConfirmDialogData,
} from '../../../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-patient-list',
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
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatTableModule,
    MatTooltipModule,
  ],
  templateUrl: './patient-list.component.html',
  styleUrl: './patient-list.component.scss',
})
export class PatientListComponent implements OnInit {
  private readonly formBuilder = inject(FormBuilder);
  private readonly patientService = inject(PatientService);
  private readonly catalogService = inject(CatalogService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);
  private readonly router = inject(Router);

  @ViewChild(MatPaginator)
  paginator?: MatPaginator;

  readonly displayedColumns = [
    'documento',
    'nombre_completo',
    'eps',
    'prioridad',
    'estado',
    'fecha_creacion',
    'acciones',
  ];

  readonly filterForm =
    this.formBuilder.nonNullable.group({
      search: [''],
      status: [''],
      priority: [''],
      eps_codigo: [''],
    });

  patients: Patient[] = [];
  catalogs: CatalogsResponse | null = null;

  pagination: PatientPagination = {
    page: 1,
    per_page: 10,
    total: 0,
    pages: 0,
    has_next: false,
    has_prev: false,
    next_page: null,
    previous_page: null,
  };

  isLoading = false;
  errorMessage = '';

  ngOnInit(): void {
    this.loadCatalogs();
    this.configureSearch();
    this.loadPatients();
  }

  loadPatients(
    page = this.pagination.page,
    perPage = this.pagination.per_page,
  ): void {
    const filters = this.filterForm.getRawValue();

    this.isLoading = true;
    this.errorMessage = '';

    this.patientService
      .getPatients({
        page,
        per_page: perPage,
        search: filters.search.trim() || undefined,
        status: filters.status || undefined,
        priority: filters.priority || undefined,
        eps_codigo: filters.eps_codigo || undefined,
      })
      .pipe(
        finalize(() => {
          this.isLoading = false;
        }),
      )
      .subscribe({
        next: (response) => {
          this.patients = response.items;
          this.pagination = response.pagination;
        },
        error: (error: HttpErrorResponse) => {
          this.errorMessage =
            this.getErrorMessage(error);
        },
      });
  }

  applyFilters(): void {
    this.loadPatients(
      1,
      this.pagination.per_page,
    );

    if (this.paginator) {
      this.paginator.firstPage();
    }
  }

  clearFilters(): void {
    this.filterForm.reset({
      search: '',
      status: '',
      priority: '',
      eps_codigo: '',
    });

    this.loadPatients(
      1,
      this.pagination.per_page,
    );

    if (this.paginator) {
      this.paginator.firstPage();
    }
  }

  onPageChange(event: PageEvent): void {
    this.loadPatients(
      event.pageIndex + 1,
      event.pageSize,
    );
  }

  editPatient(patientId: number): void {
    void this.router.navigate([
      '/patients',
      patientId,
      'edit',
    ]);
  }

  confirmDelete(patient: Patient): void {
    const dialogRef = this.dialog.open<
      ConfirmDialogComponent,
      ConfirmDialogData,
      boolean
    >(
      ConfirmDialogComponent,
      {
        width: '430px',
        data: {
          title: 'Eliminar paciente',
          message:
            `¿Está seguro de eliminar a `
            + `${patient.nombre_completo}? `
            + 'Esta acción no se puede deshacer.',
          confirmText: 'Eliminar',
          cancelText: 'Cancelar',
        },
      },
    );

    dialogRef
      .afterClosed()
      .subscribe((confirmed) => {
        if (confirmed) {
          this.deletePatient(patient);
        }
      });
  }

  getPriorityClass(priority: string): string {
    return (
      `priority-${priority
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')}`
    );
  }

  getStatusClass(status: string): string {
    return (
      `status-${status
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/\s+/g, '-')}`
    );
  }

  private configureSearch(): void {
    this.filterForm.controls.search
      .valueChanges
      .pipe(
        debounceTime(400),
        distinctUntilChanged(),
      )
      .subscribe(() => {
        this.applyFilters();
      });
  }

  private loadCatalogs(): void {
    this.catalogService
      .getCatalogs()
      .subscribe({
        next: (response) => {
          this.catalogs = response;
        },
        error: () => {
          this.snackBar.open(
            'No fue posible cargar los catálogos.',
            'Cerrar',
            {
              duration: 4000,
            },
          );
        },
      });
  }

  private deletePatient(
    patient: Patient,
  ): void {
    this.patientService
      .deletePatient(patient.paciente_id)
      .subscribe({
        next: (response) => {
          this.snackBar.open(
            response.message,
            'Cerrar',
            {
              duration: 3500,
            },
          );

          const targetPage =
            this.patients.length === 1
            && this.pagination.page > 1
              ? this.pagination.page - 1
              : this.pagination.page;

          this.loadPatients(
            targetPage,
            this.pagination.per_page,
          );
        },
        error: (error: HttpErrorResponse) => {
          this.snackBar.open(
            this.getErrorMessage(error),
            'Cerrar',
            {
              duration: 5000,
            },
          );
        },
      });
  }

  private getErrorMessage(
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