/**
 * Captura automática de procesos SECOP.
 *
 * Se ejecuta dentro de la página del proceso. Espera a que el contenido
 * real esté cargado (es decir, después de que el usuario pasó el
 * reCAPTCHA) y envía el HTML al backend local. No descarga ningún archivo.
 */

const URL_BACKEND = 'http://localhost:8000/html-descarga/capturar';

// Elemento que solo existe cuando el detalle del proceso ya está visible.
// Si el reCAPTCHA sigue en pantalla, este elemento no aparece todavía.
const SELECTOR_PROCESO_CARGADO = '#lblRequestReferenceGen';

// Cuánto esperar entre intentos y cuántas veces reintentar antes de rendirse.
const INTERVALO_MS = 1000;
const MAX_INTENTOS = 60; // hasta 1 minuto esperando a que pase el captcha

let yaEnviado = false;

/** Muestra un aviso discreto en la esquina de la pantalla. */
function mostrarAviso(mensaje, esError = false) {
  const aviso = document.createElement('div');
  aviso.textContent = mensaje;
  aviso.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 999999;
    padding: 12px 18px;
    border-radius: 8px;
    font-family: system-ui, sans-serif;
    font-size: 13px;
    color: #fff;
    box-shadow: 0 4px 12px rgba(0,0,0,.2);
    background: ${esError ? '#dc2626' : '#16a34a'};
  `;
  document.body.appendChild(aviso);

  setTimeout(() => aviso.remove(), 5000);
}

/** Envía el HTML completo de la página al backend. */
async function enviarAlBackend() {
  if (yaEnviado) {
    return;
  }
  yaEnviado = true;

  try {
    const respuesta = await fetch(URL_BACKEND, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        html: document.documentElement.outerHTML,
        url: window.location.href,
      }),
    });

    if (!respuesta.ok) {
      const error = await respuesta.json().catch(() => ({}));
      mostrarAviso(
        `No se pudo guardar: ${error.detail || respuesta.status}`,
        true
      );
      return;
    }

    const datos = await respuesta.json();
    mostrarAviso(
      `Guardado: ${datos.numero_proceso} ` +
      `(${datos.total_documentos} documentos, ${datos.total_observaciones} observaciones). ` +
      `Cerrando pestaña...`
    );

    // El script de la página no puede cerrarse a sí mismo: se le pide al
    // script de fondo que cierre esta pestaña.
    chrome.runtime.sendMessage({ accion: 'cerrarPestana' });

  } catch (error) {
    mostrarAviso(
      'No se pudo conectar con SECOP Insight. ¿Está corriendo el servidor?',
      true
    );
  }
}

/**
 * Revisa periódicamente si el proceso ya está visible en pantalla.
 * En cuanto lo detecta, espera a que terminen de cargar las tablas que
 * SECOP llena por JavaScript (documentos, proponentes, mensajes) y
 * entonces envía el HTML.
 */
function esperarProcesoCargado() {
  let intentos = 0;

  const revisar = setInterval(() => {
    intentos++;

    const procesoVisible = document.querySelector(SELECTOR_PROCESO_CARGADO);

    if (procesoVisible) {
      clearInterval(revisar);
      esperarTablasCompletas();
      return;
    }

    if (intentos >= MAX_INTENTOS) {
      clearInterval(revisar);
    }
  }, INTERVALO_MS);
}

/**
 * Las tablas de documentos y proponentes se llenan después de que la
 * página principal carga. Se espera a que la cantidad de filas deje de
 * crecer, para no capturar una lista incompleta.
 */
function esperarTablasCompletas() {
  let conteoAnterior = -1;
  let vecesEstable = 0;
  let intentos = 0;

  const contarFilas = () =>
    document.querySelectorAll(
      '[id^="tdColumnDocumentNameP2Gen_spnDocumentName_"],' +
      '[id^="tdSupplierBusinessCardP2Gen_ctzSupplierBusinessCard_"],' +
      '[id^="grdPublicMessagesGridBeforeInterest_tr"]'
    ).length;

  const revisar = setInterval(() => {
    intentos++;
    const actual = contarFilas();

    if (actual === conteoAnterior) {
      vecesEstable++;
      // Tres lecturas seguidas sin cambios: ya terminó de cargar.
      if (vecesEstable >= 3) {
        clearInterval(revisar);
        enviarAlBackend();
      }
    } else {
      vecesEstable = 0;
      conteoAnterior = actual;
    }

    // Tope de seguridad: se envía igual pasados ~15 segundos.
    if (intentos >= 15) {
      clearInterval(revisar);
      enviarAlBackend();
    }
  }, 1000);
}

esperarProcesoCargado();
