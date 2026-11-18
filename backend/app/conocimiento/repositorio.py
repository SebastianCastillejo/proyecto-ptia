# -*- coding: utf-8 -*-
"""Acceso a las recetas en SQLite (datos/aprovecha.db).

La base la construye pipeline/construir_base.py. Este módulo expone lo que
el motor y la API necesitan: listar, obtener por id, contar y sugerencias.
"""
import sqlite3
from functools import lru_cache
from pathlib import Path

from app.config import RUTA_BD


@lru_cache(maxsize=1)
def _conexion(ruta: str) -> sqlite3.Connection:
    con = sqlite3.connect(ruta, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _db() -> sqlite3.Connection:
    if not RUTA_BD.exists():
        raise FileNotFoundError(
            "No existe datos/aprovecha.db. Corre primero: python pipeline/descargar_dataset.py, "
            "python pipeline/limpiar_dataset.py y python pipeline/construir_base.py")
    return _conexion(str(RUTA_BD))


@lru_cache(maxsize=1)
def todas_las_recetas() -> list[dict]:
    """Todas las recetas con sus ingredientes, en forma de dict del motor."""
    filas = _db().execute(
        "SELECT r.id, r.nombre, r.tiempo_min, r.porciones, r.imagen_url, r.pasos, r.pais, r.particion, "
        "i.ingrediente, i.tipo FROM recetas r LEFT JOIN receta_ingrediente i ON i.receta_id=r.id "
        "ORDER BY r.id, i.tipo, i.ingrediente").fetchall()
    por_id = {}
    for f in filas:
        receta = por_id.get(f["id"])
        if receta is None:
            receta = por_id[f["id"]] = {
                "id": f["id"], "nombre": f["nombre"], "tiempoMin": f["tiempo_min"],
                "porciones": f["porciones"], "imagenUrl": f["imagen_url"],
                "principales": [], "basicos": [], "pasos": __import__("json").loads(f["pasos"] or "[]"),
                "pais": f["pais"], "particion": f["particion"],
            }
        if f["ingrediente"] is not None:
            receta["principales" if f["tipo"] == "principal" else "basicos"].append(f["ingrediente"])
    return list(por_id.values())


def obtener_receta(id_receta: str) -> dict | None:
    """Una receta con todos sus datos (endpoint GET /api/recetas/{id})."""
    f = _db().execute("SELECT * FROM recetas WHERE id=?", (id_receta,)).fetchone()
    if f is None:
        return None
    ingredientes = _db().execute(
        "SELECT ingrediente, tipo FROM receta_ingrediente WHERE receta_id=?",
        (id_receta,)).fetchall()
    return {
        "id": f["id"], "nombre": f["nombre"], "tiempo_min": f["tiempo_min"],
        "porciones": f["porciones"], "imagen_url": f["imagen_url"],
        "pasos": __import__("json").loads(f["pasos"] or "[]"),
        "ingredientes": [
            {"ingrediente": i["ingrediente"], "tipo": i["tipo"]} for i in ingredientes],
    }


def contar_recetas() -> int:
    return _db().execute("SELECT COUNT(*) FROM recetas").fetchone()[0]


def sugerencias(limite: int = 8) -> list[str]:
    """Ingredientes principales más frecuentes de la base (máximo `limite`)."""
    filas = _db().execute(
        "SELECT ingrediente, COUNT(*) n FROM receta_ingrediente WHERE tipo='principal' "
        "GROUP BY ingrediente ORDER BY n DESC, ingrediente LIMIT ?", (limite,)).fetchall()
    return [f["ingrediente"] for f in filas]


def ids_por_particion() -> dict[str, list[str]]:
    """{entrenamiento|validacion|prueba: [ids]} para el ML y la evaluación."""
    filas = _db().execute("SELECT id, particion FROM recetas").fetchall()
    resultado = {"entrenamiento": [], "validacion": [], "prueba": []}
    for f in filas:
        if f["particion"] in resultado:
            resultado[f["particion"]].append(f["id"])
    return resultado
