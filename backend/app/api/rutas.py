# -*- coding: utf-8 -*-
"""Los 4 endpoints del contrato + GET /api/salud.

Toda la lógica vive en app/motor/ y app/conocimiento/: las rutas solo
traducen HTTP. Los errores 404/422 usan {"detail": "..."} como pide el contrato.
"""
import logging
from fastapi import APIRouter, HTTPException

from app.motor.puntuacion import modelo_activo
from app.esquemas import (
    PedidoNormalizar, PedidoRecomendacion, RespuestaNormalizar,
    RespuestaRecomendaciones, RespuestaReceta, RespuestaSugerencias,
    RespuestaSalud,
)
from app.motor.recomendador import recomendar
from app.motor.normalizador import normalizar_texto
from app.conocimiento.repositorio import obtener_receta, contar_recetas, sugerencias

logger = logging.getLogger("aprovecha")

enrutador = APIRouter()


@enrutador.post("/ingredientes/normalizar", response_model=RespuestaNormalizar)
def endpoint_normalizar(pedido: PedidoNormalizar):
    """Normaliza texto libre ("jitomate, arros") a ingredientes canónicos."""
    return RespuestaNormalizar(ingredientes=normalizar_texto(pedido.texto))


@enrutador.post("/recomendaciones", response_model=RespuestaRecomendaciones, response_model_exclude_unset=True)
def endpoint_recomendaciones(pedido: PedidoRecomendacion):
    # Validaciones del contrato: lista vacía -> 422; limite entre 1 y 10.
    if not pedido.ingredientes:
        raise HTTPException(422, "Escribe al menos un ingrediente para buscar recetas.")
    if not 1 <= pedido.limite <= 10:
        raise HTTPException(422, "El límite de recetas debe estar entre 1 y 10.")
    return RespuestaRecomendaciones(recetas=recomendar(
        pedido.ingredientes, pedido.incluir_basicos, pedido.limite,
    ))


@enrutador.get("/recetas/{id_receta}", response_model=RespuestaReceta, response_model_exclude_unset=True)
def endpoint_receta(id_receta: str):
    receta = obtener_receta(id_receta)
    if receta is None:
        raise HTTPException(404, "No encontramos esa receta.")
    return RespuestaReceta(**receta)


@enrutador.get("/ingredientes/sugerencias", response_model=RespuestaSugerencias)
def endpoint_sugerencias():
    """Los ingredientes más frecuentes de la base, máximo 8."""
    return RespuestaSugerencias(ingredientes=sugerencias(8))


@enrutador.get("/salud", response_model=RespuestaSalud)
def endpoint_salud():
    try:
        cantidad = contar_recetas()
    except FileNotFoundError:
        cantidad = 0
    return RespuestaSalud(
        estado="ok",
        recetas=cantidad,
        modelo_puntuacion=modelo_activo(),
    )
