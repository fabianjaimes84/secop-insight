import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import {
  Accionista,
  Contador,
  DocumentosService,
  Empresa,
  ItemChecklist,
  PerfilProponente,
  RespuestaChecklist,
} from '../services/documentos.service';
import { HtmlDescargaService } from '../../search/services/html-descarga.service';
import { FavoritosService } from '../../../core/services/favoritos.service';

@Component({
  selector: 'app-documentos-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './documentos-page.html',
})
export class DocumentosPage implements OnInit {

  seccion: 'empresas' | 'proponentes' = 'empresas';

  empresas: Empresa[] = [];
  contadores: Contador[] = [];
  proponentes: PerfilProponente[] = [];
  procesos: any[] = [];

  // Checklist
  proponenteSeleccionado: PerfilProponente | null = null;
  checklist: RespuestaChecklist | null = null;
  seleccionados = new Set<string>();

  // Formulario de empresa
  empresaEnEdicion: Empresa | null = null;
  mostrarNuevoContador = false;
  nuevoContador: Contador | null = null;

  // Asistente de proponente
  asistenteAbierto = false;
  paso = 1;
  borrador: PerfilProponente | null = null;
  cargandoFechas = false;

  cargando = false;
  error: string | null = null;

  favoritos: any[] = [];

  constructor(
    private documentosService: DocumentosService,
    private htmlDescargaService: HtmlDescargaService,
    private favoritosService: FavoritosService
  ) {}

  ngOnInit(): void {
    this.cargarEmpresas();
    this.cargarContadores();
    this.cargarProponentes();
    this.cargarProcesos();

    this.favoritosService.favoritos$.subscribe((fav) => {
      this.favoritos = fav;
    });
  }

  // ==========================================
  // Carga de datos
  // ==========================================

  cargarEmpresas(): void {
    this.documentosService.listarEmpresas().subscribe({
      next: (lista) => (this.empresas = lista),
      error: () => (this.error = 'No se pudieron cargar las empresas.'),
    });
  }

  cargarContadores(): void {
    this.documentosService.listarContadores().subscribe({
      next: (lista) => (this.contadores = lista),
      error: () => (this.error = 'No se pudieron cargar los contadores.'),
    });
  }

  cargarProponentes(): void {
    this.documentosService.listarProponentes().subscribe({
      next: (lista) => (this.proponentes = lista),
      error: () => (this.error = 'No se pudieron cargar los proponentes.'),
    });
  }

  cargarProcesos(): void {
    this.htmlDescargaService.listarProcesos().subscribe({
      next: (lista: any) => (this.procesos = lista),
      error: () => (this.error = 'No se pudieron cargar los procesos.'),
    });
  }

  codigoBase(numeroProceso: string): string {
    return (numeroProceso || '').trim().split(' ')[0];
  }

  etiquetaRol(rol: string): string {
    return rol === 'revisor_fiscal' ? 'Revisor fiscal' : 'Contador';
  }

  // ==========================================
  // Contador (inline en formulario de empresa)
  // ==========================================

  abrirNuevoContador(): void {
    this.nuevoContador = this.documentosService.contadorVacio();
    this.mostrarNuevoContador = true;
  }

  guardarNuevoContador(): void {
    if (!this.nuevoContador?.nombre.trim()) {
      this.error = 'El nombre del contador es obligatorio.';
      return;
    }

    this.cargando = true;
    this.documentosService.crearContador(this.nuevoContador).subscribe({
      next: (creado) => {
        this.contadores.push(creado);
        if (this.empresaEnEdicion) {
          this.empresaEnEdicion.contador_id = creado.id!;
        }
        this.mostrarNuevoContador = false;
        this.nuevoContador = null;
        this.error = null;
        this.cargando = false;
      },
      error: (err) => {
        this.error = err?.error?.detail || 'No se pudo guardar el contador.';
        this.cargando = false;
      },
    });
  }

  // ==========================================
  // Empresas
  // ==========================================

  nuevaEmpresa(): void {
    this.empresaEnEdicion = this.documentosService.empresaVacia();
  }

  editarEmpresa(empresa: Empresa): void {
    this.empresaEnEdicion = {
      ...empresa,
      accionistas: (empresa.accionistas ?? []).map((a) => ({ ...a })),
    };
  }

