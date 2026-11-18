# -*- coding: utf-8 -*-
"""Genera pares supervisados desde cada partición; las etiquetas son débiles."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import random
import pandas as pd
from app.config import SEMILLA, ETIQUETA_COBERTURA_POSITIVA
from app.motor.caracteristicas import calcular_caracteristicas
from app.motor.puntuacion import CARACTERISTICAS
from app.motor.recuperacion import construir_indice, ids_recuperables
from app.conocimiento.repositorio import todas_las_recetas
from app.conocimiento.grafo import construir_desde_semilla
def main():
    raiz=Path(__file__).resolve().parents[1]; recetas=todas_las_recetas(); seed=construir_desde_semilla(); sustitutos={}
    for a,b,c,o in seed["sustitutos"]: sustitutos.setdefault(a,[]).append((b,c,o))
    rng=random.Random(SEMILLA); filas=[]
    # La simulación quita ingredientes de la receta objetivo y el resto de la partición es el universo candidato.
    grupos={p:[r for r in recetas if r["particion"]==p] for p in ("entrenamiento","validacion","prueba")}
    indices={p:construir_indice(rs) for p,rs in grupos.items()}
    por_id={p:{r["id"]:r for r in rs} for p,rs in grupos.items()}
    semilla=construir_desde_semilla(); categorias={n:i.get("categoria") for n,i in semilla["ingredientes"].items()}
    extras={p:{} for p in grupos}
    for p,rs in grupos.items():
        for ing in sorted({i for r in rs for i in r["principales"]}): extras[p].setdefault(categorias.get(ing,""),[]).append(ing)
    for objetivo in recetas:
        if len(objetivo["principales"])<2: continue
        candidatos=grupos[objetivo["particion"]]
        quitar=min(len(objetivo["principales"])-1,rng.randint(1,min(3,len(objetivo["principales"])-1)))
        quitados=set(rng.sample(objetivo["principales"],quitar))
        nevera=[i for i in objetivo["principales"] if i not in quitados]
        for _ in range(rng.randint(0,2)):
            categoria=categorias.get(rng.choice(objetivo["principales"]),"")
            bolsa=extras[objetivo["particion"]].get(categoria,[])
            if bolsa:
                extra=rng.choice(bolsa)
                if extra not in nevera and extra not in objetivo["principales"]: nevera.append(extra)
        recuperadas=ids_recuperables(nevera,indices[objetivo["particion"]],sustitutos)
        # Conserva siempre la receta de origen como positivo de la simulación.
        ids_recuperados=set(recuperadas); ids_recuperados.add(objetivo["id"])
        relevantes=[]
        for rid in sorted(ids_recuperados):
            r=por_id[objetivo["particion"]].get(rid)
            if r is None: continue
            f=calcular_caracteristicas(nevera,r,sustitutos,True)
            if f["usados"]>=1 and f["cobertura"]>=.5: relevantes.append((r,f))
        relevantes.sort(key=lambda x:(x[0]["id"]!=objetivo["id"],-x[1]["utilidad_reglas"]))
        positivos=[(r,f) for r,f in relevantes if r["id"]==objetivo["id"] or f["fraccion_principales_cubiertos"]>=ETIQUETA_COBERTURA_POSITIVA]
        negativos=[(r,f) for r,f in relevantes if r["id"]!=objetivo["id"] and f["fraccion_principales_cubiertos"]<ETIQUETA_COBERTURA_POSITIVA][:5]
        seleccion=positivos+negativos
        for r,f in seleccion:
            y=int(r["id"]==objetivo["id"] or f["fraccion_principales_cubiertos"]>=ETIQUETA_COBERTURA_POSITIVA)
            filas.append({"receta_id":r["id"],"nevera_id":objetivo["id"],"particion":r["particion"],"nevera":"|".join(nevera),"y":y,"utilidad_reglas":f["utilidad_reglas"],**{k:f[k] for k in CARACTERISTICAS}})
    out=pd.DataFrame(filas); out.to_parquet(raiz/"ml"/"dataset_pares.parquet",index=False)
    print(out.groupby(["particion","y"]).size().to_string())
    # Muestra de 100 pares para revisión manual, vacía por diseño.
    prueba=out[out.particion=="prueba"].head(100).copy(); prueba["aprovechable_si_no"]=""; prueba.to_csv(raiz/"evaluacion"/"etiquetas_manuales.csv",index=False)
if __name__=="__main__":main()
