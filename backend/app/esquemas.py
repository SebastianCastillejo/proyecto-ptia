# -*- coding: utf-8 -*-
"""Modelos Pydantic con alias camelCase, exactamente como pide docs/contrato-api.md.

El front envía y espera camelCase; internamente trabajamos con snake_case.
Con populate_by_name=True aceptamos ambas formas de nombrar los campos.
"""
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Camel(BaseModel):
    """Base: alias camelCase generados automáticamente."""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class IngredienteNormalizado(Camel):
    entrada: str
    nombre: str
    metodo: str  # exacto | sinonimo | plural | correccion | desconocido


class RespuestaNormalizar(Camel):
    ingredientes: List[IngredienteNormalizado]


class PedidoNormalizar(Camel):
    texto: str


class Sustitucion(Camel):
    necesita: str
    usar: str
    confianza: float


class IngredienteDetalle(Camel):
    nombre: str
    tipo: str          # principal | basico
    estado: str        # tiene | sustituto | despensa | falta
    sustituto: Optional[str] = None


class RecetaRecomendada(Camel):
    id: str
    nombre: str
    tiempo_min: Optional[int]
    imagen_url: Optional[str] = None
    cobertura: float
    aprovechamiento: float
    utilidad: float
    usados: int
    total_usuario: int
    faltantes: List[str]
    sustituciones: List[Sustitucion]
    ingredientes: List[IngredienteDetalle]
    explicacion: str


class RespuestaRecomendaciones(Camel):
    recetas: List[RecetaRecomendada]


class PedidoRecomendacion(Camel):
    ingredientes: List[str]
    incluir_basicos: bool = True
    limite: int = 5


class RespuestaReceta(Camel):
    id: str
    nombre: str
    tiempo_min: Optional[int]
    porciones: int
    imagen_url: Optional[str] = None
    pasos: List[str]


class RespuestaSugerencias(Camel):
    ingredientes: List[str]


class RespuestaSalud(Camel):
    estado: str
    recetas: int
    modelo_puntuacion: str