  cambiarTipoEmpresa(): void {
    // Solo actualizar el tipo, los accionistas se agregan manualmente
  }

  agregarAccionista(): void {
    if (!this.empresaEnEdicion) return;
    const orden = this.empresaEnEdicion.accionistas.length + 1;
    const nuevoAccionista = this.documentosService.accionistaVacio(orden);

    // Calcular automáticamente el porcentaje restante para personas jurídicas
    if (this.empresaEnEdicion.es_persona_juridica && this.empresaEnEdicion.accionistas.length > 0) {
      const sumaExistente = this.sumaAccionistas;
      const restante = 100 - sumaExistente;
      if (restante > 0) {
        nuevoAccionista.porcentaje = this.normalizarPorcentaje(`${restante}`);
      }
    }

    this.empresaEnEdicion.accionistas.push(nuevoAccionista);
  }

  quitarAccionista(indice: number): void {
    this.empresaEnEdicion?.accionistas.splice(indice, 1);
  }

  get sumaAccionistas(): number {
    return (this.empresaEnEdicion?.accionistas ?? []).reduce((total, a) => {
      const numero = parseFloat((a.porcentaje || '').replace('%', '').trim());
      return total + (isNaN(numero) ? 0 : numero);
    }, 0);
  }

  guardarEmpresa(): void {
    if (!this.empresaEnEdicion) return;

    if (!this.empresaEnEdicion.nom_o_raz_social.trim()) {
      this.error = 'El nombre o razón social es obligatorio.';
      return;
    }

    // Si es persona natural, asignar 100% automáticamente
    if (!this.empresaEnEdicion.es_persona_juridica) {
      this.empresaEnEdicion.accionistas.forEach((a) => {
        a.porcentaje = '100%';
      });
    } else {
      // Para personas jurídicas, normalizar porcentajes
      this.empresaEnEdicion.accionistas.forEach((a) => {
        a.porcentaje = this.normalizarPorcentaje(a.porcentaje);
      });
    }

    const peticion = this.empresaEnEdicion.id
      ? this.documentosService.actualizarEmpresa(
          this.empresaEnEdicion.id,
          this.empresaEnEdicion
        )
      : this.documentosService.crearEmpresa(this.empresaEnEdicion);

    peticion.subscribe({
      next: () => {
        this.empresaEnEdicion = null;
        this.error = null;
        this.cargarEmpresas();
      },
      error: (err) =>
        (this.error = err?.error?.detail || 'No se pudo guardar la empresa.'),
    });
  }

  eliminarEmpresa(id: number): void {
    this.documentosService.eliminarEmpresa(id).subscribe({
      next: () => this.cargarEmpresas(),
      error: (err) =>
        (this.error = err?.error?.detail || 'No se pudo eliminar la empresa.'),
    });
  }

  // ==========================================
  // Asistente de proponente
  // ==========================================

  abrirAsistente(): void {
    this.borrador = this.documentosService.perfilVacio();
    this.paso = 1;
    this.asistenteAbierto = true;
    this.error = null;
    this.cargandoFechas = false;
  }

  editarProponente(id: number): void {
    this.documentosService.obtenerProponente(id).subscribe({
      next: (perfil) => {
        this.borrador = perfil;
        this.paso = 1;
        this.asistenteAbierto = true;
      },
      error: () => (this.error = 'No se pudo cargar el proponente.'),
    });
  }

  cerrarAsistente(): void {
    this.asistenteAbierto = false;
    this.borrador = null;
    this.paso = 1;
    this.error = null;
  }

  get esPlural(): boolean {
    return this.borrador?.tipo === 'consorcio' || this.borrador?.tipo === 'union_temporal';
  }

  get requiereRepresentanteSuplente(): boolean {
    return this.esPlural;
  }

