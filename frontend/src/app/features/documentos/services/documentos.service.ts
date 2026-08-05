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
  nombre: string;
  cedula: string;

  // Participación
  orden: number;
  porcentaje: string;
  es_representante_legal: boolean;
}

export interface Empresa {
  id?: number;
  nom_o_raz_social: string;
  nit: string;
  es_persona_juridica: boolean;

  // Datos corporativos de la empresa
  direccion: string;
  ciudad: string;
  correo: string;
  telefono_fijo: string;
  telefono_celular: string;

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

  pertenece_grupo: boolean | null;
  tipo_grupo_empresarial: string;
  cotiza_bolsa: boolean | null;
  acredita_mujeres: boolean | null;
  acredita_discapacidad: boolean | null;
  acredita_mipyme: boolean;

  empresa?: Empresa;
}

export interface PerfilProponente {
  id?: number;
  tipo: 'natural' | 'juridica' | 'consorcio' | 'union_temporal';
  nombre: string;
  codigo_proceso: string;
  representante_empresa_id: number | null;

  // Representantes que firman (accionistas)
  repre_principal_accionista_id: number | null;
  repre_suplente_accionista_id: number | null;

  // Información especial de la oferta
  pers_clave_eval: string;
  experiencia_requerida: string;

  // Póliza
  poliza_numero: string;
  poliza_vigencia: string;
  poliza_valor: number | null;

  // Datos de la entidad contratante
  entidad_telefono: string;
  entidad_correo: string;
  entidad_horario: string;
  entidad_url_web: string;
  entidad_url_politica_datos: string;

  fecha_cierre: string;
  fecha_carta_gerencia: string;

  integrantes: IntegranteProponente[];
  representante_empresa?: Empresa | null;
  repre_principal?: Accionista | null;
  repre_suplente?: Accionista | null;
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
      direccion: '',
      ciudad: '',
      correo: '',
      telefono_fijo: '',
      telefono_celular: '',
      contador_id: null,
      accionistas: [],
    };
  }

  accionistaVacio(orden: number): Accionista {
    return {
      nombre: '',
      cedula: '',
      orden,
      porcentaje: '',
      es_representante_legal: false,
    };
  }

  integranteVacio(empresaId: number, orden: number, esLider: boolean): IntegranteProponente {
    return {
      empresa_id: empresaId,
      orden,
      compromiso: '',
      es_lider: esLider,
      pertenece_grupo: null,
      tipo_grupo_empresarial: '',
      cotiza_bolsa: null,
      acredita_mujeres: null,
      acredita_discapacidad: null,
      acredita_mipyme: false,
    };
  }

  perfilVacio(): PerfilProponente {
    return {
      tipo: 'union_temporal',
      nombre: '',
      codigo_proceso: '',
      representante_empresa_id: null,
      repre_principal_accionista_id: null,
      repre_suplente_accionista_id: null,
      pers_clave_eval: '',
      experiencia_requerida: '',
      poliza_numero: '',
      poliza_vigencia: '',
      poliza_valor: null,
      entidad_telefono: '',
      entidad_correo: '',
      entidad_horario: '',
      entidad_url_web: '',
      entidad_url_politica_datos: '',
      fecha_cierre: '',
      fecha_carta_gerencia: '',
      integrantes: [],
    };
  }
}
