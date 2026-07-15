import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, shareReplay } from 'rxjs';

import { environment } from '../../../environments/environment';
import { CatalogsResponse } from '../../models/catalog.model';

@Injectable({
  providedIn: 'root',
})
export class CatalogService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/catalogs`;

  private catalogsRequest$?: Observable<CatalogsResponse>;

  getCatalogs(
    forceRefresh = false,
  ): Observable<CatalogsResponse> {
    if (
      forceRefresh
      || !this.catalogsRequest$
    ) {
      this.catalogsRequest$ =
        this.http
          .get<CatalogsResponse>(
            this.apiUrl,
          )
          .pipe(
            shareReplay({
              bufferSize: 1,
              refCount: true,
            }),
          );
    }

    return this.catalogsRequest$;
  }
}