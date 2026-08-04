/**
 * Puente entre la aplicación y la extensión.
 *
 * La página web no puede hablarle directamente al script de fondo, así
 * que este script hace de intermediario: escucha mensajes de la app
 * (window.postMessage) y los reenvía a la extensión, y viceversa.
 */

const ORIGEN = 'secop-insight';

/** Avisa a la app que la extensión está instalada y activa. */
window.postMessage({ origen: ORIGEN, accion: 'extensionLista' }, '*');

window.addEventListener('message', (evento) => {
  if (evento.source !== window) {
    return;
  }

  const datos = evento.data;
  if (!datos || datos.origen !== ORIGEN || datos.haciaExtension !== true) {
    return;
  }

  // Reenviar a la extensión y devolver la respuesta a la app
  chrome.runtime.sendMessage(
    { accion: datos.accion, urls: datos.urls },
    (respuesta) => {
      window.postMessage(
        {
          origen: ORIGEN,
          accion: `${datos.accion}Respuesta`,
          respuesta: respuesta ?? null,
        },
        '*'
      );
    }
  );
});

/** Reenvía a la app el progreso que informa el script de fondo. */
chrome.runtime.onMessage.addListener((mensaje) => {
  if (mensaje?.accion === 'progresoCola') {
    window.postMessage(
      {
        origen: ORIGEN,
        accion: 'progresoCola',
        restantes: mensaje.restantes,
        total: mensaje.total,
      },
      '*'
    );
  }
});