  siguientePaso(): void {
    if (!this.borrador) return;

    // Paso 1: Validar tipo y que haya procesos disponibles
    if (this.paso === 1) {
      if (!this.borrador.tipo) {
        this.error = 'Selecciona un tipo de proponente.';
        return;
      }
      if (!this.procesosPendientes().length) {
        this.error = 'No hay procesos disponibles. Por favor, ve a Seguimiento y actualiza el estado del proceso a "Presentar oferta".';
        return;
      }
    }

    // Paso 2: Validar integrantes según el tipo
    if (this.paso === 2) {
      if (!this.borrador.integrantes.length) {
        this.error = 'Agrega al menos una empresa.';
        return;
      }
      if (this.esPlural && this.borrador.integrantes.length < 2) {
        this.error = 'Un consorcio/unión temporal debe tener al menos 2 empresas.';
        return;
      }
    }

    // Paso 3: Validar representante principal y suplente
    if (this.paso === 3) {
      if (!this.borrador.repre_principal_accionista_id) {
        this.error = 'Elige un representante principal.';
        return;
      }
      if (this.requiereRepresentanteSuplente && !this.borrador.repre_suplente_accionista_id) {
        this.error = 'Elige un representante suplente.';
        return;
      }
      if (this.borrador.repre_principal_accionista_id === this.borrador.repre_suplente_accionista_id) {
        this.error = 'El representante principal y suplente deben ser personas diferentes.';
        return;
      }
    }

    this.error = null;
    this.paso = Math.min(5, this.paso + 1);

    // Al entrar al paso 5, si ya hay proceso elegido, trae las fechas.
    if (this.paso === 5 && this.borrador.codigo_proceso) {
      this.cargarFechas();
    }
  }

  pasoAnterior(): void {
    this.error = null;
    this.paso = Math.max(1, this.paso - 1);
  }

  elegirTipo(tipo: 'natural' | 'juridica' | 'consorcio' | 'union_temporal'): void {
    if (!this.borrador) return;
    this.borrador.tipo = tipo;
    this.borrador.integrantes = [];
    this.borrador.representante_empresa_id = null;
    this.borrador.repre_principal_accionista_id = null;
    this.borrador.repre_suplente_accionista_id = null;
  }

  agregarIntegrante(): void {
    if (!this.borrador) return;

    const disponibles = this.empresasDisponibles();
    if (!disponibles.length) {
      this.error = 'No hay más empresas disponibles.';
      return;
    }

    const nuevoIntegrante = this.documentosService.integranteVacio(
      disponibles[0].id!,
      this.borrador.integrantes.length + 1,
      this.borrador.integrantes.length === 0
    );

    // Calcular automáticamente el porcentaje restante para plurales
    if (this.esPlural && this.borrador.integrantes.length > 0) {
      const sumaExistente = this.sumaCompromisos;
      const restante = 100 - sumaExistente;
      if (restante > 0) {
        nuevoIntegrante.compromiso = this.normalizarPorcentaje(`${restante}`);
      }
    }

    this.borrador.integrantes.push(nuevoIntegrante);
  }

  empresasDisponibles(): Empresa[] {
    const usadas = new Set(
      this.borrador?.integrantes.map((i) => Number(i.empresa_id)) ?? []
    );
    return this.empresas.filter((e) => !usadas.has(e.id!));
  }

  opcionesParaIntegrante(indice: number): Empresa[] {
    const actual = Number(this.borrador?.integrantes[indice]?.empresa_id);
    const propia = this.empresas.filter((e) => e.id === actual);
    return [...propia, ...this.empresasDisponibles()];
  }

  quitarIntegrante(indice: number): void {
    if (!this.borrador) return;
    const quitada = this.borrador.integrantes[indice];
    this.borrador.integrantes.splice(indice, 1);

    if (Number(quitada?.empresa_id) === this.borrador.representante_empresa_id) {
      this.borrador.representante_empresa_id = null;
    }
  }

  marcarLider(indice: number): void {
    if (!this.borrador) return;
    this.borrador.integrantes.forEach((integrante, i) => {
      integrante.es_lider = i === indice;
    });
  }

  get sumaCompromisos(): number {
    return (this.borrador?.integrantes ?? []).reduce((total, i) => {
      const numero = parseFloat((i.compromiso || '').replace('%', '').trim());
      return total + (isNaN(numero) ? 0 : numero);
    }, 0);
  }

  normalizarPorcentaje(valor: string): string {
    if (!valor) return '';
    const numero = valor.replace('%', '').trim();
    if (!numero) return '';
    return `${numero}%`;
  }

