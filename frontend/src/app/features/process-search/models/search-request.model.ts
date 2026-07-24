export interface SearchRequest {
  buscar?: string | null;

  estado?: string | null;

  tipo_proceso?: string | null;

  fecha_publicacion_desde?: string | null;

  fecha_publicacion_hasta?: string | null;

  fecha_presentacion_desde?: string | null;

  fecha_presentacion_hasta?: string | null;

  limit?: number;
}
