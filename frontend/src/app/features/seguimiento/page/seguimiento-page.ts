import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { map, Observable } from 'rxjs';

import { Proceso } from '../../../core/models/proceso';
import { FavoritosService, FavoritoGuardado } from '../../../core/services/favoritos.service';
import { ProcessDetail } from '../../search/detail/process-detail';

interface GruposSeguimiento {
  noEnviadas: FavoritoGuardado[];
  enviadas: FavoritoGuardado[];
  total: number;
}

@Component({
  selector: 'app-seguimiento-page',
  standalone: true,
  imports: [CommonModule, ProcessDetail],
  templateUrl: './seguimiento-page.html',
})
export class SeguimientoPage {

  readonly grupos$: Observable<GruposSeguimiento>;

  selectedProcess: Proceso | null = null;
  detailOpen = false;

  constructor(private favoritosService: FavoritosService) {
    this.grupos$ = this.favoritosService.favoritos$.pipe(
      map((favoritos) => ({
        noEnviadas: favoritos.filter((f) => !f.ofertaEnviada),
        enviadas: favoritos.filter((f) => f.ofertaEnviada),
        total: favoritos.length,
      }))
    );
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
