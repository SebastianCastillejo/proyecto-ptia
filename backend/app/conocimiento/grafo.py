# -*- coding: utf-8 -*-
"""Grafo de ingredientes con NetworkX.

Relaciones (sección 5.3 del enunciado):
  - es_sinonimo_de : sinónimo regional -> nombre canónico
  - pertenece_a    : ingrediente -> categoría (proteína, verdura, ...)
  - es_basico      : marca los ingredientes de despensa (sal, aceite, agua...)
  - puede_sustituir_a : ingrediente -> ingrediente con atributo confianza (0-1)
                       y atributo origen ("manual" | "inferida").

La semilla de verdad inicial vive en datos/semilla/ingredientes.json; el
agrupamiento (ml/agrupamiento_ingredientes.py) agrega sustitutos "inferida".
"""
import json
import sqlite3
from functools import lru_cache

import networkx as nx

from app.config import RUTA_SEMILLA


def construir_desde_semilla(ruta=RUTA_SEMILLA) -> dict:
    """Lee la semilla y devuelve {ingredientes, categorias, sinonimos,
    sustitutos, basicos} para poblar el grafo y el normalizador."""
    with open(ruta, encoding="utf-8") as f:
        semilla = json.load(f)
    # La base solo contiene sustituciones inferidas que fueron aprobadas en CSV.
    from app.config import RUTA_BD
    if RUTA_BD.exists():
        try:
            with sqlite3.connect(RUTA_BD) as con:
                filas=con.execute("SELECT necesita,usar,confianza,origen FROM sustitutos").fetchall()
            presentes={(a,b) for a,b,*_ in semilla.get("sustitutos",[])}
            semilla.setdefault("sustitutos",[]).extend([list(f) for f in filas if (f[0],f[1]) not in presentes])
        except sqlite3.Error:
            pass
    return semilla


def construir_grafo(datos: dict | None = None) -> nx.DiGraph:
    """Construye el grafo dirigido con las 4 relaciones del modelo."""
    if datos is None:
        datos = construir_desde_semilla()
    g = nx.DiGraph()
    for nombre, info in datos["ingredientes"].items():
        g.add_node(nombre, categoria=info.get("categoria"), es_basico=info.get("es_basico", False))
        if info.get("es_basico"):
            g.add_edge(nombre, "__basico__", tipo="es_basico")
    for sinonimo, canonico in datos["sinonimos"].items():
        g.add_edge(sinonimo, canonico, tipo="es_sinonimo_de")
    for nombre, info in datos["ingredientes"].items():
        cat = info.get("categoria")
        if cat:
            g.add_edge(nombre, cat, tipo="pertenece_a")
    for necesita, usar, confianza, origen in datos["sustitutos"]:
        g.add_edge(necesita, usar, tipo="puede_sustituir_a", confianza=confianza, origen=origen)
    return g


def sustitutos_de(grafo: nx.DiGraph, ingrediente: str) -> list[tuple[str, float, str]]:
    """Devuelve [(sustituto, confianza, origen)] ordenado por confianza."""
    aristas = [(v, d.get("confianza", 0.5), d.get("origen", "manual"))
               for _, v, d in grafo.out_edges(ingrediente, data=True)
               if d.get("tipo") == "puede_sustituir_a"]
    return sorted(aristas, key=lambda x: -x[1])

