import {
  Component,
  EventEmitter,
  HostListener,
  Input,
  Output,
  OnChanges,
  SimpleChanges,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Proceso } from '../../../core/models/proceso';

@Component({
  selector: 'app-process-detail',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './process-detail.html',
  styleUrl: './process-detail.scss',
})
export class ProcessDetail implements OnChanges {
  @Input() open = false;
  @Input() process: Proceso | null = null;
  @Output() close = new EventEmitter<void>();

  // Control de la pestaña activa
  activeTab: 'informacion' | 'cronograma' | 'documentos' | 'observaciones' = 'informacion';

  // Definición de las pestañas
  tabs = [
    { id: 'informacion' as const, label: 'Información', icon: 'fa-solid fa-circle-info' },
    { id: 'cronograma' as const, label: 'Cronograma', icon: 'fa-solid fa-calendar-days' },
    { id: 'documentos' as const, label: 'Documentos', icon: 'fa-solid fa-folder-open' },
    { id: 'observaciones' as const, label: 'Observaciones y mensajes', icon: 'fa-solid fa-comments' },
  ];

  ngOnChanges(changes: SimpleChanges) {
    // Reiniciar a la primera pestaña cada vez que se abre el modal
    if (changes['open'] && changes['open'].currentValue === true) {
      this.activeTab = 'informacion';
    }
  }

  selectTab(tab: 'informacion' | 'cronograma' | 'documentos' | 'observaciones') {
    this.activeTab = tab;
  }

  closeModal() {
    this.close.emit();
  }

  @HostListener('document:keydown.escape')
  onEscape() {
    if (this.open) this.closeModal();
  }

  // Helpers de formato
  formatCurrency(value: number | null | undefined): string {
    if (value === null || value === undefined) return 'No definido';
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(value);
  }

  formatDate(dateString: string | null | undefined): string {
    if (!dateString) return 'No definida';
    return new Date(dateString).toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' });
  }

  // Genera el cronograma dinámicamente basado en las fechas del proceso
  get cronograma() {
    if (!this.process) return [];
    
    return [
      { titulo: 'Publicación del proceso', fecha: this.formatDate(this.process.fecha_de_publicacion_del), estado: 'Completado' },
      { titulo: 'Cierre de recepción de ofertas', fecha: this.formatDate(this.process.fecha_de_recepcion_de), estado: 'Completado' },
      { titulo: 'Apertura de ofertas', fecha: this.formatDate(this.process.fecha_de_apertura_efectiva), estado: 'Completado' },
      { titulo: 'Adjudicación', fecha: this.formatDate(this.process.fecha_adjudicacion), estado: this.process.fecha_adjudicacion ? 'Completado' : 'Pendiente' },
    ];
  }
}