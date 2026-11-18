# -*- coding: utf-8 -*-
"""Evalúa los rankers con etiquetas humanas cuando la columna esté completa."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json, joblib, numpy as np, pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score
from app.motor.puntuacion import CARACTERISTICAS
def main():
 root=Path(__file__).resolve().parents[1]; ruta=root/"evaluacion"/"etiquetas_manuales.csv"; df=pd.read_csv(ruta)
 etiqueta=df["aprovechable_si_no"].astype(str).str.strip().str.lower(); valida=etiqueta.isin(["si","sí","no","1","0"])
 if not valida.any(): print("No hay etiquetas humanas para evaluar todavía."); return
 d=df.loc[valida].copy(); y=d["aprovechable_si_no"].astype(str).str.strip().str.lower().map({"si":1,"sí":1,"1":1,"no":0,"0":0}).to_numpy()
 resultados={}; root_modelos=root/"ml"/"modelos"
 for nombre in ("reglas","perceptron","logistica","arbol","red"):
  if nombre=="reglas":
   metricas=pd.read_csv(root/"ml"/"resultados"/"metricas.csv"); fila=metricas[metricas.modelo=="reglas"]
   umbral=float(fila.iloc[0].get("umbral",.5)) if len(fila) else .5; pred=(d.utilidad_reglas.to_numpy()>=umbral).astype(int)
  else:
   p=root_modelos/f"{nombre}.joblib"
   if not p.exists(): continue
   paquete=joblib.load(p); x=paquete["escalador"].transform(d[CARACTERISTICAS]); m=paquete["modelo"]
   pred=m.predict(x)
  resultados[nombre]={"exactitud":accuracy_score(y,pred),"precision":precision_score(y,pred,zero_division=0),"exhaustividad":recall_score(y,pred,zero_division=0),"F1":f1_score(y,pred,zero_division=0),"matriz_confusion":confusion_matrix(y,pred,labels=[0,1]).tolist()}
 out=root/"evaluacion"/"resultados"; out.mkdir(exist_ok=True); (out/"etiquetas_manuales.json").write_text(json.dumps({"pares_etiquetados":len(d),"resultados":resultados},ensure_ascii=False,indent=2),encoding="utf8")
 print(json.dumps({"pares_etiquetados":len(d),"resultados":resultados},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
