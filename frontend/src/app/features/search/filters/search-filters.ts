import { Component, EventEmitter, Output, OnInit, inject } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';

import { Card } from '../../../shared/ui/card/card';

import { SearchRequest } from '../models/search-request.model';
import { SearchService } from '../services/search.service';

@Component({
  selector: 'app-search-filters',
  standalone: true,
  imports: [Card, ReactiveFormsModule],
  templateUrl: './search-filters.html',
  styleUrl: './search-filters.scss',
})
export class SearchFilters implements OnInit {

  // ==========================================
  // Inyección de dependencias
  // ==========================================

  private readonly fb = inject(FormBuilder);
  private readonly searchService = inject(SearchService);

  // ==========================================
  // Eventos
  // ==========================================

  @Output()
  readonly onSearch = new EventEmitter<SearchRequest>();

  @Output()
  readonly onClear = new EventEmitter<void>();

  // ==========================================
  // Estado del componente
  // ==========================================

  searchForm: FormGroup;

  estados: string[] = [];

  tiposProceso: string[] = [];

  constructor() {
    this.searchForm = this.fb.group({
      buscar: [''],
      estado: [''],
      tipo_proceso: [''],
      fecha_publicacion_desde: [''],
      fecha_publicacion_hasta: [''],
    });
  }

  // ==========================================
  // Inicialización
  // ==========================================

  ngOnInit(): void {
    this.searchService.getCatalogos().subscribe({
      next: (catalogos) => {
        this.estados = catalogos.estados;

        this.tiposProceso = catalogos.tipos_proceso;
      },

      error: (error: unknown) => {
        console.error('Error cargando catálogos:', error);
      },
    });
  }

  // ==========================================
  // Limpiar filtros
  // ==========================================

  private limpiarFiltros(filtros: SearchRequest): SearchRequest {
    return {
      buscar: filtros.buscar?.trim() || null,

      estado: filtros.estado || null,

      tipo_proceso: filtros.tipo_proceso || null,

      fecha_publicacion_desde: filtros.fecha_publicacion_desde || null,

      fecha_publicacion_hasta: filtros.fecha_publicacion_hasta || null,

      limit: 50,
    };
  }

  // ==========================================
  // Buscar
  // ==========================================

  search(): void {
    const filtros = this.limpiarFiltros(this.searchForm.getRawValue());
    
    // Asegurar que las fechas se envíen en formato YYYY-MM-DD
    if (filtros.fecha_publicacion_desde && filtros.fecha_publicacion_desde.includes('/')) {
      const [day, month, year] = filtros.fecha_publicacion_desde.split('/');
      filtros.fecha_publicacion_desde = `${year}-${month}-${day}`;
    }
    
    if (filtros.fecha_publicacion_hasta && filtros.fecha_publicacion_hasta.includes('/')) {
      const [day, month, year] = filtros.fecha_publicacion_hasta.split('/');
      filtros.fecha_publicacion_hasta = `${year}-${month}-${day}`;
    }
    
    console.log('Filtros enviados al backend:', filtros);
    this.onSearch.emit(filtros);
  }

  // ==========================================
  // Limpiar
  // ==========================================

  clear(): void {
    this.searchForm.reset({
      buscar: '',
      estado: '',
      tipo_proceso: '',
      fecha_publicacion_desde: '',
      fecha_publicacion_hasta: '',
    });

    this.onClear.emit();
  }
}
