import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';

import { Card } from '../../../../shared/ui/card/card';
import { SearchRequest } from '../../models/search-request.model';
import { SearchService } from '../../services/search.service';

@Component({
  selector: 'app-search-filters',
  standalone: true,
  imports: [Card, ReactiveFormsModule],
  templateUrl: './search-filters.html',
  styleUrl: './search-filters.scss',
})
export class SearchFilters implements OnInit {
  @Output()
  readonly onSearch = new EventEmitter<SearchRequest>();

  searchForm: FormGroup;

  estados: string[] = [];

  tiposProceso: string[] = [];

  constructor(
    private fb: FormBuilder,
    private searchService: SearchService,
  ) {
    const defaults = this.getDefaultFilters();

    this.searchForm = this.fb.group({
      buscar: [defaults.buscar],
      estado: [defaults.estado],
      tipo_proceso: [defaults.tipo_proceso],
      fecha_publicacion_desde: [defaults.fecha_publicacion_desde],
      fecha_publicacion_hasta: [defaults.fecha_publicacion_hasta],
      fecha_presentacion_desde: [defaults.fecha_presentacion_desde],
      fecha_presentacion_hasta: [defaults.fecha_presentacion_hasta],
      limit: [defaults.limit],
    });
  }

  ngOnInit(): void {
    this.searchService.getCatalogos().subscribe({
      next: (catalogos) => {
        console.log('Catálogos recibidos');
        console.log(catalogos);

        this.estados = catalogos.estados;
        this.tiposProceso = catalogos.tipos_proceso;

        console.log(this.estados);
        console.log(this.tiposProceso);
      },
      error: (error) => {
        console.error('Error cargando catálogos:', error);
      },
    });
  }

  private getDefaultFilters(): SearchRequest {
    const today = new Date();

    const publicationFrom = new Date(today);
    publicationFrom.setMonth(publicationFrom.getMonth() - 3);

    const presentationTo = new Date(today);
    presentationTo.setMonth(presentationTo.getMonth() + 1);

    const format = (date: Date): string => date.toISOString().split('T')[0];

    return {
      buscar: '',
      estado: '',
      tipo_proceso: '',
      fecha_publicacion_desde: format(publicationFrom),
      fecha_publicacion_hasta: format(today),
      fecha_presentacion_desde: format(today),
      fecha_presentacion_hasta: format(presentationTo),
      limit: 50,
    };
  }

  search(): void {
    console.log('Filtros enviados:');
    console.log(this.searchForm.getRawValue());

    this.onSearch.emit(this.searchForm.getRawValue());
  }

  clear(): void {
    this.searchForm.reset(this.getDefaultFilters());
  }
}
