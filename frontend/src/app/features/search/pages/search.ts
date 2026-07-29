import { Component, ViewChild, inject } from '@angular/core';

import { Proceso } from '@core/models/proceso';

import { SearchFilters } from '@features/search/filters/search-filters';
import { SearchRequest } from '@features/search/models/search-request.model';
import { ProcessSearchService } from '@features/search/services/process-search.service';
import { ResultsTable } from '@features/search/table/results-table';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [SearchFilters, ResultsTable],
  templateUrl: './search.html',
  styleUrl: './search.scss',
})
export class Search {
  // ==========================================
  // Inyección de dependencias
  // ==========================================

  private readonly processSearchService = inject(ProcessSearchService);

  // ==========================================
  // Estado del componente
  // ==========================================

  processes: Proceso[] = [];

  @ViewChild(ResultsTable)
  resultsTable!: ResultsTable;

  // ==========================================
  // Buscar procesos
  // ==========================================

  search(filters: SearchRequest): void {
    this.processSearchService.search(filters).subscribe({
      next: (response: Proceso[]) => {
        this.processes = response;
      },

      error: (error: unknown) => {
        console.error('Error al consultar procesos:', error);
      },
    });
  }

  // ==========================================
  // Limpiar resultados
  // ==========================================

  clearResults(): void {
    this.processes = [];

    this.resultsTable?.clearSearch();
  }
}
