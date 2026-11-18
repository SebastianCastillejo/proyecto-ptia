# -*- coding: utf-8 -*-
"""Puntuación con baseline explicable o un modelo supervisado local."""
import logging
from functools import lru_cache
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from app.config import RAIZ_ML, MODELO_PUNTUACION

logger = logging.getLogger("aprovecha")
CARACTERISTICAS = ["cobertura", "aprovechamiento", "principales_faltantes", "basicos_faltantes", "n_sustituciones", "confianza_media", "n_ingredientes_receta", "n_ingredientes_usuario", "fraccion_principales_cubiertos", "tiempo"]

@lru_cache(maxsize=8)
def _cargar(nombre):
    ruta = Path(RAIZ_ML) / "modelos" / f"{nombre}.joblib"
    if not ruta.is_file():
        return None
    return joblib.load(ruta)

def puntuar(features, nombre=MODELO_PUNTUACION):
    if nombre == "reglas":
        return features["utilidad_reglas"], "reglas"
    paquete = _cargar(nombre)
    if paquete is None:
        logger.warning("No existe el modelo %s; se usa puntuación por reglas", nombre)
        return features["utilidad_reglas"], "reglas"
    x = pd.DataFrame([[features[k] for k in CARACTERISTICAS]], columns=CARACTERISTICAS, dtype=float)
    modelo, escalador = paquete["modelo"], paquete["escalador"]
    x = escalador.transform(x)
    if hasattr(modelo, "predict_proba"):
        valor = float(modelo.predict_proba(x)[0, 1])
    else:
        valor = float(modelo.predict(x)[0])
    return valor, nombre

def modelo_activo():
    """Nombre que efectivamente puntúa; contempla fallback por archivo ausente."""
    if MODELO_PUNTUACION == "reglas" or _cargar(MODELO_PUNTUACION) is None:
        return "reglas"
    return MODELO_PUNTUACION
