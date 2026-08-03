import { Injectable } from '@angular/core';

import { Proceso } from '../../../core/models/proceso';
import { SearchRequest } from '../models/search-request.model';

/**
 * Guarda el último estado de la búsqueda (filtros usados y resultados
 * obtenidos) en memoria, como singleton de la app. Así, si el usuario
 * navega a otra pestaña (ej. Seguimiento) y vuelve a Buscar Procesos,
 * no pierde lo que ya tenía.
 */
@Injectable({
  providedIn: 'root',
})
export class SearchStateService {

  /** Últimos valores del formulario de filtros (para restaurarlos en los campos). */
  ultimosFiltros: Record<string, any> | null = null;

  /** Últimos resultados obtenidos del backend. */
  processes: Proceso[] = [];

  guardarBusqueda(filtros: Record<string, any>, processes: Proceso[]): void {
    this.ultimosFiltros = filtros;
    this.processes = processes;
  }

  limpiar(): void {
    this.ultimosFiltros = null;
    this.processes = [];
  }
}
