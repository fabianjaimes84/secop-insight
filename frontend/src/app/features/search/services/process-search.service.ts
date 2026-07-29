import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../../environments/environment';

import { ENDPOINTS } from '../../../core/constants/endpoints';
import { Proceso } from '../../../core/models/proceso';

import { SearchRequest } from '../models/search-request.model';

@Injectable({
  providedIn: 'root',
})
export class ProcessSearchService {

  // ==========================================
  // Inyección de dependencias
  // ==========================================

  private readonly http = inject(HttpClient);

  // ==========================================
  // Buscar procesos
  // ==========================================

  search(filters: SearchRequest): Observable<Proceso[]> {

    return this.http.post<Proceso[]>(
      `${environment.apiUrl}${ENDPOINTS.busqueda}`,
      filters
    );

  }

}