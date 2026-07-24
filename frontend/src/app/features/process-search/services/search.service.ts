import { Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs';

import { SearchRequest } from '../models/search-request.model';

@Injectable({
  providedIn: 'root'
})
export class SearchService {

  constructor(private http: HttpClient) {}

  search(filters: SearchRequest): Observable<any> {

    return this.http.post(
      'http://localhost:8000/procesos/search',
      filters
    );

  }

}