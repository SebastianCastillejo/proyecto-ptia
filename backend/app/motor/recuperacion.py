# -*- coding: utf-8 -*-
"""Etapa 2: recuperación de recetas candidatas con índice invertido.

Candidatas = recetas que comparten al menos 2 ingredientes principales con el
usuario (directamente o porque el usuario tiene un sustituto de alguno); al
menos 1 si el usuario tiene menos de 2 ingredientes. El índice invertido
ingrediente -> recetas se construye una sola vez (cacheado) sobre la base.
"""
from functools import lru_cache

from app.conocimiento.repositorio import todas_las_recetas
from app.conocimiento.grafo import construir_desde_semilla


def construir_indice(recetas: list[dict]) -> dict:
    """{ingrediente: set(ids)} a partir de los ingredientes principales."""
    indice = {}
    for r in recetas:
        for i in r["principales"]:
            indice.setdefault(i, set()).add(r["id"])
    return indice


def recuperar(ingredientes_usuario: list[str], recetas: list[dict],
              indice: dict, sustitutos: dict) -> list[dict]:
    """Devuelve las recetas candidatas.

    sustitutos: {necesitado: [(sustituto, confianza, origen), ...]} — si el
    usuario tiene un sustituto de X, la receta que pide X comparte con él.
    """
    ids = ids_recuperables(ingredientes_usuario, indice, sustitutos)
    return [r for r in recetas if r["id"] in ids]

def ids_recuperables(ingredientes_usuario: list[str], indice: dict, sustitutos: dict) -> set[str]:
    """Obtiene ids candidatas directamente del índice, sin recorrer recetas."""
    tiene = set(ingredientes_usuario)
    # Ingredientes necesitados por recetas que el usuario puede cubrir.
    puede_sustituir = {necesitado for necesitado, opciones in sustitutos.items()
                       if any(op[0] in tiene for op in opciones)}
    compartidos: dict[str, int] = {}
    for ing in tiene:
        for id_receta in indice.get(ing, set()):
            compartidos[id_receta] = compartidos.get(id_receta, 0) + 1
    for necesitado in puede_sustituir:
        for id_receta in indice.get(necesitado, set()):
            compartidos[id_receta] = compartidos.get(id_receta, 0) + 1
    minimo = 1 if len(tiene) < 2 else 2
    return {rid for rid,n in compartidos.items() if n >= minimo}


@lru_cache(maxsize=1)
def indice_por_defecto():
    """Índice y mapa de sustitutos sobre la base real (cacheado)."""
    from app.conocimiento.grafo import construir_desde_semilla
    recetas = todas_las_recetas()
    semilla = construir_desde_semilla()
    sustitutos: dict[str, list[tuple[str, float, str]]] = {}
    for necesita, usar, confianza, origen in semilla["sustitutos"]:
        sustitutos.setdefault(necesita, []).append((usar, confianza, origen))
    for lista in sustitutos.values():
        lista.sort(key=lambda x: -x[1])
    return recetas, construir_indice(recetas), sustitutos
