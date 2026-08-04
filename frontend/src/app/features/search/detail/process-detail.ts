import {
  Component,
  ElementRef,
  EventEmitter,
  HostListener,
  Input,
  OnChanges,
  OnDestroy,
  OnInit,
  Output,
  SimpleChanges,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';

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
export class ProcessDetail implements OnChanges, OnInit, OnDestroy {

  private suscripcionCaptura?: Subscription;

  constructor(
    private htmlDescargaService: HtmlDescargaService,
    private elementRef: ElementRef
  ) {}

  ngOnInit(): void {
    // Si la extensión captura un proceso mientras el modal está abierto,
    // se recargan sus datos automáticamente.
    this.suscripcionCaptura = this.htmlDescargaService.capturaDetectada$
      .subscribe(() => {
        if (this.open && this.process) {
          this.consultarDatosGuardados();
        }
      });
  }

  ngOnDestroy(): void {
    this.suscripcionCaptura?.unsubscribe();
  }

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

  private readonly todasLasTabs = [
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

  /**
   * Mientras el proceso no se haya capturado desde SECOP, las pestañas de
   * Cronograma, Documentos y Observaciones no tienen contenido real, así
   * que solo se muestra Información. Las cuatro aparecen en cuanto llegan
   * los datos ampliados.
   */
  get tabs() {
    return this.datosHtmlDescarga
      ? this.todasLasTabs
      : this.todasLasTabs.filter((tab) => tab.id === 'informacion');
  }

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
      this.consultarDatosGuardados();
    }

  }

  // ==========================================
  // SECOP II (html-descarga)
  // ==========================================

  /**
   * Al abrir el modal solo se consulta lo que ya está guardado en la base
   * de datos. No se dispara ninguna importación: los datos ampliados llegan
   * cuando el proceso se captura desde SECOP con la extensión del navegador.
   */
  consultarDatosGuardados(): void {

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
      .obtenerPorCodigo(codigo)
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
            // El proceso todavía no se ha capturado desde SECOP: se muestran
            // únicamente los datos que ya trae la búsqueda (SECOP II).
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

  /** Muestra la última actualización (ISO) en formato legible. */
  formatearUltimaActualizacion(iso: string): string {
    if (!iso) {
      return 'Sin registro';
    }
    const fecha = new Date(iso);
    if (isNaN(fecha.getTime())) {
      return iso;
    }
    return fecha.toLocaleString('es-CO', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  }

  /**
   * true si la información guardada tiene más de 12 horas. Sirve para
   * sugerirle al usuario volver a capturar el proceso desde SECOP.
   */
  get datosDesactualizados(): boolean {
    const iso = this.datosHtmlDescarga?.ultima_actualizacion;
    if (!iso) {
      return false;
    }

    const fecha = new Date(iso);
    if (isNaN(fecha.getTime())) {
      return false;
    }

    const horasTranscurridas =
      (new Date().getTime() - fecha.getTime()) / (1000 * 60 * 60);

    return horasTranscurridas >= 12;
  }

  /** Cuántas horas (redondeadas) tiene la información guardada. */
  get horasDesdeActualizacion(): number {
    const iso = this.datosHtmlDescarga?.ultima_actualizacion;
    if (!iso) {
      return 0;
    }
    const fecha = new Date(iso);
    return Math.floor(
      (new Date().getTime() - fecha.getTime()) / (1000 * 60 * 60)
    );
  }

  /**
   * Quita la fase que SECOP añade al final del número de proceso.
   * Ej: "CMA-DEO-SGI-028-2026 (Presentación de oferta)" -> "CMA-DEO-SGI-028-2026"
   */
  numeroProcesoLimpio(referencia: string): string {
    return (referencia || '').trim().split(' ')[0];
  }

  /**
   * Muestra solo fecha y hora del evento, sin el texto técnico
   * "(UTC-05:00) Bogotá, Lima, Quito)" que trae el dato crudo.
   */
  formatearFechaEvento(evento: { fecha: string; zona_horaria: string }): string {
    const parseada = this.parsearFechaEvento(evento);
    if (!parseada) {
      return evento.fecha || 'Sin fecha';
    }

    return parseada.toLocaleString('es-CO', {
      day: 'numeric',
      month: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  }

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