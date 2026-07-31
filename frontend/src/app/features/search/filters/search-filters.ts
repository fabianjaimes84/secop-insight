import { Component, EventEmitter, Output, OnInit, inject, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
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
export class SearchFilters implements OnInit, AfterViewInit {

  // ==========================================
  // Inyección de dependencias
  // ==========================================

  private readonly fb = inject(FormBuilder);
  private readonly searchService = inject(SearchService);

  // ==========================================
  // Referencias al DOM
  // ==========================================
  
  @ViewChild('buscarInput') buscarInput!: ElementRef<HTMLInputElement>;

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
    
    // Establecer fechas por defecto al iniciar
    this.setFechasPorDefecto();
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

  ngAfterViewInit(): void {
    // Enfocar el campo buscar al cargar la vista
    if (this.buscarInput) {
      this.buscarInput.nativeElement.focus();
    }
  }

  // ==========================================
  // Utilidades
  // ==========================================

  private setFechasPorDefecto(): void {
    const today = new Date();
    const oneMonthAgo = new Date();
    oneMonthAgo.setMonth(today.getMonth() - 1);

    const formatDate = (date: Date): string => {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    };

    this.searchForm.patchValue({
      fecha_publicacion_desde: formatDate(oneMonthAgo),
      fecha_publicacion_hasta: formatDate(today),
    });
  }

  // ==========================================
  // Limpiar filtros
  // ==========================================

  private limpiarFiltros(filtros: any): SearchRequest {
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
    const formValues = this.searchForm.getRawValue();
    const filtros = this.limpiarFiltros(formValues);
    
    // Normalizar fechas si vienen en formato DD/MM/YYYY (por seguridad)
    const normalizeDate = (dateStr: string | null | undefined): string | null => {
      if (!dateStr) return null;
      if (dateStr.includes('/')) {
        const [day, month, year] = dateStr.split('/');
        return `${year}-${month}-${day}`;
      }
      return dateStr;
    };

    filtros.fecha_publicacion_desde = normalizeDate(filtros.fecha_publicacion_desde);
    filtros.fecha_publicacion_hasta = normalizeDate(filtros.fecha_publicacion_hasta);

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
    });

    // Restablecer fechas por defecto
    this.setFechasPorDefecto();

    this.onClear.emit();

    // MOVER EL FOCO AL CAMPO BUSCAR PARA EVITAR QUE ENTER VUELVA A LIMPIAR
    setTimeout(() => {
      if (this.buscarInput) {
        this.buscarInput.nativeElement.focus();
      }
    }, 0);
  }
}