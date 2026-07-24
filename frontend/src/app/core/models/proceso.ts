export interface Proceso {
  // Información de la Entidad
  entidad: string;
  nit_entidad: string;
  departamento_entidad: string;
  ciudad_entidad: string;
  ordenentidad: string;
  codigo_entidad: number | null;

  // Información del Proceso
  id_del_proceso: string;
  referencia_del_proceso: string;
  nombre_del_procedimiento: string;
  descripci_n_del_procedimiento: string;
  fase: string;
  estado_resumen: string;
  estado_del_procedimiento: string;
  id_estado_del_procedimiento: number | null;

  // Contratación
  modalidad_de_contratacion: string;
  justificaci_n_modalidad_de: string;
  tipo_de_contrato: string;
  subtipo_de_contrato: string;
  duracion: number | null;
  unidad_de_duracion: string;

  // Fechas
  fecha_de_publicacion_del: string;
  fecha_de_ultima_publicaci: string;
  fecha_de_recepcion_de: string;
  fecha_de_apertura_de_respuesta: string;
  fecha_de_apertura_efectiva: string;
  fecha_adjudicacion: string;

  // Información Económica
  precio_base: number | null;
  adjudicado: string;
  valor_total_adjudicacion: number | null;

  // Proveedor Adjudicado
  codigoproveedor: string;
  nombre_del_proveedor: string;
  nit_del_proveedor_adjudicado: string;
  departamento_proveedor: string;
  ciudad_proveedor: string;

  // Estadísticas
  proveedores_invitados: number | null;
  proveedores_con_invitacion: number | null;
  proveedores_que_manifestaron: number | null;
  respuestas_al_procedimiento: number | null;
  respuestas_externas: number | null;
  conteo_de_respuestas_a_ofertas: number | null;
  proveedores_unicos_con: number | null;
  visualizaciones_del: number | null;
  numero_de_lotes: number | null;

  // Clasificación
  codigo_principal_de_categoria: string;
  categorias_adicionales: string;

  // Enlace
  urlproceso: string;
}