# -*- coding: utf-8 -*-
"""Orquesta recuperación, utilidad y explicaciones de recetas."""
from app.config import COBERTURA_MINIMA, BASICOS
from app.conocimiento.grafo import construir_desde_semilla
from app.motor.caracteristicas import calcular_caracteristicas
from app.motor.puntuacion import puntuar
from app.motor.normalizador import normalizador_por_defecto
from app.motor.explicacion import frase_explicativa
from app.motor.recuperacion import construir_indice, indice_por_defecto, ids_recuperables

MODO_EVALUACION = None
IGNORAR_SUSTITUCIONES = False

def _mapa_sustitutos():
    if IGNORAR_SUSTITUCIONES:
        return {}
    resultado = {}
    for necesita, usar, confianza, origen in construir_desde_semilla()["sustitutos"]:
        resultado.setdefault(necesita, []).append((usar, confianza, origen))
    return resultado

def recomendar(ingredientes, incluir_basicos=True, limite=5, recetas=None, modo=None):
    """Devuelve las mejores recetas con explicación; argumentos de fixtures para paridad."""
    normalizador = normalizador_por_defecto()
    canonicos = []
    for item in ingredientes:
        salida = normalizador.normalizar(item)
        if salida["metodo"] != "desconocido": canonicos.append(salida["nombre"])
    basicos = set(BASICOS)
    if recetas is None:
        recetas, indice, sustitutos = indice_por_defecto()
        if IGNORAR_SUSTITUCIONES:
            sustitutos = {}
    else:
        indice=construir_indice(recetas); sustitutos=_mapa_sustitutos()
    sustitutos_recuperacion={a:[(b,c,o) for b,c,o in opciones] for a,opciones in sustitutos.items()}
    principales_usuario=[i for i in canonicos if i not in basicos]
    ids_candidatos=ids_recuperables(principales_usuario,indice,sustitutos_recuperacion)
    recetas_por_id={r["id"]:r for r in recetas}
    orden={r["id"]:pos for pos,r in enumerate(recetas)}
    candidatas=[recetas_por_id[i] for i in sorted(ids_candidatos,key=lambda x:orden.get(x,10**12)) if i in recetas_por_id]
    resultados = []
    for receta in candidatas:
        f = calcular_caracteristicas(canonicos, receta, sustitutos, incluir_basicos)
        # Recuperación de al menos dos coincidencias principales, como el mock.
        if f["cobertura"] < COBERTURA_MINIMA: continue
        utilidad, _ = puntuar(f, modo or MODO_EVALUACION) if (modo or MODO_EVALUACION) else puntuar(f)
        nombre = receta["nombre"]
        reemplazos = [{"necesita": a, "usar": b, "confianza": c} for a,b,c in f["sustituciones"]]
        frase = frase_explicativa(f["usados"],f["total_usuario"],f["cobertura"],reemplazos,f["faltantes"])
        resultados.append({"id": receta["id"], "nombre": nombre, "tiempo_min": receta.get("tiempoMin"), "imagen_url": receta.get("imagenUrl"), "cobertura": round(f["cobertura"],3), "aprovechamiento": round(f["aprovechamiento"],3), "utilidad": round(utilidad,3), "usados":f["usados"], "total_usuario":f["total_usuario"], "faltantes":f["faltantes"], "sustituciones":reemplazos, "ingredientes":f["detalle"], "explicacion":frase, "_faltantes_n":len(f["faltantes"]), "_tiempo":receta.get("tiempoMin") or 99999})
    resultados.sort(key=lambda x:(-x["utilidad"],x["_faltantes_n"],x["_tiempo"]))
    for r in resultados:
        r.pop("_faltantes_n"); r.pop("_tiempo")
    return resultados[:limite]
