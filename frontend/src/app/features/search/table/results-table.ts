import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { SMMLV } from '../../../core/constants/app.constants';
import { Proceso } from '../../../core/models/proceso';

import { Card } from '../../../shared/ui/card/card';

import { ProcessDetail } from '../detail/process-detail';

@Component({
  selector: 'app-results-table',
  standalone: true,
  imports: [FormsModule, Card, ProcessDetail],
  templateUrl: './results-table.html',
  styleUrl: './results-table.scss',
})
export class ResultsTable implements OnChanges {
  // ==========================================
  // Datos recibidos desde la búsqueda
  // ==========================================

  @Input()
  processes: Proceso[] = [];

  // ==========================================
  // Búsqueda en la tabla
  // ==========================================

  searchText = '';

  filteredProcesses: Proceso[] = [];

  // ==========================================
  // Ordenamiento
  // ==========================================

  sortColumn = '';

  sortDirection: 'asc' | 'desc' = 'asc';

  // ==========================================
  // Actualizar resultados
  // ==========================================

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['processes']) {
      this.filteredProcesses = [...this.processes];
    }
  }

  // ==========================================
  // Estado del modal
  // ==========================================

  selectedProcess: Proceso | null = null;

  detailOpen = false;

  // ==========================================
  // Abrir detalle
  // ==========================================

  openDetail(process: Proceso): void {
    this.selectedProcess = process;
    this.detailOpen = true;
  }

  // ==========================================
  // Cerrar detalle
  // ==========================================

  closeDetail(): void {
    this.detailOpen = false;
    this.selectedProcess = null;
  }

  // ==========================================
  // Filtrar tabla
  // ==========================================

  filterTable(): void {
    const value = this.searchText.toLowerCase().trim();

    if (!value) {
      this.filteredProcesses = [...this.processes];
      return;
    }

    this.filteredProcesses = this.processes.filter((process) => {
      return JSON.stringify(process).toLowerCase().includes(value);
    });
  }

  // ==========================================
  // Limpiar búsqueda de la tabla
  // ==========================================

  clearSearch(): void {
    this.searchText = '';
    this.filteredProcesses = [];
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

    this.filteredProcesses.sort((a, b) => {
      const valueA = (a[column] ?? '').toString().toLowerCase();
      const valueB = (b[column] ?? '').toString().toLowerCase();

      const comparison = valueA.localeCompare(valueB, 'es', {
        numeric: true,
      });

      return this.sortDirection === 'asc' ? comparison : -comparison;
    });
  }

  // ==========================================
  // Clase CSS del estado
  // ==========================================

  getEstadoClass(estado: string): string {
    const value = (estado ?? '').toLowerCase();

    if (value.includes('public')) {
      return 'bg-blue-100 text-blue-700';
    }

    if (value.includes('oferta') || value.includes('concurso') || value.includes('Presentación')) {
      return 'bg-green-50 text-green-600';
    }

    if (value.includes('observaciones') || value.includes('Presentación')) {
      return 'bg-yellow-50 text-yellow-600';
    }

    if (value.includes('cancel') || value.includes('revocado') || value.includes('anormal')) {
      return 'bg-red-100 text-red-700';
    }

    if (value.includes('celebrado')) {
      return 'bg-indigo-100 text-indigo-700';
    }

    return 'bg-slate-100 text-slate-700';
  }

  // ==========================================
  // Formatear fecha (CORREGIDO - sin desfase de timezone)
  // ==========================================
  formatFecha(fecha: string | null | undefined): string[] {
    if (!fecha) {
      return ['', ''];
    }

    // Extraer solo la parte de fecha (YYYY-MM-DD), ignorando hora y timezone
    const fechaStr = fecha.includes('T') ? fecha.split('T')[0] : fecha;
    const [year, month, day] = fechaStr.split('-').map(Number);
    
    // Crear fecha en zona horaria local para evitar desfase
    const date = new Date(year, month - 1, day);

    return [
      new Intl.DateTimeFormat('es-CO', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      }).format(date),
      new Intl.DateTimeFormat('es-CO', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true,
      }).format(date),
    ];
  }
  // ==========================================
  // Formatear moneda
  // ==========================================

  formatMoneda(valor: number | string | null | undefined): string {
    if (valor === null || valor === undefined || valor === '') {
      return '$ 0,00';
    }

    return (
      '$ ' +
      Number(valor).toLocaleString('es-CO', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })
    );
  }

  // ==========================================
  // Formatear SMMLV
  // ==========================================

  formatSMMLV(valor: number | string | null | undefined): string {
    if (valor === null || valor === undefined || valor === '') {
      return '0,00 SMMLV';
    }

    return (
      (Number(valor) / SMMLV).toLocaleString('es-CO', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }) + ' SMMLV'
    );
  }

  // ==========================================
  // Icono de ordenamiento
  // ==========================================

  getSortIcon(column: keyof Proceso): string {
    if (this.sortColumn !== column) {
      return '↕';
    }

    return this.sortDirection === 'asc' ? '▲' : '▼';
  }
}
