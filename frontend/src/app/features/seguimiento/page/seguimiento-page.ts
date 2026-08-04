import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { combineLatest, map, Observable, startWith, switchMap } from 'rxjs';

import { Proceso } from '../../../core/models/proceso';
import { FavoritosService, FavoritoGuardado } from '../../../core/services/favoritos.service';
import { HtmlDescargaService } from '../../search/services/html-descarga.service';
import { ProcessDetail } from '../../search/detail/process-detail';

/** Un favorito con el dato de última descarga traído del backend. */
interface FavoritoConEstado {
  favorito: FavoritoGuardado;
  ultimaActualizacion: string;
  /** Fecha de cierre para presentar la oferta (viene del cronograma). */
  fechaPresentacion: string;
  zonaPresentacion: string;
}

interface GruposSeguimiento {
  noEnviadas: FavoritoConEstado[];
  enviadas: FavoritoConEstado[];
  total: number;
}

@Component({
  selector: 'app-seguimiento-page',
  standalone: true,
  imports: [CommonModule, ProcessDetail],
  templateUrl: './seguimiento-page.html',
})
export class SeguimientoPage implements OnInit {

  grupos$!: Observable<GruposSeguimiento>;

  selectedProcess: Proceso | null = null;
  detailOpen = false;

  constructor(
    private favoritosService: FavoritosService,
    private htmlDescargaService: HtmlDescargaService
  ) {}

  ngOnInit(): void {
    this.grupos$ = combineLatest([
      this.favoritosService.favoritos$,
      // Se vuelve a consultar cada vez que la extensión captura un proceso,
      // así la fecha de actualización se refresca sola.
      this.htmlDescargaService.capturaDetectada$.pipe(
        switchMap(() => this.htmlDescargaService.listarProcesos()),
        startWith<any[]>([])
      ),
    ]).pipe(
      map(([favoritos, importados]) => {
        const conEstado: FavoritoConEstado[] = favoritos.map((f) => {
          const importado = this.buscarImportado(
            f.proceso.referencia_del_proceso,
            importados
          );

          return {
            favorito: f,
            ultimaActualizacion: importado?.ultima_actualizacion || '',
            fechaPresentacion: importado?.fecha_presentacion_ofertas || '',
            zonaPresentacion: importado?.zona_presentacion_ofertas || '',
          };
        });

        return {
          noEnviadas: conEstado.filter((c) => !c.favorito.ofertaEnviada),
          enviadas: conEstado.filter((c) => c.favorito.ofertaEnviada),
          total: conEstado.length,
        };
      })
    );
  }

  /** Empareja el favorito con su versión importada, usando el código base. */
  private buscarImportado(referenciaProceso: string, importados: any[]): any {
    const codigo = this.htmlDescargaService.extraerCodigoCarpeta(referenciaProceso);
    return importados.find(
      (p) => this.htmlDescargaService.extraerCodigoCarpeta(p.numero_proceso) === codigo
    );
  }

  /** Día del mes de la fecha de presentación, para mostrarlo grande. */
  diaPresentacion(fecha: string, zona: string): string {
    const parseada = this.parsearFecha(fecha, zona);
    return parseada ? String(parseada.getDate()) : '–';
  }

  /** Mes y año de la fecha de presentación (ej. "ago 2026"). */
  mesPresentacion(fecha: string, zona: string): string {
    const parseada = this.parsearFecha(fecha, zona);
    if (!parseada) {
      return '';
    }
    return parseada.toLocaleString('es-CO', { month: 'short', year: 'numeric' });
  }

  /** Hora de la fecha de presentación (ej. "9:00 a. m."). */
  horaPresentacion(fecha: string, zona: string): string {
    const parseada = this.parsearFecha(fecha, zona);
    if (!parseada) {
      return '';
    }
    return parseada.toLocaleString('es-CO', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  }

  /** Días que faltan para el cierre (negativo si ya pasó). */
  diasRestantes(fecha: string, zona: string): number | null {
    const parseada = this.parsearFecha(fecha, zona);
    if (!parseada) {
      return null;
    }
    const msPorDia = 1000 * 60 * 60 * 24;
    return Math.ceil((parseada.getTime() - new Date().getTime()) / msPorDia);
  }

  /**
   * La fecha real puede venir directa, o escondida dentro del texto de la
   * zona horaria cuando el campo 'fecha' trae algo relativo
   * (ej. "3 días para terminar").
   */
  private parsearFecha(fecha: string, zonaHoraria: string): Date | null {
    const patron = /(\d{1,2})\/(\d{1,2})\/(\d{4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM)?/i;
    const coincidencia = (fecha || '').match(patron) || (zonaHoraria || '').match(patron);
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

  /**
   * Quita la fase que SECOP añade al final del número de proceso.
   * Ej: "CMA-DEO-SGI-028-2026 (Presentación de oferta)" -> "CMA-DEO-SGI-028-2026"
   */
  numeroProcesoLimpio(referencia: string): string {
    return (referencia || '').trim().split(' ')[0];
  }

  /** Muestra la fecha de descarga del HTML en formato legible. */
  formatearUltimaActualizacion(iso: string): string {
    if (!iso) {
      return 'Sin actualizar';
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

  quitar(favorito: FavoritoGuardado, evento: Event): void {
    evento.stopPropagation();
    this.favoritosService.quitar(favorito.proceso);
  }

  alternarOferta(favorito: FavoritoGuardado, evento: Event): void {
    evento.stopPropagation();
    const checkbox = evento.target as HTMLInputElement;
    this.favoritosService.marcarOfertaEnviada(favorito.proceso, checkbox.checked);
  }

  openDetail(proceso: Proceso): void {
    this.selectedProcess = proceso;
    this.detailOpen = true;
  }

  closeDetail(): void {
    this.detailOpen = false;
    this.selectedProcess = null;
  }

  formatMoneda(valor: number | string | null | undefined): string {
    if (valor === null || valor === undefined || valor === '') return '$ 0,00';
    return '$ ' + Number(valor).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  getEstadoClass(estado: string): string {
    const value = (estado ?? '').toLowerCase();
    if (value.includes('public')) return 'bg-blue-100 text-blue-700';
    if (value.includes('oferta') || value.includes('concurso')) return 'bg-green-50 text-green-600';
    if (value.includes('observaciones')) return 'bg-yellow-50 text-yellow-600';
    if (value.includes('cancel') || value.includes('revocado') || value.includes('anormal')) return 'bg-red-100 text-red-700';
    if (value.includes('celebrado')) return 'bg-indigo-100 text-indigo-700';
    return 'bg-slate-100 text-slate-700';
  }
}
