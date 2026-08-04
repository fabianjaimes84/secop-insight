import { Component, ElementRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { combineLatest, map, Observable, startWith, switchMap } from 'rxjs';

import { Proceso } from '../../../core/models/proceso';
import { FavoritosService, FavoritoGuardado } from '../../../core/services/favoritos.service';
import { HtmlDescargaService } from '../../search/services/html-descarga.service';
import { ProcessDetail } from '../../search/detail/process-detail';

/** Fila para la lista de "Activos", con el próximo evento pendiente. */
interface ItemActivo {
  numeroProceso: string;
  entidad: string;
  proximoEventoNombre: string;
  proximoEventoFecha: string;
  proximoEventoZona: string;
  eventoAnteriorNombre: string;
  eventoAnteriorFecha: string;
  eventoAnteriorZona: string;
  /** Fecha ya parseada, para ordenar y para mostrar en grande. */
  fechaParseada: Date | null;
  ultimaActualizacion: string;
  /** Proceso completo, para poder abrir el modal de detalle. */
  proceso: Proceso;
}

/** Grupo de procesos activos que comparten el mismo evento de cronograma. */
interface GrupoActivos {
  evento: string;
  color: string;
  items: ItemActivo[];
}

/** Fila simple para la lista de "Favoritos". */
interface ItemSimple {
  numeroProceso: string;
  entidad: string;
  descripcion: string;
  estado: string;
  ultimaActualizacion: string;
  proceso: Proceso;
}

/** Fila para la lista de "Próximos a cerrar", con más detalle. */
interface ItemProximoACerrar {
  numeroProceso: string;
  entidad: string;
  fase: string;
  fecha: string;
  zonaHoraria: string;
  fechaAdenda: string;
  zonaAdenda: string;
  ultimaActualizacion: string;
  proceso: Proceso;
}

interface EstadisticasDashboard {
  activos: number;
  proximosACerrar: number;
  favoritos: number;
  listaActivos: ItemActivo[];
  gruposActivos: GrupoActivos[];
  listaProximosACerrar: ItemProximoACerrar[];
  listaFavoritos: ItemSimple[];
}

/**
 * Color asignado a cada tipo de evento del cronograma, para distinguirlos
 * de un vistazo. Se compara con el nombre normalizado (sin tildes).
 */
const COLORES_EVENTO: { patron: string; color: string }[] = [
  { patron: 'adjudicacion', color: 'purple' },
  { patron: 'informe de evaluacion', color: 'blue' },
  { patron: 'evaluacion de las ofertas', color: 'blue' },
  { patron: 'informe de presentacion', color: 'teal' },
  { patron: 'presentacion de ofertas', color: 'orange' },
  { patron: 'apertura de ofertas', color: 'amber' },
  { patron: 'observaciones', color: 'yellow' },
  { patron: 'adendas', color: 'pink' },
  { patron: 'firma del contrato', color: 'green' },
  { patron: 'garantias', color: 'emerald' },
  { patron: 'poliza', color: 'emerald' },
];

/** Cuántos días antes del cierre empieza a contar como "próximo a cerrar". */
const DIAS_VENTANA_ALERTA = 5;

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, ProcessDetail],
  templateUrl: './dashboard.html',
})
export class Dashboard implements OnInit {

  estadisticas$!: Observable<EstadisticasDashboard>;

  /**
   * Número del proceso sobre el que está el cursor. Sirve para resaltarlo
   * simultáneamente en las tres columnas (Activos, Próximos a cerrar y
   * Favoritos), y así ver de un vistazo dónde más aparece.
   */
  procesoResaltado: string | null = null;

  /** Compara ignorando la fase entre paréntesis, mayúsculas y espacios. */
  esResaltado(numeroProceso: string): boolean {
    if (!this.procesoResaltado || !numeroProceso) {
      return false;
    }
    return (
      this.codigoBase(numeroProceso) === this.codigoBase(this.procesoResaltado)
    );
  }

  private codigoBase(numeroProceso: string): string {
    return numeroProceso.trim().split(' ')[0].toLowerCase();
  }

  // ==========================================
  // Expansión al hacer clic + modal de detalle
  // ==========================================

  /** Proceso actualmente expandido (se muestra su detalle ampliado). */
  procesoExpandido: string | null = null;

  selectedProcess: Proceso | null = null;
  detailOpen = false;

  /** Abre o cierra el detalle ampliado de un proceso. */
  alternarExpansion(numeroProceso: string): void {
    this.procesoExpandido =
      this.procesoExpandido === numeroProceso ? null : numeroProceso;
  }

  estaExpandido(numeroProceso: string): boolean {
    return this.procesoExpandido === numeroProceso;
  }

