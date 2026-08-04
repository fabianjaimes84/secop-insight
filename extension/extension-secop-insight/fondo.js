/**
 * Script de fondo de la extensión.
 *
 * El script que corre dentro de la página no puede cerrarse a sí mismo,
 * así que envía un mensaje aquí y desde acá se cierra la pestaña.
 */

chrome.runtime.onMessage.addListener((mensaje, remitente) => {
  if (mensaje?.accion === 'cerrarPestana' && remitente.tab?.id) {
    // Pequeña espera para que el usuario alcance a ver el aviso de
    // confirmación antes de que la pestaña desaparezca.
    setTimeout(() => {
      chrome.tabs.remove(remitente.tab.id);
    }, 2500);
  }
});
