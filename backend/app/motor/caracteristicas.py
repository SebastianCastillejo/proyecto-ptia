# -*- coding: utf-8 -*-
"""Características compartidas por el entrenamiento y el motor."""
from app.config import PESO_PRINCIPAL, PESO_BASICO, W_COBERTURA, W_APROVECHAMIENTO, PENALIZACION_FALTANTE


def calcular_caracteristicas(ingredientes_usuario, receta, sustitutos, incluir_basicos=True):
    """Calcula cobertura, aprovechamiento y señales descriptivas de un par."""
    tiene = set(ingredientes_usuario)
    basicos = set(receta.get("basicos", []))
    principales = receta.get("principales", [])
    total_peso = suma = 0.0
    usados = set()
    faltantes = []
    reemplazos = []
    detalle = []
    for ing in principales:
        total_peso += PESO_PRINCIPAL
        if ing in tiene:
            suma += PESO_PRINCIPAL; usados.add(ing)
            detalle.append({"nombre": ing, "tipo": "principal", "estado": "tiene"})
            continue
        opciones = sustitutos.get(ing, [])
        opcion = next((o for o in opciones if o[0] in tiene), None)
        if opcion:
            reemplazo, confianza = opcion[0], float(opcion[1])
            suma += PESO_PRINCIPAL * confianza; usados.add(reemplazo)
            reemplazos.append((ing, reemplazo, confianza))
            detalle.append({"nombre": ing, "tipo": "principal", "estado": "sustituto", "sustituto": reemplazo})
        else:
            faltantes.append(ing)
            detalle.append({"nombre": ing, "tipo": "principal", "estado": "falta"})
    for ing in receta.get("basicos", []):
        total_peso += PESO_BASICO
        disponible = incluir_basicos or ing in tiene
        if disponible: suma += PESO_BASICO
        else: faltantes.append(ing)
        detalle.append({"nombre": ing, "tipo": "basico", "estado": "despensa" if incluir_basicos else ("tiene" if ing in tiene else "falta")})
    del_usuario = [i for i in ingredientes_usuario if i not in basicos]
    cobertura = suma / total_peso if total_peso else 0.0
    aprovechamiento = len(set(del_usuario) & usados) / len(del_usuario) if del_usuario else 0.0
    principales_faltantes = [i for i in faltantes if i in principales]
    penalizacion = PENALIZACION_FALTANTE * len(principales_faltantes)
    utilidad = W_COBERTURA * cobertura + W_APROVECHAMIENTO * aprovechamiento - penalizacion
    return {
        "cobertura": cobertura, "aprovechamiento": aprovechamiento, "penalizacion": penalizacion,
        "utilidad_reglas": utilidad, "usados": len(set(del_usuario) & usados), "total_usuario": len(del_usuario),
        "faltantes": faltantes, "sustituciones": reemplazos, "detalle": detalle,
        "principales_faltantes": len(principales_faltantes), "basicos_faltantes": len([i for i in faltantes if i not in principales]),
        "n_sustituciones": len(reemplazos), "confianza_media": sum(x[2] for x in reemplazos) / len(reemplazos) if reemplazos else 0.0,
        "n_ingredientes_receta": len(principales) + len(basicos), "n_ingredientes_usuario": len(del_usuario),
        "fraccion_principales_cubiertos": (len(principales) - len(principales_faltantes)) / len(principales) if principales else 0.0,
        "tiempo": float(receta.get("tiempoMin") or 0),
    }

