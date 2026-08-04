import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { SMMLV } from '../../../core/constants/app.constants';
import { Proceso } from '../../../core/models/proceso';
import { FavoritosService } from '../../../core/services/favoritos.service';

import { Card } from '../../../shared/ui/card/card';
import { ProcessDetail } from '../detail/process-detail';

@Component({
  selector: 'app-results-table',
  standalone: true,
  imports: [CommonModule, FormsModule, Card, ProcessDetail],
  templateUrl: './results-table.html',
  styleUrl: './results-table.scss',
})
export class ResultsTable implements OnChanges {

  constructor(private favoritosService: FavoritosService) {}

  // ==========================================
  // Datos recibidos desde la búsqueda
  // ==========================================
  @Input() processes: Proceso[] = [];

  // ==========================================
  // Configuración de Paginación (NUEVO)
  // ==========================================
  @Input() itemsPerPage: number = 10;
  @Input() currentPage: number = 1;
  @Input() isLoading: boolean = false;

  @Output() pageChange = new EventEmitter<number>();

  // ==========================================
  // Búsqueda en la tabla
  // ==========================================
  searchText = '';
  filteredProcesses: Proceso[] = [];

  // ==========================================
  // Variables internas de paginación
  // ==========================================
  paginatedProcesses: Proceso[] = [];
  totalPages = 0;

  // ==========================================
  // Ordenamiento
  // ==========================================
  sortColumn = '';
  sortDirection: 'asc' | 'desc' = 'asc';

  // ==========================================
  // Estado del modal
  // ==========================================
  selectedProcess: Proceso | null = null;
  detailOpen = false;

