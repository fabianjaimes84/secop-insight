/**
 * Endpoints del backend.
 *
 * Todas las rutas deben definirse aquí para evitar
 * cadenas de texto repetidas en los servicios.
 */
export const ENDPOINTS = {

  // ==========================================
  // Procesos
  // ==========================================

  procesos: '/procesos',

  busqueda: '/procesos/busqueda',

  catalogos: '/procesos/catalogos',

  // ==========================================
  // Dashboard (Sprint futuro)
  // ==========================================

  dashboard: '/dashboard',

  // ==========================================
  // Seguimiento (Sprint futuro)
  // ==========================================

  favoritos: '/tracking/favoritos',

  alertas: '/tracking/alertas',

  // ==========================================
  // Reportes (Sprint futuro)
  // ==========================================

  exportarExcel: '/reportes/excel',

  exportarPdf: '/reportes/pdf',

  // ==========================================
  // Inteligencia Artificial (Sprint futuro)
  // ==========================================

  chat: '/ai/chat',

} as const;