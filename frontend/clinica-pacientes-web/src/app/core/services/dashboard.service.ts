import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { DashboardIndicators } from '../../models/dashboard.model';

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  private readonly http = inject(HttpClient);

  private readonly apiUrl =
    `${environment.apiUrl}/dashboard`;

  getIndicators(): Observable<DashboardIndicators> {
    return this.http.get<DashboardIndicators>(
      this.apiUrl,
    );
  }
}