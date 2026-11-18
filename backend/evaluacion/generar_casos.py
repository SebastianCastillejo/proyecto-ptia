# -*- coding: utf-8 -*-
"""Crea listas de prueba reproducibles a partir de la partición de prueba."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json, random
from app.config import SEMILLA
from app.conocimiento.repositorio import todas_las_recetas
def main():
 root=Path(__file__).resolve().parents[1]; recetas=[r for r in todas_las_recetas() if r["particion"]=="prueba"]; rng=random.Random(SEMILLA); casos=[]
 semilla=json.loads((root/"datos"/"semilla"/"ingredientes.json").read_text(encoding="utf8")); categorias={n:i.get("categoria") for n,i in semilla["ingredientes"].items()}
 for r in recetas[:max(30,min(100,len(recetas)))]:
  if len(r["principales"])<3: continue
  quitar=rng.sample(r["principales"],min(rng.randint(1,2),len(r["principales"])-1)); nevera=[i for i in r["principales"] if i not in quitar]
  categoria=categorias.get(rng.choice(r["principales"]),"")
  otros=sorted({i for x in recetas for i in x["principales"] if i not in nevera and i not in r["principales"] and categorias.get(i)==categoria})
  if otros: nevera.append(rng.choice(otros))
  casos.append({"recetaOriginal":r["id"],"nombreEsperado":r["nombre"],"ingredientes":nevera,"quitados":quitar})
 # Caso verificable de transposición tomada de una lista derivada del corpus.
 for r in recetas:
  if "tomate" in r["principales"] and len(r["principales"])>=3:
   nevera=[i for i in r["principales"] if i not in set(r["principales"][:1])]
   if "tomate" in nevera:
    nevera[nevera.index("tomate") if "tomate" in nevera else 0]="tomtae"
   else: nevera.append("tomtae")
   casos.append({"recetaOriginal":r["id"],"nombreEsperado":r["nombre"],"ingredientes":nevera,"quitados":r["principales"][:1],"nota":"ingrediente mal escrito tomtae"})
   break
 (root/"evaluacion"/"listas_prueba.json").write_text(json.dumps(casos,ensure_ascii=False,indent=2),encoding="utf8")
 print(f"Listas creadas: {len(casos)}")
if __name__=="__main__":main()
