export interface SearchRequest {
  buscar: string | null;
  estado: string | null;
  tipo_proceso: string | null;
  tipo_contrato: string | null; // NUEVO CAMPO
  fecha_publicacion_desde: string | null;
  fecha_publicacion_hasta: string | null;
  limit: number;
}