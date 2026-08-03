import {
  Component,
  ElementRef,
  EventEmitter,
  HostListener,
  Input,
  OnChanges,
  Output,
  SimpleChanges,
} from '@angular/core';
import { CommonModule } from '@angular/common';

import { Proceso } from '../../../core/models/proceso';
import { HtmlDescargaService } from '../services/html-descarga.service';

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

  constructor(
    private htmlDescargaService: HtmlDescargaService,
    private elementRef: ElementRef
  ) {}

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

  // Datos reales de SECOP II (se llenan automáticamente al abrir el modal)
  datosHtmlDescarga: any = null;
  cargandoHtmlDescarga = false;
  errorHtmlDescarga: string | null = null;
  carpetaNoEncontrada = false;

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
      this.datosHtmlDescarga = null;
      this.errorHtmlDescarga = null;
      this.carpetaNoEncontrada = false;
      this.actualizarDesdeSecopII();
    }

  }

  // ==========================================
  // SECOP II (html-descarga)
  // ==========================================

  actualizarDesdeSecopII(): void {

    if (!this.process?.referencia_del_proceso) {
      return;
    }

    this.cargandoHtmlDescarga = true;
    this.errorHtmlDescarga = null;
    this.carpetaNoEncontrada = false;

    const codigo = this.htmlDescargaService.extraerCodigoCarpeta(
      this.process.referencia_del_proceso
    );

    this.htmlDescargaService
      .actualizarDesdeCarpeta(codigo)
      .subscribe({
        next: (datos) => {
          this.datosHtmlDescarga = datos;
          this.cargandoHtmlDescarga = false;

          if (this.activeTab === 'cronograma') {
            this.desplazarA('[data-cercano="true"]');
          } else if (this.activeTab === 'documentos') {
            this.desplazarA('[data-documento-reciente="true"]');
          }
        },
        error: (err) => {
          this.cargandoHtmlDescarga = false;

          if (err?.status === 404) {
            // La carpeta del proceso todavía no existe: no es un error real,
            // solo significa que aún no se ha importado nada.
            this.carpetaNoEncontrada = true;
            return;
          }

          this.errorHtmlDescarga =
            err?.error?.detail || 'No se pudo cargar la información adicional.';
        },
      });

  }

  /**
   * Desplaza el contenido de la pestaña activa hasta el elemento marcado
   * con el atributo data-* indicado, sin que el usuario tenga que
   * buscarlo manualmente (ej. el evento más cercano a hoy, o el
   * documento más reciente).
   */
  private desplazarA(selectorAtributo: string): void {

    setTimeout(() => {
      const elemento = this.elementRef.nativeElement.querySelector(
        selectorAtributo
      );
      elemento?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });

  }

  secopIIUrl(enlaceRelativo: string): string {
    return `https://community.secop.gov.co${enlaceRelativo}`;
  }

  // ==========================================
  // Cronograma SECOP II: evento más cercano a hoy
  // ==========================================

  /**
   * Extrae una fecha real (d/m/yyyy hh:mm:ss AM/PM) de un evento del
   * cronograma. Algunos eventos traen la fecha directa en 'fecha', y otros
   * la traen como texto relativo ("30 días de tiempo transcurrido") con la
   * fecha real escondida dentro de 'zona_horaria'. Se intenta primero un
   * campo y luego el otro.
   */
  private parsearFechaEvento(evento: {
    fecha: string;
    zona_horaria: string;
  }): Date | null {

    const patron = /(\d{1,2})\/(\d{1,2})\/(\d{4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM)?/i;

    const coincidencia =
      evento.fecha.match(patron) || evento.zona_horaria.match(patron);

    if (!coincidencia) {
      return null;
    }

    const [, dia, mes, anio, horas12, minutos, segundos, ampm] = coincidencia;
    let horas = parseInt(horas12, 10);

    if (ampm) {
      const esPM = ampm.toUpperCase() === 'PM';
      if (esPM && horas < 12) horas += 12;
      if (!esPM && horas === 12) horas = 0;
    }

    return new Date(
      parseInt(anio, 10),
      parseInt(mes, 10) - 1,
      parseInt(dia, 10),
      horas,
      parseInt(minutos, 10),
      segundos ? parseInt(segundos, 10) : 0
    );

  }

  /** Índice del evento del cronograma cuya fecha está más cerca de hoy. */
  get indiceEventoCercano(): number {

    const eventos = this.datosHtmlDescarga?.cronograma;
    if (!eventos?.length) {
      return -1;
    }

    const ahora = new Date().getTime();
    let mejorIndice = -1;
    let menorDiferencia = Infinity;

    eventos.forEach((evento: any, indice: number) => {
      const fecha = this.parsearFechaEvento(evento);
      if (!fecha) {
        return;
      }
      const diferencia = Math.abs(fecha.getTime() - ahora);
      if (diferencia < menorDiferencia) {
        menorDiferencia = diferencia;
        mejorIndice = indice;
      }
    });

    return mejorIndice;

  }

  // ==========================================
  // Documentos: documento más reciente
  // ==========================================

  /**
   * El nombre del documento no trae fecha, pero el enlace de descarga trae
   * un 'documentFileId' que aumenta con cada archivo subido a SECOP II. Se
   * usa ese número para identificar el documento subido más recientemente.
   */
  private extraerIdDocumento(enlace: string): number {
    const coincidencia = enlace.match(/documentFileId=(\d+)/);
    return coincidencia ? parseInt(coincidencia[1], 10) : -1;
  }

  /** Índice del documento subido más recientemente (mayor documentFileId). */
  get indiceDocumentoReciente(): number {

    const documentos = this.datosHtmlDescarga?.documentos;
    if (!documentos?.length) {
      return -1;
    }

    let mejorIndice = 0;
    let mayorId = this.extraerIdDocumento(documentos[0].enlace);

    documentos.forEach((doc: any, indice: number) => {
      const id = this.extraerIdDocumento(doc.enlace);
      if (id > mayorId) {
        mayorId = id;
        mejorIndice = indice;
      }
    });

    return mejorIndice;

  }

  // ==========================================
  // Documentos: palabras clave a destacar
  // ==========================================

  private readonly PALABRAS_CLAVE_DOCUMENTOS = [
    'pliego',
    'definitivo',
    'cronograma',
    'anexo tecnico',
    'documento base',
    'resolucion',
    'apertura',
    'respuesta',
    'observaciones',
    'adenda',
    'presupuesto', 
  ];

  /** Quita tildes y pasa a minúsculas, para comparar sin importar acentos. */
  private normalizarTexto(texto: string): string {
    return texto
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase();
  }

  /** true si el nombre del documento contiene alguna palabra clave importante. */
  esDocumentoDestacado(nombreDocumento: string): boolean {
    const normalizado = this.normalizarTexto(nombreDocumento);
    return this.PALABRAS_CLAVE_DOCUMENTOS.some((palabra) =>
      normalizado.includes(palabra)
    );
  }

  // ==========================================
  // Navegación
  // ==========================================

  selectTab(tab: DetailTab): void {
    this.activeTab = tab;

    if (tab === 'cronograma') {
      this.desplazarA('[data-cercano="true"]');
    } else if (tab === 'documentos') {
      this.desplazarA('[data-documento-reciente="true"]');
    }
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