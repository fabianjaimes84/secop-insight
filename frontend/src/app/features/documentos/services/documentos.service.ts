import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Contador {
  id?: number;
  nombre: string;
  cedula: string;
  mat_profe: string;
  rol: 'contador' | 'revisor_fiscal';
}

export interface Accionista {
  id?: number;
  orden: number;
  nombre: string;
  cedula: string;
  porcentaje: string;
}

export interface Empresa {
  id?: number;
  nom_o_raz_social: string;
  nit: string;
  es_persona_juridica: boolean;

  repre_nombre: string;
  repre_cedula: string;
  repre_mat_profe: string;

  contac_direccion: string;
  contac_ciudad: string;
  contac_email: string;
  contac_tele: string;
  contac_telefax: string;

  contador_id: number | null;
  contador?: Contador | null;

  accionistas: Accionista[];
}

/** La participación de una empresa en un proponente, para esta oferta. */
export interface IntegranteProponente {
  id?: number;
  empresa_id: number;
  orden: number;
  compromiso: string;
  es_lider: boolean;

  pertenece_grupo: boolean;
  cotiza_bolsa: boolean;
  acredita_mujeres: boolean;
  acredita_discapacidad: boolean;
  acredita_mipyme: boolean;

  empresa?: Empresa;
}

export interface PerfilProponente {
  id?: number;
  tipo: 'natural' | 'consorcio' | 'union_temporal';
  nombre: string;
  codigo_proceso: string;
  representante_empresa_id: number | null;

  entidad_telefono: string;
  entidad_pagina: string;
  entidad_horario: string;
  entidad_correo: string;
  entidad_politica: string;

  fecha_cierre: string;
  fecha_carta_gerencia: string;

  pers_clave_eval: string;
  integrantes: IntegranteProponente[];
  representante_empresa?: Empresa | null;
}

export interface FechasProceso {
  fecha_cierre: string;
  zona_cierre: string;
  fecha_carta_gerencia: string;
}

export interface ItemChecklist {
  codigo: string;
  nombre: string;
  nombre_archivo: string;
  integrante: string;
  nota: string;
}

export interface RespuestaChecklist {
  numero_proceso: string;
  entidad: string;
  proponente: string;
  tipo_proponente: string;
  total: number;
  items: ItemChecklist[];
}

@Injectable({
  providedIn: 'root',
})
export class DocumentosService {

  private readonly API_URL = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  // ==========================================
  // Contadores
  // ==========================================

  listarContadores(): Observable<Contador[]> {
    return this.http.get<Contador[]>(`${this.API_URL}/contadores`);
  }

  crearContador(contador: Contador): Observable<Contador> {
    return this.http.post<Contador>(`${this.API_URL}/contadores`, contador);
  }

  actualizarContador(id: number, contador: Contador): Observable<Contador> {
    return this.http.put<Contador>(`${this.API_URL}/contadores/${id}`, contador);
  }

  eliminarContador(id: number): Observable<any> {
    return this.http.delete(`${this.API_URL}/contadores/${id}`);
  }

  // ==========================================
  // Empresas
  // ==========================================

  listarEmpresas(): Observable<Empresa[]> {
    return this.http.get<Empresa[]>(`${this.API_URL}/empresas`);
  }

  crearEmpresa(empresa: Empresa): Observable<Empresa> {
    return this.http.post<Empresa>(`${this.API_URL}/empresas`, empresa);
  }

  actualizarEmpresa(id: number, empresa: Empresa): Observable<Empresa> {
    return this.http.put<Empresa>(`${this.API_URL}/empresas/${id}`, empresa);
  }

  eliminarEmpresa(id: number): Observable<any> {
    return this.http.delete(`${this.API_URL}/empresas/${id}`);
  }

  // ==========================================
  // Proponentes
  // ==========================================

  listarProponentes(): Observable<PerfilProponente[]> {
    return this.http.get<PerfilProponente[]>(`${this.API_URL}/proponentes`);
  }

  obtenerProponente(id: number): Observable<PerfilProponente> {
    return this.http.get<PerfilProponente>(`${this.API_URL}/proponentes/${id}`);
  }

  crearProponente(perfil: PerfilProponente): Observable<PerfilProponente> {
    return this.http.post<PerfilProponente>(`${this.API_URL}/proponentes`, perfil);
  }

  actualizarProponente(id: number, perfil: PerfilProponente): Observable<PerfilProponente> {
    return this.http.put<PerfilProponente>(`${this.API_URL}/proponentes/${id}`, perfil);
  }

  eliminarProponente(id: number): Observable<any> {
    return this.http.delete(`${this.API_URL}/proponentes/${id}`);
  }

  // ==========================================
  // Fechas y checklist
  // ==========================================

  obtenerFechas(codigoProceso: string): Observable<FechasProceso> {
    return this.http.get<FechasProceso>(`${this.API_URL}/documentos/fechas/${codigoProceso}`);
  }

  obtenerChecklist(
    codigoProceso: string,
    proponenteId: number
  ): Observable<RespuestaChecklist> {
    return this.http.get<RespuestaChecklist>(`${this.API_URL}/documentos/checklist`, {
      params: {
        codigo_proceso: codigoProceso,
        proponente_id: proponenteId,
      },
    });
  }

  // ==========================================
  // Plantillas vacías
  // ==========================================

  contadorVacio(): Contador {
    return { nombre: '', cedula: '', mat_profe: '', rol: 'contador' };
  }

  empresaVacia(): Empresa {
    return {
      nom_o_raz_social: '',
      nit: '',
      es_persona_juridica: false,
      repre_nombre: '',
      repre_cedula: '',
      repre_mat_profe: '',
      contac_direccion: '',
      contac_ciudad: '',
      contac_email: '',
      contac_tele: '',
      contac_telefax: '',
      contador_id: null,
      accionistas: [],
    };
  }

  accionistaVacio(orden: number): Accionista {
    return { orden, nombre: '', cedula: '', porcentaje: '' };
  }

  integranteVacio(empresaId: number, orden: number, esLider: boolean): IntegranteProponente {
    return {
      empresa_id: empresaId,
      orden,
      compromiso: '',
      es_lider: esLider,
      pertenece_grupo: false,
      cotiza_bolsa: false,
      acredita_mujeres: false,
      acredita_discapacidad: false,
      acredita_mipyme: false,
    };
  }

  perfilVacio(): PerfilProponente {
    return {
      tipo: 'union_temporal',
      nombre: '',
      codigo_proceso: '',
      representante_empresa_id: null,
      entidad_telefono: '',
      entidad_pagina: '',
      entidad_horario: '',
      entidad_correo: '',
      entidad_politica: '',
      fecha_cierre: '',
      fecha_carta_gerencia: '',
      pers_clave_eval: '',
      integrantes: [],
    };
  }
}
