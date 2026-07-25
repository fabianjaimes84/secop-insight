import { Component, Input } from '@angular/core';

import { Proceso } from '../../../../core/models/proceso';
import { Card } from '../../../../shared/ui/card/card';
import { ProcessDetail } from '../../../../shared/components/process-detail/process-detail';
import { SMMLV } from '../../../../core/constants/app.constants';

@Component({
  selector: 'app-results-table',
  standalone: true,
  imports: [
    Card,
    ProcessDetail,
  ],
  templateUrl: './results-table.html',
  styleUrl: './results-table.scss',
})
export class ResultsTable {

  // ==========================================
  // Datos recibidos desde la página de búsqueda
  // ==========================================

  @Input()
  processes: Proceso[] = [];

  // ==========================================
  // Estado del modal
  // ==========================================
  // Controla el proceso seleccionado y la
  // apertura del modal de detalle.
  // ==========================================

  selectedProcess: Proceso | null = null;

  detailOpen = false;

  // ==========================================
  // Abre el detalle del proceso seleccionado.
  // ==========================================

  openDetail(process: Proceso): void {

    this.selectedProcess = process;
    this.detailOpen = true;

  }

  // ==========================================
  // Cierra el modal y limpia el proceso
  // seleccionado.
  // ==========================================

  closeDetail(): void {

    this.detailOpen = false;
    this.selectedProcess = null;

  }

  // ==========================================
  // Devuelve la clase CSS según el estado
  // del proceso para mostrar una etiqueta
  // con un color representativo.
  // ==========================================

  getEstadoClass(estado: string): string {

    const value = (estado ?? '').toLowerCase();

    if (value.includes('public')) {
      return 'bg-green-100 text-green-700';
    }

    if (
      value.includes('oferta') ||
      value.includes('concurso') ||
      value.includes('observacion')
    ) {
      return 'bg-yellow-100 text-yellow-700';
    }

    if (
      value.includes('adjudicado') ||
      value.includes('evaluacion')
    ) {
      return 'bg-blue-100 text-blue-700';
    }

    if (
      value.includes('cancel') ||
      value.includes('revocado') ||
      value.includes('anormal')
    ) {
      return 'bg-red-100 text-red-700';
    }

    if (value.includes('celebrado')) {
      return 'bg-indigo-100 text-indigo-700';
    }

    return 'bg-slate-100 text-slate-700';

  }

  // ==========================================
  // Formatea una fecha para mostrar:
  //
  // 24/07/2026
  // 08:30 a. m.
  // ==========================================

  formatFecha(fecha: string | null | undefined): string[] {

    if (!fecha) {
      return ['', ''];
    }

    const date = new Date(fecha);

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
  // Formatea valores monetarios.
  // ==========================================

  formatMoneda(valor: number | string | null | undefined): string {

    if (
      valor === null ||
      valor === undefined ||
      valor === ''
    ) {
      return '$ 0,00';
    }

    return '$ ' + Number(valor).toLocaleString(
      'es-CO',
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }
    );

  }

  // ==========================================
  // Calcula la cuantía equivalente en SMMLV.
  // ==========================================

  formatSMMLV(valor: number | string | null | undefined): string {

    if (
      valor === null ||
      valor === undefined ||
      valor === ''
    ) {
      return '0,00 SMMLV';
    }

    return (
      (
        Number(valor) / SMMLV
      ).toLocaleString(
        'es-CO',
        {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        }
      ) + ' SMMLV'
    );

  }

}