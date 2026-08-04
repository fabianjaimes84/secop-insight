import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

const ORIGEN = 'secop-insight';

export interface ProgresoCola {
  restantes: number;
  total: number;
}

/**
 * Comunicación con la extensión del navegador.
 *
 * La app no puede hablarle directamente a la extensión, así que envía
 * mensajes a la ventana y el script 'puente.js' los reenvía.
 */
@Injectable({
  providedIn: 'root',
})
export class ExtensionService {

  private readonly extensionDisponibleSubject = new BehaviorSubject<boolean>(false);
  private readonly progresoSubject = new BehaviorSubject<ProgresoCola>({
    restantes: 0,
    total: 0,
  });

  /** true cuando la extensión está instalada y respondiendo. */
  readonly extensionDisponible$: Observable<boolean> =
    this.extensionDisponibleSubject.asObservable();

  /** Cuántos procesos quedan por actualizar en la cola. */
  readonly progreso$: Observable<ProgresoCola> = this.progresoSubject.asObservable();

  constructor() {
    window.addEventListener('message', (evento) => {
      if (evento.source !== window) {
        return;
      }

      const datos = evento.data;
      if (!datos || datos.origen !== ORIGEN) {
        return;
      }

      if (datos.accion === 'extensionLista') {
        this.extensionDisponibleSubject.next(true);
      }

      if (datos.accion === 'progresoCola') {
        this.progresoSubject.next({
          restantes: datos.restantes ?? 0,
          total: datos.total ?? 0,
        });
      }

      if (datos.accion === 'actualizarEnLoteRespuesta' && datos.respuesta) {
        this.progresoSubject.next({
          restantes: datos.respuesta.total ?? 0,
          total: datos.respuesta.total ?? 0,
        });
      }
    });
  }

  /** Abre los procesos uno por uno para capturarlos. */
  actualizarEnLote(urls: string[]): void {
    window.postMessage(
      {
        origen: ORIGEN,
        haciaExtension: true,
        accion: 'actualizarEnLote',
        urls,
      },
      '*'
    );
  }

  /** Detiene la cola, sin cerrar la pestaña que esté abierta. */
  cancelarCola(): void {
    window.postMessage(
      { origen: ORIGEN, haciaExtension: true, accion: 'cancelarCola' },
      '*'
    );
    this.progresoSubject.next({ restantes: 0, total: 0 });
  }
}
