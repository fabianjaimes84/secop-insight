import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

import { Proceso } from '../models/proceso';

const CLAVE_STORAGE = 'secop_seguimiento_favoritos';

/** Un proceso guardado en Seguimiento, con su estado de gestión. */
export interface FavoritoGuardado {
  proceso: Proceso;
  /** true si ya se envió la oferta para este proceso. */
  ofertaEnviada: boolean;
  /** Fecha (ISO) en que se agregó a Seguimiento. */
  fechaAgregado: string;
}

@Injectable({
  providedIn: 'root',
})
export class FavoritosService {

  private readonly favoritosSubject = new BehaviorSubject<FavoritoGuardado[]>(
    this.cargarDesdeStorage()
  );

  /** Lista reactiva de procesos guardados en Seguimiento. */
  readonly favoritos$: Observable<FavoritoGuardado[]> = this.favoritosSubject.asObservable();

  private cargarDesdeStorage(): FavoritoGuardado[] {
    try {
      const guardado = localStorage.getItem(CLAVE_STORAGE);
      if (!guardado) {
        return [];
      }

      const datos = JSON.parse(guardado);

      // Compatibilidad: si viene de una versión anterior que solo guardaba
      // el Proceso directo (sin ofertaEnviada), se envuelve automáticamente.
      return datos.map((item: any) =>
        item && item.proceso
          ? item
          : {
              proceso: item,
              ofertaEnviada: false,
              fechaAgregado: new Date().toISOString(),
            }
      );
    } catch {
      return [];
    }
  }

  private guardarEnStorage(lista: FavoritoGuardado[]): void {
    try {
      localStorage.setItem(CLAVE_STORAGE, JSON.stringify(lista));
    } catch {
      // Si el storage falla (modo privado, cuota llena, etc.) simplemente
      // no persiste entre sesiones, pero la app sigue funcionando.
    }
  }

  /** Identificador único de un proceso, para no duplicarlo en la lista. */
  private idDe(proceso: Proceso): string {
    return proceso.id_del_proceso || proceso.referencia_del_proceso;
  }

  /** true si el proceso ya está guardado en Seguimiento. */
  esFavorito(proceso: Proceso): boolean {
    const id = this.idDe(proceso);
    return this.favoritosSubject.value.some((f) => this.idDe(f.proceso) === id);
  }

  /** Agrega el proceso si no estaba, o lo quita si ya estaba guardado. */
  alternar(proceso: Proceso): void {
    const id = this.idDe(proceso);
    const actual = this.favoritosSubject.value;
    const yaExiste = actual.some((f) => this.idDe(f.proceso) === id);

    const nuevaLista: FavoritoGuardado[] = yaExiste
      ? actual.filter((f) => this.idDe(f.proceso) !== id)
      : [
          ...actual,
          {
            proceso,
            ofertaEnviada: false,
            fechaAgregado: new Date().toISOString(),
          },
        ];

    this.favoritosSubject.next(nuevaLista);
    this.guardarEnStorage(nuevaLista);
  }

  /** Quita un proceso puntual de la lista (usado desde Seguimiento). */
  quitar(proceso: Proceso): void {
    const id = this.idDe(proceso);
    const nuevaLista = this.favoritosSubject.value.filter(
      (f) => this.idDe(f.proceso) !== id
    );
    this.favoritosSubject.next(nuevaLista);
    this.guardarEnStorage(nuevaLista);
  }

  /** Marca o desmarca si ya se envió la oferta para un proceso guardado. */
  marcarOfertaEnviada(proceso: Proceso, enviada: boolean): void {
    const id = this.idDe(proceso);
    const nuevaLista = this.favoritosSubject.value.map((f) =>
      this.idDe(f.proceso) === id ? { ...f, ofertaEnviada: enviada } : f
    );
    this.favoritosSubject.next(nuevaLista);
    this.guardarEnStorage(nuevaLista);
  }
}
