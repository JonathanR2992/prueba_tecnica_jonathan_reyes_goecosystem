import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  DeletePatientResponse,
  PatientFilters,
  PatientListResponse,
  PatientPayload,
  PatientResponse,
} from '../../models/patient.model';

@Injectable({
  providedIn: 'root',
})
export class PatientService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/patients`;

  getPatients(
    filters: PatientFilters = {},
  ): Observable<PatientListResponse> {
    let params = new HttpParams();

    if (filters.page !== undefined) {
      params = params.set(
        'page',
        filters.page.toString(),
      );
    }

    if (filters.per_page !== undefined) {
      params = params.set(
        'per_page',
        filters.per_page.toString(),
      );
    }

    if (filters.search) {
      params = params.set(
        'search',
        filters.search,
      );
    }

    if (filters.status) {
      params = params.set(
        'status',
        filters.status,
      );
    }

    if (filters.priority) {
      params = params.set(
        'priority',
        filters.priority,
      );
    }

    if (filters.eps_codigo) {
      params = params.set(
        'eps_codigo',
        filters.eps_codigo,
      );
    }

    return this.http.get<PatientListResponse>(
      this.apiUrl,
      { params },
    );
  }

  getPatient(
    patientId: number,
  ): Observable<PatientResponse> {
    return this.http.get<PatientResponse>(
      `${this.apiUrl}/${patientId}`,
    );
  }

  createPatient(
    payload: PatientPayload,
  ): Observable<PatientResponse> {
    return this.http.post<PatientResponse>(
      this.apiUrl,
      payload,
    );
  }

  updatePatient(
    patientId: number,
    payload: PatientPayload,
  ): Observable<PatientResponse> {
    return this.http.put<PatientResponse>(
      `${this.apiUrl}/${patientId}`,
      payload,
    );
  }

  deletePatient(
    patientId: number,
  ): Observable<DeletePatientResponse> {
    return this.http.delete<DeletePatientResponse>(
      `${this.apiUrl}/${patientId}`,
    );
  }
}