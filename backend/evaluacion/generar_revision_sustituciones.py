# -*- coding: utf-8 -*-
"""Exporta hasta 50 oportunidades de sustitución para revisión culinaria."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from app.conocimiento.repositorio import todas_las_recetas
from app.conocimiento.grafo import construir_desde_semilla
def main():
 root=Path(__file__).resolve().parents[1]; recetas=todas_las_recetas(); seed=construir_desde_semilla(); rows=[]
 for r in recetas:
  for necesita,usar,confianza,origen in seed["sustitutos"]:
   if necesita in r["principales"] and usar not in r["principales"]:
    rows.append({"receta":r["nombre"],"ingrediente_necesitado":necesita,"sustituto":usar,"confianza":confianza,"origen":origen,"valida_si_no":""})
    if len(rows)>=50:break
  if len(rows)>=50:break
 if len(rows)<50:
  # Las relaciones manuales pueden aparecer en pocas recetas; se proponen por
  # contexto de necesidad y se conserva el motivo en las mismas columnas.
  for a,b,c,o in seed["sustitutos"]:
   rows.append({"receta":"Revisión general","ingrediente_necesitado":a,"sustituto":b,"confianza":c,"origen":o,"valida_si_no":""})
   if len(rows)>=50:break
 pd.DataFrame(rows).to_csv(root/"evaluacion"/"sustituciones_revision.csv",index=False)
 print(f"Oportunidades exportadas: {len(rows)}; etiquetas humanas vacías.")
if __name__=="__main__":main()
