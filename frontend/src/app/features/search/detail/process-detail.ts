import {
  Component,
  EventEmitter,
  HostListener,
  Input,
  OnChanges,
  Output,
  SimpleChanges,
} from '@angular/core';
import { CommonModule } from '@angular/common';

import { Proceso } from '../../../core/models/proceso';

type DetailTab =
  | 'informacion'
  | 'cronograma'
  | 'documentos'
  | 'observaciones';

@Component({
  selector: 'app-process-detail',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './process-detail.html',
  styleUrl: './process-detail.scss',
})
export class ProcessDetail implements OnChanges {

  // ==========================================
  // Inputs / Outputs
  // ==========================================

  @Input()
  open = false;

  @Input()
  process: Proceso | null = null;

  @Output()
  readonly close = new EventEmitter<void>();

  // ==========================================
  // Estado
  // ==========================================

  activeTab: DetailTab = 'informacion';

  readonly tabs = [
    {
      id: 'informacion' as const,
      label: 'Información',
      icon: 'fa-solid fa-circle-info',
    },
    {
      id: 'cronograma' as const,
      label: 'Cronograma',
      icon: 'fa-solid fa-calendar-days',
    },
    {
      id: 'documentos' as const,
      label: 'Documentos',
      icon: 'fa-solid fa-folder-open',
    },
    {
      id: 'observaciones' as const,
      label: 'Observaciones y mensajes',
      icon: 'fa-solid fa-comments',
    },
  ];

  // ==========================================
  // Ciclo de vida
  // ==========================================

  ngOnChanges(changes: SimpleChanges): void {

    if (
      changes['open'] &&
      changes['open'].currentValue === true
    ) {
      this.activeTab = 'informacion';
    }

  }

  // ==========================================
  // Navegación
  // ==========================================

  selectTab(tab: DetailTab): void {
    this.activeTab = tab;
  }

  closeModal(): void {
    this.close.emit();
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {

    if (this.open) {
      this.closeModal();
    }

  }

  // ==========================================
  // Formato
  // ==========================================

  formatCurrency(value: number | null | undefined): string {

    if (value === null || value === undefined) {
      return 'No definido';
    }

    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0,
    }).format(value);

  }

  formatDate(dateString: string | null | undefined): string {

    if (!dateString) {
      return 'No definida';
    }

    return new Date(dateString).toLocaleDateString(
      'es-CO',
      {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      }
    );

  }

  // ==========================================
  // Cronograma
  // ==========================================

  get cronograma() {

    if (!this.process) {
      return [];
    }

    return [
      {
        titulo: 'Publicación del proceso',
        fecha: this.formatDate(this.process.fecha_de_publicacion_del),
        estado: 'Completado',
      },
      {
        titulo: 'Cierre de recepción de ofertas',
        fecha: this.formatDate(this.process.fecha_de_recepcion_de),
        estado: 'Completado',
      },
      {
        titulo: 'Apertura de ofertas',
        fecha: this.formatDate(this.process.fecha_de_apertura_efectiva),
        estado: 'Completado',
      },
      {
        titulo: 'Adjudicación',
        fecha: this.formatDate(this.process.fecha_adjudicacion),
        estado: this.process.fecha_adjudicacion
          ? 'Completado'
          : 'Pendiente',
      },
    ];

  }

}