import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { SearchRequest } from '../models/search-request.model';
import { ENDPOINTS } from '../../../core/constants/endpoints';

@Injectable({
  providedIn: 'root'
})
export class SearchService {

  // URL base del backend
  private readonly API_URL = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  search(filters: SearchRequest): Observable<any> {
    return this.http.post(
      `${this.API_URL}${ENDPOINTS.busqueda}`,
      filters
    );
  }

  getCatalogos(): Observable<any> {
    return this.http.get(
      `${this.API_URL}${ENDPOINTS.catalogos}`
    );
  }

}