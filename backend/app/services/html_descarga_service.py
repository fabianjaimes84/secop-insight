import re

from bs4 import BeautifulSoup

from app.core.logger import logger
from app.models.html_descarga import (
    DocumentoHtmlDescarga,
    EventoCronogramaHtmlDescarga,
    InfoGeneralHtmlDescarga,
    ObservacionHtmlDescarga,
    ProcesoHtmlDescargaExtraido,
    ProponenteHtmlDescarga,
    RequisitoHtmlDescarga,
)


class HtmlDescargaServiceError(Exception):
    """Excepción para errores al procesar un HTML de SECOP I."""

    pass


class HtmlDescargaService:
    """
    Extrae información estructurada de un archivo HTML de detalle de proceso
    descargado manualmente desde SECOP I (community.secop.gov.co).
    """

    CAMPOS_INFO_GENERAL = {
        "lblBasePriceGen": "precio_estimado_total",
        "lblRequestReferenceGen": "numero_proceso",
        "lblRequestNameGen": "titulo",
        "lblPhaseGen": "fase",
        "lblStateGen": "estado",
        "lblPreviousPhaseGen": "fase_previa",
        "lblDescriptionGen": "descripcion",
        "lblProcedureTypeGen": "modalidad",
        "lblTypeOfContractGen": "tipo_contrato",
        "spnRelatedRequestGen": "proceso_relacionado",
        "lblDocumentsTypeClassLabel": "sector",
        "lblContractEndDateGen": "fecha_terminacion_contrato",
        "lbllblPlaceOfWorks": "direccion_ejecucion",
        "lblExpectedDurationOfContractGen": "duracion_contrato",
    }

    ID_ENTIDAD = "fdsRequestSummaryInfo_tblDetail_trRowBuyer_tdCell1_ctzBusinessCard"
    ID_GRUPO_MIPYME = "rdbgMipymeRadioButton"
    ID_GRUPO_LOTES = "rdbgHasLotsRadio"
    ID_DOCUMENTOS_TIPO_SI = "spnHasDocumentsTypeClassFieldTrue"
    ID_DOCUMENTOS_TIPO_DETALLE = "spnDocumentTypeClassHelpTextSpan"

    PATRON_PROPONENTE_CON_CIUDAD = re.compile(
        r"^(.*?)COLOMBIA,\s*(.*?)\s*\d+\s*Recomendaci", re.I
    )
    PATRON_PROPONENTE_SIN_CIUDAD = re.compile(r"^(.*?)\s*\d+\s*Recomendaci", re.I)

    def _texto_valor_de_fila(self, soup: BeautifulSoup, label_id: str) -> str:
        etiqueta = soup.find(id=label_id)
        if not etiqueta:
            return ""
        fila = etiqueta.find_parent("tr")
        if not fila:
            return ""
        celdas = fila.find_all("td", recursive=False)
        if len(celdas) >= 2:
            return celdas[1].get_text(" ", strip=True)
        return ""

    def _extraer_radio_booleano(self, soup: BeautifulSoup, id_grupo: str) -> bool:
        """El HTML marca la opción elegida (Sí/No) de un grupo de radio con 'checked'."""
        grupo = soup.find(id=id_grupo)
        if not grupo:
            return False
        opcion_marcada = grupo.find("input", checked=True)
        if not opcion_marcada:
            return False
        return opcion_marcada.get("value") == "true"

    def _extraer_documentos_tipo(self, soup: BeautifulSoup) -> tuple[bool, str]:
        """
        'Documentos Tipo' no usa radio buttons: hay dos <span>, uno para 'Sí' y
        otro para 'No', y el que no aplica queda oculto con style="display:none".
        """
        span_si = soup.find(id=self.ID_DOCUMENTOS_TIPO_SI)
        usa_documentos_tipo = bool(span_si) and "display:none" not in (
            span_si.get("style", "")
        )

        detalle_tag = soup.find(id=self.ID_DOCUMENTOS_TIPO_DETALLE)
        detalle = detalle_tag.get_text(strip=True) if detalle_tag else ""

        return usa_documentos_tipo, detalle

    def _extraer_info_general(self, soup: BeautifulSoup) -> InfoGeneralHtmlDescarga:
        datos = {}
        for id_html, campo in self.CAMPOS_INFO_GENERAL.items():
            datos[campo] = self._texto_valor_de_fila(soup, id_html)

        entidad_tag = soup.find(id=self.ID_ENTIDAD)
        datos["entidad"] = entidad_tag.get_text(" ", strip=True) if entidad_tag else ""
        datos["limitado_mipyme"] = self._extraer_radio_booleano(
            soup, self.ID_GRUPO_MIPYME
        )
        datos["tiene_lotes"] = self._extraer_radio_booleano(soup, self.ID_GRUPO_LOTES)
        datos["usa_documentos_tipo"], datos["documentos_tipo_detalle"] = (
            self._extraer_documentos_tipo(soup)
        )

        return InfoGeneralHtmlDescarga(**datos)

    def _extraer_cronograma(self, soup: BeautifulSoup) -> list[EventoCronogramaHtmlDescarga]:
        """
        Cada hito tiene un <label id="lblScheduleDateTimeLabel_N"> con el nombre
        del evento, y una fecha en <span id="dtmbScheduleDateTime_N_txt"> donde
        la zona horaria viene anidada dentro de un <font class="DateTimeDetail">.
        """
        eventos = []
        labels = soup.find_all(id=re.compile(r"^lblScheduleDateTimeLabel_(\d+)$"))

        for label in labels:
            numero = re.search(r"(\d+)$", label["id"]).group(1)
            nombre_evento = label.get_text(strip=True)

            contenedor_fecha = soup.find(id=f"dtmbScheduleDateTime_{numero}_txt")
            if not contenedor_fecha:
                continue

            zona = contenedor_fecha.find("font", class_="DateTimeDetail")
            zona_horaria = zona.get_text(strip=True) if zona else ""

            # El texto de la fecha es lo que queda del span quitando la zona horaria
            fecha_completa = contenedor_fecha.get_text(" ", strip=True)
            fecha = fecha_completa.replace(zona_horaria, "").strip()

            eventos.append(
                EventoCronogramaHtmlDescarga(
                    evento=nombre_evento,
                    fecha=fecha,
                    zona_horaria=zona_horaria,
                )
            )

        return eventos

    PATRON_ID_DOCUMENTO = re.compile(r"documentFileId=' \+ '(\d+)")

    def _extraer_documentos(self, soup: BeautifulSoup) -> list[DocumentoHtmlDescarga]:
        """
        Dos documentos pueden tener el mismo nombre visible pero ser archivos
        distintos (ej. la misma plantilla subida en la fase de proyecto de
        pliego y otra vez en la fase definitiva). Por eso NO deduplicamos por
        nombre, sino por el 'documentFileId' real que trae el enlace de
        descarga de cada fila.
        """
        nombres = soup.find_all(
            id=re.compile(r"^tdColumnDocumentNameP2Gen_spnDocumentName_\d+$")
        )
        vistos = set()
        documentos = []

        for n in nombres:
            nombre = n.get_text(strip=True)
            if not nombre:
                continue

            fila = n.find_parent("tr")
            enlace = ""
            if fila:
                link = fila.find("a")
                onclick = link.get("onclick", "") if link else ""
                coincidencia = self.PATRON_ID_DOCUMENTO.search(onclick)
                if coincidencia:
                    enlace = (
                        "/Public/Tendering/OpportunityDetail/DownloadFile"
                        f"?documentFileId={coincidencia.group(1)}"
                    )

            # Si no se pudo obtener el id del archivo, usamos el nombre como
            # respaldo para al menos evitar duplicados exactos.
            clave = enlace or nombre
            if clave not in vistos:
                vistos.add(clave)
                documentos.append(
                    DocumentoHtmlDescarga(nombre_documento=nombre, enlace=enlace)
                )

        return documentos

    def _extraer_proponentes(self, soup: BeautifulSoup) -> list[ProponenteHtmlDescarga]:
        tarjetas = soup.find_all(
            id=re.compile(r"^tdSupplierBusinessCardP2Gen_ctzSupplierBusinessCard_\d+$")
        )
        vistos = set()
        proponentes = []
        for t in tarjetas:
            texto = t.get_text(" ", strip=True)

            coincidencia = self.PATRON_PROPONENTE_CON_CIUDAD.match(texto)
            if coincidencia:
                nombre = coincidencia.group(1).strip(" ,")
                ciudad = coincidencia.group(2).strip(" ,")
            else:
                # Algunos proponentes no tienen ciudad registrada en el HTML
                coincidencia = self.PATRON_PROPONENTE_SIN_CIUDAD.match(texto)
                if not coincidencia:
                    continue
                nombre = coincidencia.group(1).strip(" ,")
                ciudad = ""

            clave = (nombre, ciudad)
            if nombre and clave not in vistos:
                vistos.add(clave)
                proponentes.append(ProponenteHtmlDescarga(nombre=nombre, ciudad=ciudad))
        return proponentes

    def _extraer_observaciones(self, soup: BeautifulSoup) -> list[ObservacionHtmlDescarga]:
        """
        Tabla de mensajes públicos del proceso (fieldset 'Observaciones y Mensajes'):
        cada fila trae tipo, referencia (código único), asunto y fecha.
        """
        filas = soup.find_all(
            id=re.compile(r"^grdPublicMessagesGridBeforeInterest_tr\d+$")
        )
        observaciones = []

        for fila in filas:
            tipo_td = fila.find(id=re.compile(r"td_thTypeColBeforeInterest$"))
            ref_td = fila.find(id=re.compile(r"td_thObjectReferenceColBeforeInterest$"))
            asunto_td = fila.find(id=re.compile(r"td_thSubjectColBeforeInterest$"))
            fecha_td = fila.find(id=re.compile(r"td_thMessageDateColBeforeInterest$"))

            observaciones.append(
                ObservacionHtmlDescarga(
                    tipo=tipo_td.get_text(strip=True) if tipo_td else "",
                    referencia=ref_td.get_text(strip=True) if ref_td else "",
                    asunto=asunto_td.get_text(strip=True) if asunto_td else "",
                    fecha=fecha_td.get_text(" ", strip=True) if fecha_td else "",
                )
            )

        return observaciones

    def _extraer_requisitos(self, soup: BeautifulSoup) -> list[RequisitoHtmlDescarga]:
        requisitos = []
        filas = soup.find_all("tr", class_=re.compile(r"QuestionnaireLine"))

        for fila in filas:
            numero = fila.find("span", class_="VortalSpan")
            descripcion_div = fila.find(
                "div", id=re.compile(r"questionDescriptionwrapper_")
            )
            requiere_evidencia = fila.find("span", id=re.compile(r"spnReqEvidenceMsg"))

            if descripcion_div:
                requisitos.append(
                    RequisitoHtmlDescarga(
                        item=numero.get_text(strip=True) if numero else "",
                        descripcion=descripcion_div.get_text(" ", strip=True),
                        requiere_documento_adjunto=requiere_evidencia is not None,
                    )
                )

        return requisitos

    def procesar_html(self, contenido_html: str) -> ProcesoHtmlDescargaExtraido:
        """Punto de entrada principal: recibe el HTML como texto y devuelve todo lo extraído."""
        try:
            soup = BeautifulSoup(contenido_html, "lxml")

            info_general = self._extraer_info_general(soup)
            cronograma = self._extraer_cronograma(soup)
            documentos = self._extraer_documentos(soup)
            proponentes = self._extraer_proponentes(soup)
            observaciones = self._extraer_observaciones(soup)
            requisitos = self._extraer_requisitos(soup)

            logger.info(
                f"HTML SECOP I procesado. Proceso: '{info_general.numero_proceso}', "
                f"{len(cronograma)} eventos, {len(documentos)} documentos, "
                f"{len(proponentes)} proponentes, {len(observaciones)} observaciones, "
                f"{len(requisitos)} requisitos."
            )

            return ProcesoHtmlDescargaExtraido(
                info_general=info_general,
                cronograma=cronograma,
                documentos=documentos,
                proponentes=proponentes,
                observaciones=observaciones,
                requisitos=requisitos,
            )

        except Exception as e:
            logger.error(f"Error procesando HTML de SECOP I: {e}")
            raise HtmlDescargaServiceError(f"No se pudo procesar el archivo HTML: {e}")
