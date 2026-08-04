/**
 * Script de fondo de la extensión.
 *
 * Se encarga de dos cosas:
 *  1. Cerrar la pestaña de un proceso cuando ya fue capturado.
 *  2. Gestionar la cola de actualización: abre los procesos uno por uno,
 *     esperando a que cada uno se capture antes de abrir el siguiente.
 */

/** URLs pendientes por abrir en la actualización en lote. */
let cola = [];
let pestanaActual = null;
let totalCola = 0;

/** Avisa a la app cuántos procesos quedan por actualizar. */
function notificarProgreso() {
  const restantes = cola.length + (pestanaActual ? 1 : 0);

  chrome.runtime.sendMessage({
    accion: 'progresoCola',
    restantes,
    total: totalCola,
  }).catch(() => {
    // La app puede no estar escuchando; no es un problema.
  });
}

/** Abre el siguiente proceso de la cola, si queda alguno. */
function abrirSiguiente() {
  if (cola.length === 0) {
    pestanaActual = null;
    totalCola = 0;
    notificarProgreso();
    return;
  }

  const url = cola.shift();

  chrome.tabs.create({ url, active: true }, (pestana) => {
    pestanaActual = pestana.id;
    notificarProgreso();
  });
}

/** Cierra una pestaña y continúa con la cola si venía de ahí. */
function cerrarPestana(idPestana) {
  const eraDeLaCola = idPestana === pestanaActual;

  chrome.tabs.remove(idPestana).catch(() => {});

  if (eraDeLaCola) {
    pestanaActual = null;
    // Pequeña pausa entre procesos, para no atropellar al servidor.
    setTimeout(abrirSiguiente, 800);
  }
}

chrome.runtime.onMessage.addListener((mensaje, remitente, responder) => {

  // Mensaje del script que corre dentro de la página del proceso
  if (mensaje?.accion === 'cerrarPestana' && remitente.tab?.id) {
    const idPestana = remitente.tab.id;
    // Espera breve para que el usuario alcance a ver el aviso verde.
    setTimeout(() => cerrarPestana(idPestana), 2500);
    return;
  }

  // Mensaje de la app: arrancar la actualización en lote
  if (mensaje?.accion === 'actualizarEnLote' && Array.isArray(mensaje.urls)) {
    cola = mensaje.urls.filter(Boolean);
    totalCola = cola.length;

    responder({ recibido: true, total: totalCola });

    if (!pestanaActual) {
      abrirSiguiente();
    }
    return true;
  }

  // La app pregunta si hay una cola en curso
  if (mensaje?.accion === 'estadoCola') {
    responder({
      restantes: cola.length + (pestanaActual ? 1 : 0),
      total: totalCola,
    });
    return true;
  }

  // Cancelar la cola
  if (mensaje?.accion === 'cancelarCola') {
    cola = [];
    totalCola = 0;
    responder({ cancelado: true });
    return true;
  }
});

/**
 * Si el usuario cierra manualmente la pestaña en curso, la cola debe
 * continuar igualmente en vez de quedarse trabada.
 */
chrome.tabs.onRemoved.addListener((idPestana) => {
  if (idPestana === pestanaActual) {
    pestanaActual = null;
    setTimeout(abrirSiguiente, 800);
  }
});
