import { Component, inject } from '@angular/core';

import { Proceso } from '../../../../core/models/proceso';

import { SearchFilters } from '../../components/search-filters/search-filters';
import { ResultsTable } from '../../components/results-table/results-table';

import { ProcessSearch } from '../../services/process-search';
import { SearchRequest } from '../../models/search-request.model';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [SearchFilters, ResultsTable],
  templateUrl: './search.html',
  styleUrl: './search.scss',
})
export class Search {

  private readonly processSearch = inject(ProcessSearch);

  processes: Proceso[] = [];

  search(filters: SearchRequest): void {

    console.log('=======================================');
    console.log('📤 SearchPage recibió los filtros:');
    console.log(filters);
    console.log('=======================================');

    this.processSearch.search(filters).subscribe({

      next: (response) => {

        console.log('✅ Respuesta del backend:');
        console.log(response);

        this.processes = response;

      },

      error: (error) => {

        console.error('❌ Error recibido del backend:');
        console.error(error);

      }

    });

  }

}