# -*- coding: utf-8 -*-
"""Etapa 1 del motor: normalización de ingredientes.

Orden de búsqueda: coincidencia exacta -> sinónimo -> singular (plural) ->
corrección por similitud -> desconocido.

La corrección usa distancia Damerau-Levenshtein (OSA, RapidFuzz), que tolera
transposiciones de letras: "tomtae" -> "tomate" con distancia 1.
"""
import re
import unicodedata
from functools import lru_cache

from rapidfuzz import fuzz
from rapidfuzz.distance import OSA

from app.config import UMBRAL_SIMILITUD, BASICOS

_PATRON_COMA = re.compile(r"[,;\n]+")


def quitar_tildes(texto: str) -> str:
    """Minúsculas, sin tildes y con espacios colapsados."""
    texto = (texto or "").lower().strip()
    texto = "".join(c for c in unicodedata.normalize("NFD", texto)
                    if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texto).strip()


class Normalizador:
    """Normaliza términos del usuario al vocabulario canónico del grafo."""

    def __init__(self, vocabulario: dict, sinonimos: dict):
        # vocabulario: {sin_tildes: nombre_canonico}; sinonimos: {sin_tildes: canonico}
        self.vocabulario = vocabulario
        self.sinonimos = sinonimos
        self._terminos = list(vocabulario.keys())

    def normalizar(self, entrada: str) -> dict:
        """Devuelve {entrada, nombre, metodo}: exacto|sinonimo|plural|correccion|desconocido."""
        entrada = (entrada or "").strip()
        t = quitar_tildes(entrada)
        if not t:
            return {"entrada": entrada, "nombre": entrada, "metodo": "desconocido"}
        # 1. Coincidencia exacta con el vocabulario (o con un básico).
        if t in self.vocabulario or t in {quitar_tildes(b) for b in BASICOS}:
            return {"entrada": entrada, "nombre": self.vocabulario.get(t, entrada), "metodo": "exacto"}
        # 2. Sinónimo declarado en el grafo.
        if t in self.sinonimos:
            return {"entrada": entrada, "nombre": self.sinonimos[t], "metodo": "sinonimo"}
        # 3. Plural -> singular (prueba con "es" y con "s").
        for singular in (re.sub(r"es$", "", t), re.sub(r"s$", "", t)):
            if singular != t and singular in self.vocabulario:
                return {"entrada": entrada, "nombre": self.vocabulario[singular], "metodo": "plural"}
            if singular != t and singular in self.sinonimos:
                return {"entrada": entrada, "nombre": self.sinonimos[singular], "metodo": "plural"}
        # 4. Corrección por similitud con Damerau-Levenshtein (OSA), igual que
        #    el mock: se acepta si la distancia es <= max(1, 20 % del largo) y
        #    además la similitud normalizada supera el umbral de config.py.
        if len(t) >= 4:
            mejor, mejor_dist = None, None
            for candidato in self._terminos:
                d = OSA.distance(t, candidato)
                if mejor_dist is None or d < mejor_dist:
                    mejor, mejor_dist = candidato, d
            permitida = max(1, int(len(mejor) * 0.2)) if mejor else 0
            puntaje = fuzz.ratio(t, mejor) if mejor else 0.0
            # Un intercambio adyacente (p. ej. tomtae) tiene similitud de
            # caracteres menor a 85% aunque su distancia Damerau sea 1; se
            # acepta esa operación elemental por la regla de distancia del mock.
            transposicion_simple = bool(mejor and mejor_dist == 1 and len(t) == len(mejor))
            if mejor and mejor_dist <= permitida and (puntaje >= UMBRAL_SIMILITUD or transposicion_simple):
                return {"entrada": entrada, "nombre": self.vocabulario[mejor], "metodo": "correccion"}
        # 5. Desconocido: se conserva el texto tal cual (el front lo avisa).
        return {"entrada": entrada, "nombre": entrada, "metodo": "desconocido"}


def normalizar_texto(texto: str, normalizador: "Normalizador | None" = None) -> list[dict]:
    """Separa por comas/punto y coma y normaliza cada término."""
    if normalizador is None:
        normalizador = normalizador_por_defecto()
    return [normalizador.normalizar(term.strip())
            for term in _PATRON_COMA.split(texto or "") if term.strip()]


@lru_cache(maxsize=1)
def normalizador_por_defecto() -> Normalizador:
    """Construye el normalizador con el grafo de la base real (cacheado)."""
    from app.conocimiento.grafo import construir_desde_semilla
    datos = construir_desde_semilla()
    # Si varias claves se distinguen solo por tildes, preferimos la forma
    # observada con mayor frecuencia. Los alias regionales nunca desplazan al
    # nombre canónico, aunque el texto del alias aparezca en recetas antiguas.
    alias = {quitar_tildes(k) for k in datos["sinonimos"]}
    vocabulario = {}
    frecuencias = {}
    for nombre, info in datos["ingredientes"].items():
        clave = quitar_tildes(nombre)
        if clave in alias:
            continue
        frecuencia = int(info.get("frecuencia", 0))
        if clave not in frecuencias or frecuencia > frecuencias[clave]:
            vocabulario[clave] = nombre
            frecuencias[clave] = frecuencia
    for b in BASICOS:
        vocabulario.setdefault(quitar_tildes(b), b)
    sinonimos = {quitar_tildes(k): v for k, v in datos["sinonimos"].items()}
    return Normalizador(vocabulario, sinonimos)
