import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { finalize } from 'rxjs';

import { DashboardService } from '../../core/services/dashboard.service';
import { DashboardIndicators } from '../../models/dashboard.model';

interface IndicatorCard {
  label: string;
  value: number;
  icon: string;
  className: string;
  description: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
  private readonly dashboardService =
    inject(DashboardService);

  indicators: DashboardIndicators | null = null;

  isLoading = false;
  errorMessage = '';

  ngOnInit(): void {
    this.loadIndicators();
  }

  loadIndicators(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.dashboardService
      .getIndicators()
      .pipe(
        finalize(() => {
          this.isLoading = false;
        }),
      )
      .subscribe({
        next: (response) => {
          this.indicators = response;
        },
        error: (error: HttpErrorResponse) => {
          this.errorMessage =
            this.getErrorMessage(error);
        },
      });
  }

  get cards(): IndicatorCard[] {
    if (!this.indicators) {
      return [];
    }

    return [
      {
        label: 'Pacientes registrados',
        value: this.indicators.total_pacientes,
        icon: 'groups',
        className: 'card-total',
        description: 'Total disponible en el sistema',
      },
      {
        label: 'Pendientes',
        value: this.indicators.pacientes_pendientes,
        icon: 'schedule',
        className: 'card-pending',
        description: 'Aún no han iniciado atención',
      },
      {
        label: 'En atención',
        value: this.indicators.pacientes_en_atencion,
        icon: 'medical_services',
        className: 'card-attention',
        description: 'Actualmente en proceso asistencial',
      },
      {
        label: 'Atendidos',
        value: this.indicators.pacientes_atendidos,
        icon: 'task_alt',
        className: 'card-attended',
        description: 'Atención finalizada',
      },
      {
        label: 'Prioridad alta',
        value: this.indicators.pacientes_prioridad_alta,
        icon: 'priority_high',
        className: 'card-priority',
        description: 'Pacientes clasificados como alta',
      },
      {
        label: 'Pendientes prioritarios',
        value: this.indicators.pendientes_prioridad_alta,
        icon: 'warning',
        className: 'card-critical',
        description: 'Pendientes con prioridad alta',
      },
    ];
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

    return 'No fue posible cargar los indicadores.';
  }
}