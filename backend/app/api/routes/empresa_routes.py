from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.db.base import obtener_db
from app.db.models import AccionistaEmpresa, Empresa
from app.models.empresa import EmpresaEntrada, EmpresaRespuesta

router = APIRouter(prefix="/empresas", tags=["empresas"])


def _reemplazar_accionistas(db: Session, empresa: Empresa, datos: EmpresaEntrada) -> None:
    """Los accionistas se reemplazan completos en cada guardado."""
    for antiguo in list(empresa.accionistas):
        db.delete(antiguo)
    db.flush()

    accionistas_a_guardar = datos.accionistas if datos.accionistas else []

    # Si es persona natural y no tiene accionistas, crear uno con sus datos
    if not empresa.es_persona_juridica and not accionistas_a_guardar:
        accionistas_a_guardar = [
            {
                "nombre": empresa.nom_o_raz_social,
                "cedula": "",
                "cedula_ciudad": "",
                "mat_profe": "",
                "direccion_personal": empresa.direccion,
                "ciudad_personal": empresa.ciudad,
                "correo_personal": empresa.correo,
                "telefono_personal_fijo": empresa.telefono_fijo,
                "telefono_personal_celular": empresa.telefono_celular,
                "orden": 1,
                "porcentaje": "100%",
                "es_representante_legal": True,
            }
        ]

    for i, accionista in enumerate(accionistas_a_guardar, start=1):
        # Convertir dict a modelo si es necesario
        if isinstance(accionista, dict):
            accionista_dict = accionista
        else:
            accionista_dict = accionista.model_dump()

        # Si no se especifica orden, usar índice
        if "orden" not in accionista_dict:
            accionista_dict["orden"] = i

        # Para persona natural, marcar como representante legal
        if not empresa.es_persona_juridica and i == 1:
            accionista_dict["es_representante_legal"] = True

        db.add(AccionistaEmpresa(empresa_id=empresa.id, **accionista_dict))


@router.get("", response_model=list[EmpresaRespuesta])
def listar_empresas(db: Session = Depends(obtener_db)):
    """Catálogo de empresas y personas naturales, en orden alfabético."""
    return db.query(Empresa).order_by(Empresa.nom_o_raz_social).all()


@router.get("/{empresa_id}", response_model=EmpresaRespuesta)
def obtener_empresa(empresa_id: int, db: Session = Depends(obtener_db)):
    empresa = db.query(Empresa).filter_by(id=empresa_id).first()
    if empresa is None:
        raise HTTPException(status_code=404, detail="La empresa no existe.")
    return empresa


@router.post("", response_model=EmpresaRespuesta)
def crear_empresa(datos: EmpresaEntrada, db: Session = Depends(obtener_db)):
    """Registra una empresa nueva en el catálogo."""
    if not datos.nom_o_raz_social.strip():
        raise HTTPException(
            status_code=422, detail="El nombre o razón social es obligatorio."
        )

    existente = (
        db.query(Empresa)
        .filter_by(nom_o_raz_social=datos.nom_o_raz_social.strip())
        .first()
    )
    if existente:
        raise HTTPException(
            status_code=422,
            detail=f"Ya existe una empresa llamada '{datos.nom_o_raz_social}'.",
        )

    if datos.contador_id is not None:
        from app.db.models import Contador
        if not db.query(Contador).filter_by(id=datos.contador_id).first():
            raise HTTPException(
                status_code=422,
                detail=f"El contador con id {datos.contador_id} no existe.",
            )

    empresa = Empresa(**datos.model_dump(exclude={'accionistas'}))
    empresa.nom_o_raz_social = datos.nom_o_raz_social.strip()

    db.add(empresa)
    db.flush()

    _reemplazar_accionistas(db, empresa, datos)

    db.commit()
    db.refresh(empresa)
    logger.info(f"Empresa creada: {empresa.nom_o_raz_social}")
    return empresa


@router.put("/{empresa_id}", response_model=EmpresaRespuesta)
def actualizar_empresa(
    empresa_id: int, datos: EmpresaEntrada, db: Session = Depends(obtener_db)
):
    empresa = db.query(Empresa).filter_by(id=empresa_id).first()
    if empresa is None:
        raise HTTPException(status_code=404, detail="La empresa no existe.")

    for campo, valor in datos.model_dump(exclude={'accionistas'}).items():
        setattr(empresa, campo, valor)

    _reemplazar_accionistas(db, empresa, datos)

    db.commit()
    db.refresh(empresa)
    logger.info(f"Empresa actualizada: {empresa.nom_o_raz_social}")
    return empresa


@router.delete("/{empresa_id}")
def eliminar_empresa(empresa_id: int, db: Session = Depends(obtener_db)):
    """
    Elimina una empresa del catálogo, siempre que no esté siendo usada
    por algún proponente ya creado.
    """
    empresa = db.query(Empresa).filter_by(id=empresa_id).first()
    if empresa is None:
        raise HTTPException(status_code=404, detail="La empresa no existe.")

    if empresa.participaciones:
        raise HTTPException(
            status_code=422,
            detail=(
                f"No se puede eliminar '{empresa.nom_o_raz_social}': "
                f"está siendo usada por {len(empresa.participaciones)} proponente(s)."
            ),
        )

    nombre = empresa.nom_o_raz_social
    db.delete(empresa)
    db.commit()
    logger.info(f"Empresa eliminada: {nombre}")
    return {"mensaje": f"Empresa '{nombre}' eliminada."}
