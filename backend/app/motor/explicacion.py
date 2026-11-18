# -*- coding: utf-8 -*-
"""Construcción de frases y orden estable del ranking."""
def frase_explicativa(usados, total_usuario, cobertura, sustituciones, faltantes):
    texto=f"Aprovecha {usados} de tus {total_usuario} ingredientes y cubre el {round(cobertura*100)}% de la receta."
    if sustituciones:
        texto += " Puedes reemplazar " + " y ".join(f"{s['necesita']} por {s['usar']}" for s in sustituciones) + "."
    texto += " Solo te faltaría: " + ", ".join(faltantes) + "." if faltantes else " No te falta nada."
    return texto

def ordenar_recomendaciones(recetas):
    return sorted(recetas,key=lambda x:(-x["utilidad"],len(x["faltantes"]),x.get("tiempoMin") or 99999))
