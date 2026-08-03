import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class HtmlDescargaService {

  // URL base del backend (mismo patrón que SearchService)
  private readonly API_URL = 'http://localhost:8000';
  private readonly BASE = `${this.API_URL}/html-descarga`;

  constructor(private http: HttpClient) {}

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