  /**
   * Al hacer clic en un favorito, no se despliega ahí mismo: se busca ese
   * proceso en la columna "Procesos activos", se expande allá y se hace
   * scroll hasta él, aunque estuviera escondido más abajo en su grupo.
   */
  expandirEnActivos(numeroProceso: string): void {
    this.procesoExpandido = numeroProceso;

    setTimeout(() => {
      const elemento = this.elementRef.nativeElement.querySelector(
        `[data-activo="${CSS.escape(numeroProceso)}"]`
      );
      elemento?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  }

  /** Abre el modal completo del proceso (el mismo del buscador). */
  abrirModal(proceso: Proceso, evento: Event): void {
    evento.stopPropagation();
    this.selectedProcess = proceso;
    this.detailOpen = true;
  }

  cerrarModal(): void {
    this.detailOpen = false;
    this.selectedProcess = null;
  }

  /**
   * Quita la fase que SECOP añade al final del número de proceso.
   * Ej: "CMA-DEO-SGI-028-2026 (Presentación de oferta)" -> "CMA-DEO-SGI-028-2026"
   */
  numeroProcesoLimpio(referencia: string): string {
    return (referencia || '').trim().split(' ')[0];
  }

  /** Muestra la última actualización en formato legible. */
  formatearUltimaActualizacion(iso: string): string {
    if (!iso) {
      return 'Sin importar todavía';
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

  constructor(
    private favoritosService: FavoritosService,
    private htmlDescargaService: HtmlDescargaService,
    private elementRef: ElementRef
  ) {}

  ngOnInit(): void {
    // Se combinan los favoritos (localStorage) con la lista de procesos ya
    // importados (backend). La lista del backend se vuelve a pedir cada vez
    // que la extensión captura un proceso, así el tablero se actualiza solo.
    this.estadisticas$ = combineLatest([
      this.favoritosService.favoritos$,
      this.htmlDescargaService.capturaDetectada$.pipe(
        switchMap(() => this.htmlDescargaService.listarProcesos()),
        startWith<any[]>([])
      ),
    ]).pipe(
      map(([favoritos, procesosImportados]) =>
        this.calcularEstadisticas(favoritos, procesosImportados)
      )
    );
  }

  private calcularEstadisticas(
    favoritos: FavoritoGuardado[],
    procesosImportados: any[]
  ): EstadisticasDashboard {

    // Favoritos: todos, tal cual están guardados en Seguimiento.
    const listaFavoritos: ItemSimple[] = favoritos.map((f) => {
      const importado = this.buscarImportadoCoincidente(
        f.proceso.referencia_del_proceso,
        procesosImportados
      );
      return {
        numeroProceso: f.proceso.referencia_del_proceso,
        entidad: f.proceso.entidad,
        descripcion: f.proceso.descripci_n_del_procedimiento || '',
        estado: importado?.estado || f.proceso.estado_resumen || '',
        ultimaActualizacion: importado?.ultima_actualizacion || '',
        proceso: f.proceso,
      };
    });

    // Activos: favoritos con oferta ya enviada, con su próximo evento pendiente.
    const listaActivos: ItemActivo[] = favoritos
      .filter((f) => f.ofertaEnviada)
      .map((f) => {
        const importado = this.buscarImportadoCoincidente(
          f.proceso.referencia_del_proceso,
          procesosImportados
        );
        const fechaTexto = importado?.proximo_evento_fecha || '';
        const zonaTexto = importado?.proximo_evento_zona || '';

        return {
          numeroProceso: f.proceso.referencia_del_proceso,
          entidad: f.proceso.entidad,
          proximoEventoNombre: importado?.proximo_evento_nombre || '',
          proximoEventoFecha: fechaTexto,
          proximoEventoZona: zonaTexto,
          eventoAnteriorNombre: importado?.evento_anterior_nombre || '',
          eventoAnteriorFecha: importado?.evento_anterior_fecha || '',
          eventoAnteriorZona: importado?.evento_anterior_zona || '',
          fechaParseada: this.parsearFecha(fechaTexto, zonaTexto),
          ultimaActualizacion: importado?.ultima_actualizacion || '',
          proceso: f.proceso,
        };
      });

    const gruposActivos = this.agruparPorEvento(listaActivos);

    // Próximos a cerrar: sin oferta, importado, publicado, y dentro de la ventana de días.
    const listaProximosACerrar: ItemProximoACerrar[] = [];

    for (const favorito of favoritos) {
      if (favorito.ofertaEnviada) {
        continue;
      }

      const importado = this.buscarImportadoCoincidente(
        favorito.proceso.referencia_del_proceso,
        procesosImportados
      );
      if (!importado?.fecha_presentacion_ofertas) {
        continue;
      }

      if (!this.esEstadoPublicado(importado.estado)) {
        continue;
      }

      const fechaCierre = this.parsearFecha(
        importado.fecha_presentacion_ofertas,
        importado.zona_presentacion_ofertas
      );
      if (!fechaCierre) {
        continue;
      }

      const diasRestantes = this.diasHasta(fechaCierre);
      if (diasRestantes >= 0 && diasRestantes <= DIAS_VENTANA_ALERTA) {
        listaProximosACerrar.push({
          numeroProceso: importado.numero_proceso,
          entidad: importado.entidad,
          fase: importado.fase,
          fecha: importado.fecha_presentacion_ofertas,
          zonaHoraria: importado.zona_presentacion_ofertas,
          fechaAdenda: importado.fecha_adenda || '',
          zonaAdenda: importado.zona_adenda || '',
          ultimaActualizacion: importado.ultima_actualizacion || '',
          proceso: favorito.proceso,
        });
      }
    }

    return {
      activos: listaActivos.length,
      proximosACerrar: listaProximosACerrar.length,
      favoritos: listaFavoritos.length,
      listaActivos,
      gruposActivos,
      listaProximosACerrar,
      listaFavoritos,
    };

  }

  /** Empareja un favorito de SECOP II con su versión importada, por código base. */
  private buscarImportadoCoincidente(
    referenciaProceso: string,
    procesosImportados: any[]
  ): any | undefined {
    const codigo = this.htmlDescargaService.extraerCodigoCarpeta(referenciaProceso);
    return procesosImportados.find(
      (p) => this.htmlDescargaService.extraerCodigoCarpeta(p.numero_proceso) === codigo
    );
  }

  /**
   * Agrupa los procesos activos por tipo de evento del cronograma.
   * Dentro de cada grupo ordena por fecha (más cercana primero), y los
   * grupos también se ordenan por su fecha más cercana.
   */
  private agruparPorEvento(items: ItemActivo[]): GrupoActivos[] {
    const mapa = new Map<string, ItemActivo[]>();

    for (const item of items) {
      const clave = item.proximoEventoNombre || 'Sin evento pendiente';
      const existentes = mapa.get(clave) ?? [];
      existentes.push(item);
      mapa.set(clave, existentes);
    }

    const grupos: GrupoActivos[] = [];

    mapa.forEach((itemsDelGrupo, evento) => {
      itemsDelGrupo.sort(
        (a, b) =>
          (a.fechaParseada?.getTime() ?? Infinity) -
          (b.fechaParseada?.getTime() ?? Infinity)
      );
      grupos.push({
        evento,
        color: this.colorDeEvento(evento),
        items: itemsDelGrupo,
      });
    });

    // Orden descendente: los eventos más avanzados del cronograma
    // (adjudicación, evaluación) aparecen primero, y los más inmediatos
    // al final. Dentro de cada grupo se mantiene la fecha más cercana arriba.
    grupos.sort(
      (a, b) =>
        (b.items[0]?.fechaParseada?.getTime() ?? -Infinity) -
        (a.items[0]?.fechaParseada?.getTime() ?? -Infinity)
    );

    return grupos;
  }

  /** Devuelve el color asociado al tipo de evento (ver COLORES_EVENTO). */
  private colorDeEvento(evento: string): string {
    const normalizado = evento
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase();

    const encontrado = COLORES_EVENTO.find((c) => normalizado.includes(c.patron));
    return encontrado?.color ?? 'slate';
  }

  /** Día del mes, para mostrarlo grande (ej. "5"). */
  diaDeFecha(fecha: string, zonaHoraria: string): string {
    const parseada = this.parsearFecha(fecha, zonaHoraria);
    return parseada ? String(parseada.getDate()) : '–';
  }

  /** Mes, año y hora, para la línea pequeña bajo el día (ej. "ago 2026, 9:00 a. m."). */
  restoDeFecha(fecha: string, zonaHoraria: string): string {
    const parseada = this.parsearFecha(fecha, zonaHoraria);
    if (!parseada) {
      return '';
    }
    return parseada.toLocaleString('es-CO', {
      month: 'short',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  }

  /**
   * Muestra solo fecha y hora, sin el texto técnico "(UTC-05:00) Bogotá,
   * Lima, Quito)" que trae el dato crudo de SECOP I.
   */
  formatearFecha(fecha: string, zonaHoraria: string): string {
    const parseada = this.parsearFecha(fecha, zonaHoraria);
    if (!parseada) {
      return fecha || 'Sin fecha';
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

  /** Igual que en el modal de detalle: entiende fecha directa o "X días de..." con la fecha real en zona_horaria. */
  private parsearFecha(fecha: string, zonaHoraria: string): Date | null {
    const patron = /(\d{1,2})\/(\d{1,2})\/(\d{4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM)?/i;
    const coincidencia = fecha.match(patron) || zonaHoraria.match(patron);
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

  /** Compara el estado ignorando mayúsculas y tildes ("Publicado" = "publicado"). */
  private esEstadoPublicado(estado: string): boolean {
    if (!estado) {
      return false;
    }
    const normalizado = estado
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .trim();
    return normalizado === 'publicado';
  }

  private diasHasta(fecha: Date): number {
    const ahora = new Date();
    const msPorDia = 1000 * 60 * 60 * 24;
    return Math.ceil((fecha.getTime() - ahora.getTime()) / msPorDia);
  }
}