  alTerminarDeIngresarPorcentaje(objeto: any, campo: string): void {
    if (objeto && campo) {
      objeto[campo] = this.normalizarPorcentaje(objeto[campo]);
    }
  }

  empresasElegidas(): Empresa[] {
    const ids = (this.borrador?.integrantes ?? []).map((i) => Number(i.empresa_id));
    return this.empresas.filter((e) => ids.includes(e.id!));
  }

  empresaPorId(id: number | null): Empresa | undefined {
    return this.empresas.find((e) => e.id === Number(id));
  }

  nombreEmpresa(id: number | null): string {
    return this.empresaPorId(id)?.nom_o_raz_social ?? '';
  }

  // ==========================================
  // Accionistas (representantes)
  // ==========================================

  accionistasDisponibles(): Accionista[] {
    if (!this.borrador) return [];
    const empresasIntegrantes = this.empresasElegidas();
    return empresasIntegrantes.flatMap((e) => e.accionistas || []);
  }

  accionistasParaPrincipal(): Accionista[] {
    return this.accionistasDisponibles();
  }

  accionistasParaSuplente(): Accionista[] {
    // Suplente debe ser diferente al principal
    const principal = this.borrador?.repre_principal_accionista_id;
    return this.accionistasDisponibles().filter((a) => a.id !== principal);
  }

  nombreAccionista(accionistaId: number | null): string {
    if (!accionistaId) return '';
    const todos = this.accionistasDisponibles();
    return todos.find((a) => a.id === accionistaId)?.nombre || '';
  }

  cedulaAccionista(accionistaId: number | null): string {
    if (!accionistaId) return '';
    const todos = this.accionistasDisponibles();
    return todos.find((a) => a.id === accionistaId)?.cedula || '';
  }

  procesosDisponibles(): any[] {
    const procesosUsados = new Set(
      this.proponentes
        .filter(p => p.codigo_proceso)
        .map(p => p.codigo_proceso)
    );
    return this.procesos.filter(p => !procesosUsados.has(this.codigoBase(p.numero_proceso)));
  }

  procesoPorCodigo(codigo: string): any {
    return this.procesos.find(p => this.codigoBase(p.numero_proceso) === codigo);
  }

  procesosPendientes(): any[] {
    const procesosUsados = new Set(
      this.proponentes
        .filter(p => p.codigo_proceso)
        .map(p => p.codigo_proceso)
    );

    // Solo mostrar procesos que están en seguimiento (favoritos) y sin oferta enviada
    const favoritosEnSeguimiento = this.favoritos
      .filter(f => !f.ofertaEnviada)
      .map(f => this.codigoBase(f.proceso.referencia_del_proceso));

    return this.procesos.filter(p => {
      const codigo = this.codigoBase(p.numero_proceso);
      return favoritosEnSeguimiento.includes(codigo) && !procesosUsados.has(codigo);
    });
  }

  /** Trae la fecha de cierre real del cronograma y calcula la carta de gerencia. */
  cargarFechas(): void {
    if (!this.borrador?.codigo_proceso) return;

    this.cargandoFechas = true;
    this.documentosService.obtenerFechas(this.borrador.codigo_proceso).subscribe({
      next: (fechas) => {
        if (this.borrador) {
          this.borrador.fecha_cierre = fechas.fecha_cierre;
          this.borrador.fecha_carta_gerencia = fechas.fecha_carta_gerencia;
        }
        this.cargandoFechas = false;
      },
      error: () => (this.cargandoFechas = false),
    });
  }

  proponenteNombreDuplicado(): boolean {
    if (!this.borrador?.nombre.trim()) return false;
    return this.proponentes.some(
      (p) => p.nombre.toLowerCase() === this.borrador?.nombre.toLowerCase() && p.id !== this.borrador?.id
    );
  }

