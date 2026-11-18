# -*- coding: utf-8 -*-
"""Ajusta modelos de minutos usando únicamente recetas con tiempo observado."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import re
import numpy as np, pandas as pd
from sklearn.linear_model import LinearRegression,Ridge
from sklearn.metrics import mean_squared_error,mean_absolute_error,r2_score
from sklearn.model_selection import train_test_split
from app.config import SEMILLA
def vector(r):
 p=" ".join(r["pasos"]); t=p.lower(); return [len(r["pasos"]),len(r["principales"])+len(r["basicos"]),len(p),*[int(w in t) for w in ("horno","remojar","olla a presión","reposar")]]
def main():
 root=Path(__file__).resolve().parents[1]; path=root/"datos"/"procesado"/"recetas.parquet"; df=pd.read_parquet(path); known=df[df.tiempoMin.notna()].copy(); out=root/"ml"/"resultados"; out.mkdir(exist_ok=True); (root/"ml"/"modelos").mkdir(exist_ok=True)
 if len(known)<10:
  msg="Dataset sin suficientes tiempos observados; se usa heurística: 10 min por paso + 5 min por ingrediente principal (mínimo 15)."
  faltan=df.tiempoMin.isna(); df.loc[faltan,"tiempoMin"]=(10*df.loc[faltan,"pasos"].map(len)+5*df.loc[faltan,"principales"].map(len)).clip(lower=15); df.loc[faltan,"tiempoEstimado"]=True; df.to_parquet(path,index=False)
  (out/"tiempo.md").write_text("# Estimación del tiempo\n\n"+msg+f"\n\nTiempos observados disponibles: {len(known)}. MSE, MAE y R² no son estimables sin muestra suficiente.\n",encoding="utf8"); print(msg); return
 X=np.array([vector(r) for r in known.to_dict("records")]); y=known.tiempoMin.astype(float).to_numpy(); tr,te=train_test_split(np.arange(len(y)),test_size=.2,random_state=SEMILLA)
 modelos={"LinearRegression":LinearRegression(),"Ridge":Ridge(alpha=1.0)}; resultados={}
 for n,m in modelos.items():
  m.fit(X[tr],y[tr]); p=m.predict(X[te]); resultados[n]={"MSE":mean_squared_error(y[te],p),"MAE":mean_absolute_error(y[te],p),"R2":r2_score(y[te],p)}
 mejor=min(modelos,key=lambda n:resultados[n]["MAE"]); m=modelos[mejor]; faltan=df.tiempoMin.isna(); df.loc[faltan,"tiempoMin"]=np.maximum(5,m.predict(np.array([vector(r) for r in df.loc[faltan].to_dict("records")]))).round().astype(int); df.loc[faltan,"tiempoEstimado"]=True; df.to_parquet(path,index=False)
 import joblib; joblib.dump(m,root/"ml"/"modelos"/"tiempo.joblib")
 (out/"tiempo.md").write_text("# Regresión de tiempo\n\n| Modelo | MSE | MAE | R² |\n|---|---:|---:|---:|\n"+"\n".join(f"| {n} | {x['MSE']:.3f} | {x['MAE']:.3f} | {x['R2']:.3f} |" for n,x in resultados.items())+f"\n\nModelo elegido por MAE: {mejor}. Se estimaron {int(faltan.sum())} tiempos faltantes.\n",encoding="utf8")
if __name__=="__main__":main()