  // ==========================================
  // Actualizar resultados y recalcular paginación
  // ==========================================
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['processes'] || changes['currentPage'] || changes['itemsPerPage']) {
      this.currentPage = 1;
      this.filteredProcesses = [...this.processes];
      this.applyFilterAndSort();
      this.updatePagination();
    }
  }

  // ==========================================
  // Lógica de Paginación
  // ==========================================
  private updatePagination(): void {
    if (this.itemsPerPage <= 0) {
      this.paginatedProcesses = this.filteredProcesses;
      this.totalPages = 1;
      return;
    }

    this.totalPages = Math.max(1, Math.ceil(this.filteredProcesses.length / this.itemsPerPage));

    if (this.currentPage > this.totalPages) {
      this.currentPage = this.totalPages;
    } else if (this.currentPage < 1) {
      this.currentPage = 1;
    }

    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;

    this.paginatedProcesses = this.filteredProcesses.slice(startIndex, endIndex);
  }

  // Método auxiliar para reaplicar filtros/orden al cambiar datos
  private applyFilterAndSort(): void {
    if (this.searchText) {
      this.filterTableLogic();
    }
    if (this.sortColumn) {
      this.sortLogic();
    }
    // Si no hay filtro ni orden, updatePagination ya trabajará sobre la copia completa
  }

  // ==========================================
  // Navegación de Páginas
  // ==========================================
  goToPage(page: number | string): void {
    if (typeof page !== 'number') {
      return;
    }

    if (page < 1 || page > this.totalPages || page === this.currentPage) {
      return;
    }

    this.currentPage = page;
    this.updatePagination();
    this.pageChange.emit(this.currentPage);

    setTimeout(() => {
      const searchSection = document.querySelector('app-search') || document.querySelector('.search-page');
      if (searchSection) {
        searchSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }, 0);
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.goToPage(this.currentPage + 1);
    } else {
      // Si estamos en la última página calculada, emitimos el evento
      // para que el padre decida si carga más datos del backend
      this.pageChange.emit(this.currentPage + 1);
    }
  }

  prevPage(): void {
    if (this.currentPage > 1) {
      this.goToPage(this.currentPage - 1);
    }
  }

  // ==========================================
  // Getter para páginas visibles (Lógica de puntos suspensivos)
  // ==========================================
  get visiblePages(): (number | string)[] {
    const range = 2; // Cantidad de páginas a mostrar antes/después de la actual
    const pages: (number | string)[] = [];

    // Si hay pocas páginas (7 o menos), mostrar todas
    if (this.totalPages <= 7) {
      for (let i = 1; i <= this.totalPages; i++) {
        pages.push(i);
      }
      return pages;
    }

    // Si la página actual está cerca del inicio (páginas 1, 2, 3, 4)
    if (this.currentPage <= range + 1) {
      for (let i = 1; i <= range * 2 + 2; i++) {
        pages.push(i);
      }
      pages.push('...');
      pages.push(this.totalPages);
      return pages;
    }

    // Si la página actual está cerca del final
    if (this.currentPage >= this.totalPages - range) {
      pages.push(1);
      pages.push('...');
      for (let i = this.totalPages - (range * 2 + 1); i <= this.totalPages; i++) {
        pages.push(i);
      }
      return pages;
    }

    // Si la página actual está en el medio
    pages.push(1);
    pages.push('...');
    for (let i = this.currentPage - range; i <= this.currentPage + range; i++) {
      pages.push(i);
    }
    pages.push('...');
    pages.push(this.totalPages);

    return pages;
  }

  // ==========================================
  // Abrir/Cerrar Detalle
  // ==========================================
  openDetail(process: Proceso): void {
    this.selectedProcess = process;
    this.detailOpen = true;
  }

  closeDetail(): void {
    this.detailOpen = false;
    this.selectedProcess = null;
  }

  // ==========================================
  // Favoritos / Seguimiento
  // ==========================================

  /**
   * Quita la fase que SECOP añade al final del número de proceso.
   * Ej: "CMA-DEO-SGI-028-2026 (Presentación de oferta)" -> "CMA-DEO-SGI-028-2026"
   */
  numeroProcesoLimpio(referencia: string): string {
    return (referencia || '').trim().split(' ')[0];
  }

  esFavorito(process: Proceso): boolean {
    return this.favoritosService.esFavorito(process);
  }

  alternarFavorito(process: Proceso): void {
    this.favoritosService.alternar(process);
  }

  // ==========================================
  // Filtrar tabla
  // ==========================================
  filterTable(): void {
    this.filterTableLogic();
    this.currentPage = 1;
    this.updatePagination();
    this.pageChange.emit(this.currentPage);
  }

  private filterTableLogic(): void {
    const value = this.searchText.toLowerCase().trim();
    if (!value) {
      this.filteredProcesses = [...this.processes];
      return;
    }
    this.filteredProcesses = this.processes.filter((process) => {
      return JSON.stringify(process).toLowerCase().includes(value);
    });
  }

  clearSearch(): void {
    this.searchText = '';
    this.filteredProcesses = [...this.processes];
    this.currentPage = 1;
    this.updatePagination();
    this.pageChange.emit(this.currentPage);
  }

  // ==========================================
  // Ordenar tabla
  // ==========================================
  sort(column: keyof Proceso): void {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
    this.sortLogic();
    this.updatePagination(); // Recalcular tras ordenar
    this.currentPage = 1;
    this.pageChange.emit(this.currentPage);
  }

  private sortLogic(): void {
    this.filteredProcesses.sort((a, b) => {
      // CORRECCIÓN TS7053: Usar 'as keyof Proceso' para acceso seguro
      const col = this.sortColumn as keyof Proceso;
      const valueA = (a[col] ?? '').toString().toLowerCase();
      const valueB = (b[col] ?? '').toString().toLowerCase();

      const comparison = valueA.localeCompare(valueB, 'es', { numeric: true });
      return this.sortDirection === 'asc' ? comparison : -comparison;
    });
  }

  // ==========================================
  // Utilidades Visuales (Clases, Fechas, Moneda)
  // ==========================================
  getEstadoClass(estado: string): string {
    const value = (estado ?? '').toLowerCase();
    if (value.includes('public')) return 'bg-blue-100 text-blue-700';
    if (value.includes('oferta') || value.includes('concurso') || value.includes('Presentación')) return 'bg-green-50 text-green-600';
    if (value.includes('observaciones') || value.includes('Presentación')) return 'bg-yellow-50 text-yellow-600';
    if (value.includes('cancel') || value.includes('revocado') || value.includes('anormal')) return 'bg-red-100 text-red-700';
    if (value.includes('celebrado')) return 'bg-indigo-100 text-indigo-700';
    return 'bg-slate-100 text-slate-700';
  }

  formatFecha(fecha: string | null | undefined): string[] {
    if (!fecha) return ['', ''];
    const fechaStr = fecha.includes('T') ? fecha.split('T')[0] : fecha;
    const [year, month, day] = fechaStr.split('-').map(Number);
    const date = new Date(year, month - 1, day);
    return [
      new Intl.DateTimeFormat('es-CO', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(date),
      new Intl.DateTimeFormat('es-CO', { hour: '2-digit', minute: '2-digit', hour12: true }).format(date),
    ];
  }

  formatMoneda(valor: number | string | null | undefined): string {
    if (valor === null || valor === undefined || valor === '') return '$ 0,00';
    return '$ ' + Number(valor).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  formatSMMLV(valor: number | string | null | undefined): string {
    if (valor === null || valor === undefined || valor === '') return '0,00 SMMLV';
    return (Number(valor) / SMMLV).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' SMMLV';
  }

  getSortIcon(column: keyof Proceso): string {
    if (this.sortColumn !== column) return '↕';
    return this.sortDirection === 'asc' ? '▲' : '▼';
  }
}
