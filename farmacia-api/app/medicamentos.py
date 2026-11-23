# app/Medicamentos.py — primera parte
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.datos import MEDICAMENTOS
from app.esquemas import Medicamento, MedicamentoActualizar, MedicamentoCrear

router = APIRouter(prefix="/medicamentos", tags=["medicamentos"])


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
def listar_medicamentos(
    categoria: Annotated[int | None, Query(ge=1, le=100)] = None,
    requiere_receta: bool = False,
) -> list[dict]:
    resultado = MEDICAMENTOS
    if categoria is not None:
        resultado = [m for m in resultado if m["categoria"] == categoria]
    if requiere_receta:
        resultado = [m for m in resultado if m["requiere receta"]]
    return resultado

# PREGUNTA 2:

@router.get("/pedido")
def calcular_pedido(
    unidades: Annotated[int, Query(ge=1, le=500)],
    categoria: Annotated[int | None, Query(ge=1, le=100)] = None,
):
    if categoria is not None:
        seleccion = [h for h in MEDICAMENTOS if h["categoria"] == categoria]
    else:
        seleccion = MEDICAMENTOS

    if not seleccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay medicamentos de la categoria {categoria}",
        )

    cantidad = len(seleccion)
    suma_medicamentos = sum(h["precio"] for h in seleccion)
    con_receta_count = sum(1 for h in seleccion if h["requiere_receta"])

    precio_promedio = round(suma_medicamentos / cantidad, 2)
    valor_base = suma_medicamentos * unidades


    descuento_aplicado = unidades >= 100
    if descuento_aplicado:
        valor_estimado = round(valor_base * 1.2, 2)
    else:
        valor_estimado = float(valor_base)

    porcentaje_con_receta = round((con_receta_count / cantidad) * 100, 1)

    return {
        "medicamentos": cantidad,
        "unidades": unidades,
        "precio_promedio": precio_promedio,
        "valor_base": valor_base,
        "descuento_aplicado": descuento_aplicado,
        "valor_estimado": valor_estimado,
        "porcentaje_con_receta": porcentaje_con_receta,
    }

# PREGUNTA 3:

@router.get("/disponibilidad")
def consultar_disponibilidad(
    agotados: Annotated[list[str] | None, Query()] = None,
):

    if not MEDICAMENTOS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay medicamentos registrados",
        )

    codigos_agotados = {cod.upper() for cod in agotados} if agotados else set()
    total = 0
    cant_agotados = 0
    cant_disponibles = 0
    valor_disponibles = 0
    disponible_mas_economico: str | None = None
    menor_medicamento = float("inf")

    for med in MEDICAMENTOS:
        total += 1
        if med["codigo"] in codigos_agotados:
            cant_agotados += 1
        else:
            cant_disponibles += 1
            valor_disponibles += med["precio"]
            if med["precio"] < menor_medicamento:
                menor_medicamento = med["precio"]
                disponible_mas_economico = med["codigo"]

    porcentaje_agotado = round((cant_agotados / total) * 100, 1)

    return {
        "total": total,
        "agotados": cant_agotados,
        "disponibles": cant_disponibles,
        "porcentaje_agotado": porcentaje_agotado,
        "valor_disponibles": valor_disponibles,
        "disponible_mas_economico": disponible_mas_economico,
    }

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
