# app/Medicamentos.py — primera parte
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.datos import MEDICAMENTOS
from app.esquemas import Medicamento, MedicamentoActualizar, MedicamentoCrear

router = APIRouter(prefix="/medicamentoss", tags=["medicamentoss"])


def obtener_medicamentos(codigo: str) -> dict:
    """Devuelve el diccionario de la medicamentos o lanza 404."""
    for medicamentos in MEDICAMENTOS:
        if medicamentos["codigo"] == codigo.upper():
            return medicamentos
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe la medicamentos '{codigo}'",
    )


MedicamentoEncontrada = Annotated[dict, Depends(obtener_medicamentos)]

@router.get("", response_model=list[Medicamento])
def listar_medicamentoss(
    semestre: Annotated[int | None, Query(ge=1, le=10)] = None,
    solo_obligatorias: bool = False,
) -> list[dict]:
    resultado = MEDICAMENTOS
    if semestre is not None:
        resultado = [m for m in resultado if m["semestre"] == semestre]
    if solo_obligatorias:
        resultado = [m for m in resultado if m["obligatoria"]]
    return resultado


@router.post("", response_model=Medicamento, status_code=status.HTTP_201_CREATED)
def crear_medicamentos(nueva: MedicamentoCrear) -> dict:
    if any(m["codigo"] == nueva.codigo for m in MEDICAMENTOS):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La medicamentos '{nueva.codigo}' ya existe",
        )
    MEDICAMENTOS.append(nueva.model_dump())
    return MEDICAMENTOS[-1]


@router.get("/{codigo}", response_model=Medicamento)
def ver_medicamentos(medicamentos: MedicamentoEncontrada) -> dict:
    return medicamentos


@router.put("/{codigo}", response_model=Medicamento)
def actualizar_medicamentos(cambios: MedicamentoActualizar, medicamentos: MedicamentoEncontrada) -> dict:
    medicamentos.update(cambios.model_dump(exclude_unset=True))
    return medicamentos


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_medicamentos(medicamentos: MedicamentoEncontrada) -> None:
    MEDICAMENTOS.remove(medicamentos)