import { environment } from '../../../../environments/environment';
import { ENDPOINTS } from '../../../core/constants/endpoints';
import { Proceso } from '../../../core/models/proceso';
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ProcessSearch {
  private readonly http = inject(HttpClient);

  search(): Observable<Proceso[]> {
    return this.http.get<Proceso[]>(`${environment.apiUrl}${ENDPOINTS.procesos}`);
  }
}
