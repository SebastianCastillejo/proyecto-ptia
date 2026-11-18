# -*- coding: utf-8 -*-
"""Configuración central del backend: pesos, umbrales y modelo de puntuación.

Aquí vive TODO lo ajustable del motor. Si el informe final propone cambiar un
peso o un umbral, se cambia aquí y todo el sistema (motor, ML y evaluación) usa
el nuevo valor.
"""
import os
from pathlib import Path

# ---------------------------------------------------------------- rutas
# backend/ es la raíz de este módulo; el proyecto completo está un nivel arriba.
RAIZ_BACKEND = Path(__file__).resolve().parent.parent
RAIZ_DATOS = RAIZ_BACKEND / "datos"
RAIZ_ML = RAIZ_BACKEND / "ml"
RUTA_BD = RAIZ_DATOS / "aprovecha.db"
RUTA_SEMILLA = RAIZ_DATOS / "semilla" / "ingredientes.json"
RUTA_PROCESADO = RAIZ_DATOS / "procesado" / "recetas.parquet"

# ------------------------------------------------- pesos del modo reglas
# Baseline de reglas (sección 6.e del documento). También sirve de respaldo
# cuando no existe el archivo del modelo aprendido.
PESO_PRINCIPAL = 1.0
PESO_BASICO = 0.3
COBERTURA_MINIMA = 0.5
PENALIZACION_FALTANTE = 0.1
W_COBERTURA = 0.6
W_APROVECHAMIENTO = 0.4
BASICOS = {"sal", "aceite", "agua", "pimienta"}

# --------------------------------------------- modelo de puntuación activo
# Valores válidos: reglas | perceptron | logistica | arbol | red
# El mejor según F1 en validación se deja escrito tras entrenar (sección 7.3).
_MODELO_ENV = os.environ.get("MODELO_PUNTUACION", "").strip().lower()
MODELOS_VALIDOS = {"reglas", "perceptron", "logistica", "arbol", "red"}
# La selección entrenada se guarda en resultados/modelo_elegido.json. Antes
# de entrenar, el fallback reproducible es reglas.
try:
    import json
    _seleccion = RAIZ_ML / "resultados" / "modelo_elegido.json"
    MODELO_POR_DEFECTO = json.loads(_seleccion.read_text(encoding="utf8")).get("modelo", "reglas") if _seleccion.exists() else "reglas"
except Exception:
    MODELO_POR_DEFECTO = "reglas"
MODELO_PUNTUACION = _MODELO_ENV if _MODELO_ENV in MODELOS_VALIDOS else MODELO_POR_DEFECTO

# ----------------------------------------------------- normalizador
UMBRAL_SIMILITUD = 85  # RapidFuzz, escala 0-100, tolera transposiciones (Damerau-Levenshtein)

# ----------------------------------------------------- API
ORIGENES_CORS = [o for o in os.environ.get("CORS_ORIGINS", "").split(",") if o]

# ------------------------------------------- parámetros del aprendizaje
SEMILLA = 42
ETIQUETA_COBERTURA_POSITIVA = 0.70  # candidata positiva si cubre ≥ 70 % de principales
