import { Component, inject } from '@angular/core';
import { Proceso } from '../../../../core/models/proceso';
import { SearchFilters } from '../../components/search-filters/search-filters';
import { ResultsTable } from '../../components/results-table/results-table';

import { ProcessSearch } from '../../services/process-search';

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

  search(): void {
    this.processSearch.search().subscribe({
      next: (response) => {
        this.processes = response;
      },

      error: (error) => {
        console.error('Error:', error);
      },
    });
  }
}