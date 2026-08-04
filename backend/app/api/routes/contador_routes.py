from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.db.base import obtener_db
from app.db.models import Contador
from app.models.contador import ContadorEntrada, ContadorRespuesta

router = APIRouter(prefix="/contadores", tags=["contadores"])

ROLES_VALIDOS = {"contador", "revisor_fiscal"}


@router.get("", response_model=list[ContadorRespuesta])
def listar_contadores(db: Session = Depends(obtener_db)):
    """Catálogo de contadores y revisores fiscales."""
    return db.query(Contador).order_by(Contador.nombre).all()


@router.post("", response_model=ContadorRespuesta)
def crear_contador(datos: ContadorEntrada, db: Session = Depends(obtener_db)):
    """
    Registra un contador o revisor fiscal. Se guarda una sola vez y puede
    asignarse luego a varias empresas distintas.
    """
    if not datos.nombre.strip():
        raise HTTPException(status_code=422, detail="El nombre es obligatorio.")

    if datos.rol not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=422,
            detail=f"Rol inválido. Debe ser uno de: {', '.join(sorted(ROLES_VALIDOS))}.",
        )

    contador = Contador(**datos.model_dump())
    db.add(contador)
    db.commit()
    db.refresh(contador)
    logger.info(f"Contador creado: {contador.nombre} ({contador.rol})")
    return contador


@router.put("/{contador_id}", response_model=ContadorRespuesta)
def actualizar_contador(
    contador_id: int, datos: ContadorEntrada, db: Session = Depends(obtener_db)
):
    contador = db.query(Contador).filter_by(id=contador_id).first()
    if contador is None:
        raise HTTPException(status_code=404, detail="El contador no existe.")

    if datos.rol not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=422,
            detail=f"Rol inválido. Debe ser uno de: {', '.join(sorted(ROLES_VALIDOS))}.",
        )

    for campo, valor in datos.model_dump().items():
        setattr(contador, campo, valor)

    db.commit()
    db.refresh(contador)
    return contador


@router.delete("/{contador_id}")
def eliminar_contador(contador_id: int, db: Session = Depends(obtener_db)):
    contador = db.query(Contador).filter_by(id=contador_id).first()
    if contador is None:
        raise HTTPException(status_code=404, detail="El contador no existe.")

    if contador.empresas:
        raise HTTPException(
            status_code=422,
            detail=(
                f"No se puede eliminar: está asignado a "
                f"{len(contador.empresas)} empresa(s)."
            ),
        )

    nombre = contador.nombre
    db.delete(contador)
    db.commit()
    return {"mensaje": f"Contador '{nombre}' eliminado."}
