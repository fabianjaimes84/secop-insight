import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { combineLatest, map, Observable, startWith } from 'rxjs';

import { Proceso } from '../../../core/models/proceso';
import { FavoritosService, FavoritoGuardado } from '../../../core/services/favoritos.service';
import { HtmlDescargaService } from '../../search/services/html-descarga.service';
import { ProcessDetail } from '../../search/detail/process-detail';

/** Un favorito con el dato de última descarga traído del backend. */
interface FavoritoConEstado {
  favorito: FavoritoGuardado;
  ultimaActualizacion: string;
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
      this.htmlDescargaService.listarProcesos().pipe(startWith<any[]>([])),
    ]).pipe(
      map(([favoritos, importados]) => {
        const conEstado: FavoritoConEstado[] = favoritos.map((f) => ({
          favorito: f,
          ultimaActualizacion: this.buscarUltimaActualizacion(
            f.proceso.referencia_del_proceso,
            importados
          ),
        }));

        return {
          noEnviadas: conEstado.filter((c) => !c.favorito.ofertaEnviada),
          enviadas: conEstado.filter((c) => c.favorito.ofertaEnviada),
          total: conEstado.length,
        };
      })
    );
  }

  /** Empareja el favorito con su versión importada, usando el código base. */
  private buscarUltimaActualizacion(
    referenciaProceso: string,
    importados: any[]
  ): string {
    const codigo = this.htmlDescargaService.extraerCodigoCarpeta(referenciaProceso);
    const encontrado = importados.find(
      (p) => this.htmlDescargaService.extraerCodigoCarpeta(p.numero_proceso) === codigo
    );
    return encontrado?.ultima_actualizacion || '';
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
