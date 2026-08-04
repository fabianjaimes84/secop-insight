import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, timer } from 'rxjs';
import {
  catchError,
  distinctUntilChanged,
  map,
  shareReplay,
  switchMap,
} from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class HtmlDescargaService {

  // URL base del backend (mismo patrón que SearchService)
  private readonly API_URL = 'http://localhost:8000';
  private readonly BASE = `${this.API_URL}/html-descarga`;

  /** Cada cuántos milisegundos se pregunta al backend si hubo capturas. */
  private readonly INTERVALO_SONDEO = 4000;

  constructor(private http: HttpClient) {}

  /**
   * Emite cada vez que la extensión captura un proceso nuevo. Los
   * componentes se suscriben para refrescar sus datos automáticamente,
   * sin que el usuario recargue la página.
   */
  readonly capturaDetectada$: Observable<string> = timer(0, this.INTERVALO_SONDEO).pipe(
    switchMap(() =>
      this.http
        .get<{ momento: string; numero_proceso: string }>(`${this.BASE}/ultima-captura`)
        .pipe(catchError(() => of({ momento: '', numero_proceso: '' })))
    ),
    map((estado) => estado.momento),
    distinctUntilChanged(),
    shareReplay(1)
  );

  /**
   * Busca en 'backend/documentos/{codigoProceso}/' el HTML descargado
   * manualmente de SECOP I, lo procesa y actualiza la base de datos.
   * Devuelve el detalle completo ya actualizado.
   */
  actualizarDesdeCarpeta(codigoProceso: string): Observable<any> {
    return this.http.post(
      `${this.BASE}/actualizar/${encodeURIComponent(codigoProceso)}`,
      {}
    );
  }

  /**
   * Consulta (sin importar ni modificar nada) la información ya guardada
   * de un proceso, a partir de su código base. Es lo que usa el modal.
   */
  obtenerPorCodigo(codigoProceso: string): Observable<any> {
    return this.http.get(
      `${this.BASE}/proceso-por-codigo/${encodeURIComponent(codigoProceso)}`
    );
  }

  /** Detalle completo de un proceso ya guardado, por su id interno. */
  obtenerDetalle(procesoId: number): Observable<any> {
    return this.http.get(`${this.BASE}/procesos/${procesoId}`);
  }

  /** Lista resumida de todos los procesos SECOP I guardados. */
  listarProcesos(): Observable<any> {
    return this.http.get(`${this.BASE}/procesos`);
  }

  /**
   * A partir del número de proceso de SECOP I/II (que puede traer la fase
   * pegada, ej. "CMA-DEO-SGI-028-2026 (Presentación de oferta)"), devuelve
   * solo el fragmento de números/guiones/letras antes del primer espacio,
   * que es el nombre real de la carpeta en documentos/.
   */
  extraerCodigoCarpeta(numeroProceso: string): string {
    return numeroProceso.trim().split(' ')[0];
  }
}
