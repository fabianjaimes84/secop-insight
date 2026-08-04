from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.db.base import obtener_db
from app.db.models import Empresa, IntegranteProponente, ProponentePerfil
from app.models.proponente_perfil import (
    ProponentePerfilEntrada,
    ProponentePerfilRespuesta,
    ProponentePerfilResumen,
)

router = APIRouter(prefix="/proponentes", tags=["proponentes"])

TIPOS_VALIDOS = {"natural", "consorcio", "union_temporal"}


def _validar(datos: ProponentePerfilEntrada, db: Session) -> None:
    """Comprobaciones antes de guardar un proponente."""

    if datos.tipo not in TIPOS_VALIDOS:
        raise HTTPException(
            status_code=422,
            detail=f"Tipo inválido. Debe ser uno de: {', '.join(sorted(TIPOS_VALIDOS))}.",
        )

    if not datos.nombre.strip():
        raise HTTPException(status_code=422, detail="El nombre es obligatorio.")

    if not datos.integrantes:
        raise HTTPException(
            status_code=422, detail="Debes agregar al menos una empresa."
        )

    # Todas las empresas referenciadas deben existir
    for integrante in datos.integrantes:
        if not db.query(Empresa).filter_by(id=integrante.empresa_id).first():
            raise HTTPException(
                status_code=422,
                detail=f"La empresa con id {integrante.empresa_id} no existe.",
            )

    # No repetir la misma empresa dentro del mismo proponente
    ids = [i.empresa_id for i in datos.integrantes]
    if len(ids) != len(set(ids)):
        raise HTTPException(
            status_code=422,
            detail="No puedes agregar la misma empresa dos veces.",
        )

    # El representante debe ser de una de las empresas participantes
    if datos.representante_empresa_id is not None:
        ids_participantes = {i.empresa_id for i in datos.integrantes}
        if datos.representante_empresa_id not in ids_participantes:
            raise HTTPException(
                status_code=422,
                detail=(
                    "El representante debe pertenecer a una de las empresas "
                    "que conforman el proponente."
                ),
            )

    if datos.tipo == "natural":
        if len(datos.integrantes) > 1:
            raise HTTPException(
                status_code=422,
                detail="Una persona natural solo puede tener una empresa.",
            )
        return

    # En consorcios y uniones temporales debe haber exactamente un líder
    lideres = [i for i in datos.integrantes if i.es_lider]

    if len(lideres) == 0:
        raise HTTPException(
            status_code=422,
            detail="Debes marcar cuál empresa es el proponente líder.",
        )

    if len(lideres) > 1:
        raise HTTPException(
            status_code=422, detail="Solo puede haber un proponente líder."
        )


def _reemplazar_integrantes(
    db: Session, perfil: ProponentePerfil, datos: ProponentePerfilEntrada
) -> None:
    """Los integrantes se reemplazan completos en cada guardado."""
    for antiguo in list(perfil.integrantes):
        db.delete(antiguo)
    db.flush()

    for integrante in datos.integrantes:
        db.add(
            IntegranteProponente(perfil_id=perfil.id, **integrante.model_dump())
        )


@router.get("", response_model=list[ProponentePerfilResumen])
def listar_proponentes(db: Session = Depends(obtener_db)):
    """Lista los proponentes guardados, para el selector."""
    return db.query(ProponentePerfil).order_by(ProponentePerfil.nombre).all()


@router.get("/{perfil_id}", response_model=ProponentePerfilRespuesta)
def obtener_proponente(perfil_id: int, db: Session = Depends(obtener_db)):
    """Devuelve un proponente con sus empresas integrantes completas."""
    perfil = db.query(ProponentePerfil).filter_by(id=perfil_id).first()
    if perfil is None:
        raise HTTPException(status_code=404, detail="El proponente no existe.")
    return perfil


@router.post("", response_model=ProponentePerfilRespuesta)
def crear_proponente(
    datos: ProponentePerfilEntrada, db: Session = Depends(obtener_db)
):
    """Crea un proponente combinando empresas del catálogo."""
    _validar(datos, db)

    perfil = ProponentePerfil(
        tipo=datos.tipo,
        nombre=datos.nombre.strip(),
        codigo_proceso=datos.codigo_proceso.strip(),
        representante_empresa_id=datos.representante_empresa_id,
        entidad_telefono=datos.entidad_telefono,
        entidad_pagina=datos.entidad_pagina,
        entidad_horario=datos.entidad_horario,
        entidad_correo=datos.entidad_correo,
        fecha_cierre=datos.fecha_cierre,
        fecha_carta_gerencia=datos.fecha_carta_gerencia,
        pers_clave_eval=datos.pers_clave_eval,
    )
    db.add(perfil)
    db.flush()

    _reemplazar_integrantes(db, perfil, datos)

    db.commit()
    db.refresh(perfil)
    logger.info(f"Proponente creado: {perfil.nombre} ({perfil.tipo})")
    return perfil


@router.put("/{perfil_id}", response_model=ProponentePerfilRespuesta)
def actualizar_proponente(
    perfil_id: int,
    datos: ProponentePerfilEntrada,
    db: Session = Depends(obtener_db),
):
    perfil = db.query(ProponentePerfil).filter_by(id=perfil_id).first()
    if perfil is None:
        raise HTTPException(status_code=404, detail="El proponente no existe.")

    _validar(datos, db)

    perfil.tipo = datos.tipo
    perfil.nombre = datos.nombre.strip()
    perfil.codigo_proceso = datos.codigo_proceso.strip()
    perfil.representante_empresa_id = datos.representante_empresa_id
    perfil.entidad_telefono = datos.entidad_telefono
    perfil.entidad_pagina = datos.entidad_pagina
    perfil.entidad_horario = datos.entidad_horario
    perfil.entidad_correo = datos.entidad_correo
    perfil.fecha_cierre = datos.fecha_cierre
    perfil.fecha_carta_gerencia = datos.fecha_carta_gerencia
    perfil.pers_clave_eval = datos.pers_clave_eval

    _reemplazar_integrantes(db, perfil, datos)

    db.commit()
    db.refresh(perfil)
    logger.info(f"Proponente actualizado: {perfil.nombre}")
    return perfil


@router.delete("/{perfil_id}")
def eliminar_proponente(perfil_id: int, db: Session = Depends(obtener_db)):
    perfil = db.query(ProponentePerfil).filter_by(id=perfil_id).first()
    if perfil is None:
        raise HTTPException(status_code=404, detail="El proponente no existe.")

    nombre = perfil.nombre
    db.delete(perfil)
    db.commit()
    logger.info(f"Proponente eliminado: {nombre}")
    return {"mensaje": f"Proponente '{nombre}' eliminado."}
