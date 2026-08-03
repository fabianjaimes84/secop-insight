import re
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import (
    CronogramaHistorialHtmlDescarga,
    CronogramaHtmlDescarga,
    DocumentoHtmlDescarga,
    ObservacionHtmlDescarga,
    ProcesoHtmlDescarga,
    ProponenteHtmlDescarga,
    RequisitoHtmlDescarga,
)
from app.models.html_descarga import InfoGeneralHtmlDescarga, ProcesoHtmlDescargaExtraido


def _parsear_precio(texto: str) -> float | None:
    """Convierte '1.605.417.705 COP' -> 1605417705.0. Devuelve None si no hay número."""
    if not texto:
        return None
    solo_digitos = re.sub(r"[^\d]", "", texto)
    return float(solo_digitos) if solo_digitos else None


class HtmlDescargaRepository:
    """
    Guarda en la base de datos lo extraído de un HTML de SECOP I, aplicando
    las reglas de negocio confirmadas:
        - Información y cronograma: se ACTUALIZAN.
        - Cambios de fecha en el cronograma: quedan en el historial.
        - Documentos, proponentes: se ACUMULAN (solo se agregan los nuevos).
        - Requisitos: se REEMPLAZAN por la lista más reciente.
    """

    def __init__(self, db: Session):
        self.db = db

    def guardar_proceso(self, datos: ProcesoHtmlDescargaExtraido) -> ProcesoHtmlDescarga:
        proceso = self._guardar_info_general(datos.info_general)
        self._guardar_cronograma(proceso, datos.cronograma)
        self._guardar_documentos(proceso, datos.documentos)
        self._guardar_proponentes(proceso, datos.proponentes)
        self._guardar_observaciones(proceso, datos.observaciones)
        self._guardar_requisitos(proceso, datos.requisitos)

        self.db.commit()
        self.db.refresh(proceso)
        return proceso

    def _guardar_info_general(self, info: InfoGeneralHtmlDescarga) -> ProcesoHtmlDescarga:
        proceso = (
            self.db.query(ProcesoHtmlDescarga)
            .filter_by(numero_proceso=info.numero_proceso)
            .first()
        )

        if proceso is None:
            proceso = ProcesoHtmlDescarga(numero_proceso=info.numero_proceso)
            self.db.add(proceso)

        proceso.titulo = info.titulo
        proceso.descripcion = info.descripcion
        proceso.entidad = info.entidad
        proceso.nit_entidad = info.nit_entidad
        proceso.modalidad = info.modalidad
        proceso.tipo_contrato = info.tipo_contrato
        proceso.limitado_mipyme = info.limitado_mipyme
        proceso.proceso_relacionado = info.proceso_relacionado
        proceso.sector = info.sector
        proceso.tiene_lotes = info.tiene_lotes
        proceso.duracion_contrato = info.duracion_contrato
        proceso.fecha_terminacion_contrato = info.fecha_terminacion_contrato
        proceso.direccion_ejecucion = info.direccion_ejecucion
        proceso.usa_documentos_tipo = info.usa_documentos_tipo
        proceso.documentos_tipo_detalle = info.documentos_tipo_detalle
        proceso.estado = info.estado
        proceso.fase = info.fase
        proceso.fase_previa = info.fase_previa
        proceso.precio_base = _parsear_precio(info.precio_estimado_total)

        self.db.flush()  # asegura que proceso.id ya exista para lo que sigue
        return proceso

    def _guardar_cronograma(self, proceso: ProcesoHtmlDescarga, eventos) -> None:
        ahora = datetime.now().isoformat(timespec="seconds")

        for evento_extraido in eventos:
            existente = (
                self.db.query(CronogramaHtmlDescarga)
                .filter_by(proceso_id=proceso.id, evento=evento_extraido.evento)
                .first()
            )

            if existente is None:
                self.db.add(
                    CronogramaHtmlDescarga(
                        proceso_id=proceso.id,
                        evento=evento_extraido.evento,
                        fecha=evento_extraido.fecha,
                        zona_horaria=evento_extraido.zona_horaria,
                    )
                )
                continue

            if existente.fecha != evento_extraido.fecha:
                self.db.add(
                    CronogramaHistorialHtmlDescarga(
                        cronograma_id=existente.id,
                        fecha_anterior=existente.fecha,
                        fecha_nueva=evento_extraido.fecha,
                        detectado_en=ahora,
                    )
                )
                existente.fecha = evento_extraido.fecha

    def _guardar_documentos(self, proceso: ProcesoHtmlDescarga, documentos) -> None:
        existentes = {(d.nombre_documento, d.enlace) for d in proceso.documentos}
        for doc in documentos:
            if (doc.nombre_documento, doc.enlace) not in existentes:
                self.db.add(
                    DocumentoHtmlDescarga(
                        proceso_id=proceso.id,
                        nombre_documento=doc.nombre_documento,
                        enlace=doc.enlace,
                    )
                )

    def _guardar_proponentes(self, proceso: ProcesoHtmlDescarga, proponentes) -> None:
        existentes = {(p.nombre, p.ciudad) for p in proceso.proponentes}
        for prop in proponentes:
            if (prop.nombre, prop.ciudad) not in existentes:
                self.db.add(
                    ProponenteHtmlDescarga(
                        proceso_id=proceso.id, nombre=prop.nombre, ciudad=prop.ciudad
                    )
                )

    def _guardar_observaciones(self, proceso: ProcesoHtmlDescarga, observaciones) -> None:
        existentes = {o.referencia for o in proceso.observaciones if o.referencia}
        for obs in observaciones:
            if obs.referencia and obs.referencia in existentes:
                continue
            self.db.add(
                ObservacionHtmlDescarga(
                    proceso_id=proceso.id,
                    tipo=obs.tipo,
                    referencia=obs.referencia,
                    asunto=obs.asunto,
                    fecha=obs.fecha,
                )
            )

    def _guardar_requisitos(self, proceso: ProcesoHtmlDescarga, requisitos) -> None:
        for antiguo in list(proceso.requisitos):
            self.db.delete(antiguo)
        self.db.flush()

        for req in requisitos:
            self.db.add(
                RequisitoHtmlDescarga(
                    proceso_id=proceso.id,
                    item=req.item,
                    descripcion=req.descripcion,
                    requiere_documento=req.requiere_documento_adjunto,
                )
            )
