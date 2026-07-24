import { Component, Input } from '@angular/core';

import { Proceso } from '../../../../core/models/proceso';
import { Card } from '../../../../shared/ui/card/card';
import { SMMLV } from '../../../../core/constants/app.constants';

@Component({
  selector: 'app-results-table',
  standalone: true,
  imports: [Card],
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
  // Devuelve la clase CSS según el estado
  // del proceso para mostrar una etiqueta
  // con un color representativo.
  // ==========================================

  getEstadoClass(estado: string): string {

    const value = (estado ?? '').toLowerCase();

    // Procesos publicados
    if (value.includes('public')) {
      return 'bg-green-100 text-green-700';
    }

    // Procesos en etapa de ofertas o concurso
    if (
      value.includes('oferta') ||
      value.includes('concurso') ||
      value.includes('observacion')
    ) {
      return 'bg-yellow-100 text-yellow-700';
    }

    // Procesos adjudicados o en evaluación
    if (
      value.includes('adjudicado') ||
      value.includes('evaluacion')
    ) {
      return 'bg-blue-100 text-blue-700';
    }

    // Procesos cancelados o revocados
    if (
      value.includes('cancel') ||
      value.includes('revocado') ||
      value.includes('anormal')
    ) {
      return 'bg-red-100 text-red-700';
    }

    // Contratos celebrados
    if (value.includes('celebrado')) {
      return 'bg-indigo-100 text-indigo-700';
    }

    // Estado por defecto
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

    const fechaFormateada = new Intl.DateTimeFormat(
      'es-CO',
      {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      }
    ).format(date);

    const horaFormateada = new Intl.DateTimeFormat(
      'es-CO',
      {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true,
      }
    ).format(date);

    return [
      fechaFormateada,
      horaFormateada,
    ];

  }

  // ==========================================
  // Formatea valores monetarios.
  //
  // Ejemplo:
  // $ 130.000.000,00
  // ==========================================

  formatMoneda(valor: number | string | null | undefined): string {

    if (
      valor === null ||
      valor === undefined ||
      valor === ''
    ) {
      return '$ 0,00';
    }

    const numero = Number(valor);

    return '$ ' + numero.toLocaleString(
      'es-CO',
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }
    );

  }

  // ==========================================
  // Calcula el equivalente del presupuesto
  // en Salarios Mínimos Legales Mensuales
  // Vigentes (SMMLV).
  // ==========================================

  formatSMMLV(valor: number | string | null | undefined): string {

    if (
      valor === null ||
      valor === undefined ||
      valor === ''
    ) {
      return '0,00 SMMLV';
    }

    const numero = Number(valor);

    return (
      (numero / SMMLV).toLocaleString(
        'es-CO',
        {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        }
      ) + ' SMMLV'
    );

  }

  // ==========================================
  // Próximamente
  // ==========================================
  //
  // - Ver detalle del proceso.
  // - Guardar proceso en seguimiento.
  // - Ordenar por fecha de presentación.
  //
  // ==========================================

}