  formatearFechaCierre(): string {
    if (!this.borrador?.fecha_cierre) return '—';

    // Patrón para detectar fecha real (DD/MM/YYYY HH:MM)
    const patronFecha = /(\d{1,2})\/(\d{1,2})\/(\d{4})/;
    const match = this.borrador.fecha_cierre.match(patronFecha);

    // Si contiene una fecha real, formatearla como DD/MM/YYYY
    if (match) {
      const [fechaCompleta, dia, mes, año] = match;
      // Retornar en formato DD/MM/YYYY con ceros a la izquierda
      return `${String(dia).padStart(2, '0')}/${String(mes).padStart(2, '0')}/${año}`;
    }

    // Si no es una fecha real (ej: "5 días para terminar"), retornar como está
    return this.borrador.fecha_cierre;
  }

  guardarProponente(): void {
    if (!this.borrador) return;

    if (!this.borrador.nombre.trim()) {
      this.error = 'Ponle un nombre al proponente.';
      return;
    }

    if (this.proponenteNombreDuplicado()) {
      this.error = 'Ese proponente ya ha sido utilizado. Elige otro nombre.';
      return;
    }

    // Normalizar porcentajes de integrantes antes de guardar
    this.borrador.integrantes.forEach((integrante) => {
      integrante.compromiso = this.normalizarPorcentaje(integrante.compromiso);
    });

    const peticion = this.borrador.id
      ? this.documentosService.actualizarProponente(this.borrador.id, this.borrador)
      : this.documentosService.crearProponente(this.borrador);

    peticion.subscribe({
      next: () => {
        this.cerrarAsistente();
        this.cargarProponentes();
      },
      error: (err) =>
        (this.error = err?.error?.detail || 'No se pudo guardar el proponente.'),
    });
  }

  eliminarProponente(id: number, evento: Event): void {
    evento.stopPropagation();
    this.documentosService.eliminarProponente(id).subscribe({
      next: () => {
        this.cargarProponentes();
        if (this.proponenteSeleccionado?.id === id) {
          this.proponenteSeleccionado = null;
          this.checklist = null;
        }
      },
      error: () => (this.error = 'No se pudo eliminar el proponente.'),
    });
  }

  // ==========================================
  // Checklist
  // ==========================================

  verChecklist(proponente: PerfilProponente): void {
    if (!proponente.codigo_proceso) {
      this.error = 'Este proponente no tiene un proceso asociado.';
      return;
    }

    this.proponenteSeleccionado = proponente;
    this.cargando = true;
    this.error = null;
    this.checklist = null;

    this.documentosService
      .obtenerChecklist(proponente.codigo_proceso, proponente.id!)
      .subscribe({
        next: (respuesta) => {
          this.checklist = respuesta;
          this.seleccionados = new Set(
            respuesta.items.map((i) => i.nombre_archivo)
          );
          this.cargando = false;
        },
        error: (err) => {
          this.error = err?.error?.detail || 'No se pudo generar el checklist.';
          this.cargando = false;
        },
      });
  }

  cerrarChecklist(): void {
    this.checklist = null;
    this.proponenteSeleccionado = null;
  }

  alternarSeleccion(item: ItemChecklist): void {
    if (this.seleccionados.has(item.nombre_archivo)) {
      this.seleccionados.delete(item.nombre_archivo);
    } else {
      this.seleccionados.add(item.nombre_archivo);
    }
  }

  estaSeleccionado(item: ItemChecklist): boolean {
    return this.seleccionados.has(item.nombre_archivo);
  }

  marcarTodos(marcar: boolean): void {
    this.seleccionados = marcar
      ? new Set(this.checklist?.items.map((i) => i.nombre_archivo) ?? [])
      : new Set();
  }

  get itemsGenerales(): ItemChecklist[] {
    return this.checklist?.items.filter((i) => !i.integrante) ?? [];
  }

  get integrantesConDocumentos(): string[] {
    const nombres = (this.checklist?.items ?? [])
      .filter((i) => i.integrante)
      .map((i) => i.integrante);
    return [...new Set(nombres)];
  }

  itemsDeIntegrante(nombre: string): ItemChecklist[] {
    return this.checklist?.items.filter((i) => i.integrante === nombre) ?? [];
  }

  etiquetaTipo(tipo: string): string {
    const etiquetas: Record<string, string> = {
      natural: 'Persona natural',
      juridica: 'Persona jurídica',
      consorcio: 'Consorcio',
      union_temporal: 'Unión temporal',
    };
    return etiquetas[tipo] ?? tipo;
  }
}
