export interface BusquedaProceso {
  buscar?: string;
  estado?: string;
  tipo_proceso?: string;

  fecha_publicacion_desde?: string;
  fecha_publicacion_hasta?: string;

  limit?: number;
}