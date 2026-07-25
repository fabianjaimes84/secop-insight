// ==========================================
// Componente: ProcessDetail
// ------------------------------------------
// Este componente muestra el detalle de un
// proceso de contratación dentro de un modal.
//
// En esta primera versión permitirá:
//
// - Mostrar u ocultar el modal.
// - Recibir el proceso seleccionado.
// - Cerrar mediante:
//   • Botón X.
//   • Clic sobre el fondo.
//   • Tecla ESC.
//
// Posteriormente se agregarán:
//
// - Información.
// - Cronograma.
// - Documentos.
// - Observaciones.
// ==========================================

import {
  Component,
  EventEmitter,
  HostListener,
  Input,
  Output,
} from '@angular/core';

import { Proceso } from '../../../core/models/proceso';

@Component({
  selector: 'app-process-detail',
  standalone: true,
  imports: [],
  templateUrl: './process-detail.html',
  styleUrl: './process-detail.scss',
})
export class ProcessDetail {

  // ==========================================
  // Entradas del componente
  // ==========================================

  /**
   * Controla la visibilidad del modal.
   */
  @Input()
  open = false;

  /**
   * Proceso seleccionado desde la tabla.
   */
  @Input()
  process: Proceso | null = null;

  // ==========================================
  // Eventos
  // ==========================================

  /**
   * Notifica al componente padre que el
   * modal debe cerrarse.
   */
  @Output()
  close = new EventEmitter<void>();

  // ==========================================
  // Métodos públicos
  // ==========================================

  /**
   * Solicita el cierre del modal.
   */
  closeModal(): void {
    this.close.emit();
  }

  /**
   * Cierra el modal cuando el usuario
   * presiona la tecla ESC.
   */
  @HostListener('document:keydown.escape')
  onEscape(): void {

    if (!this.open) {
      return;
    }

    this.closeModal();

  }

}

