# -*- coding: utf-8 -*-
"""Clusters de coocurrencia; candidatos requieren aprobación humana."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np,pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import normalize
from app.config import SEMILLA
def main():
 root=Path(__file__).resolve().parents[1]; recetas=pd.read_parquet(root/"datos"/"procesado"/"recetas.parquet"); out=root/"ml"/"resultados"; out.mkdir(exist_ok=True)
 from collections import Counter
 frecuencia=Counter(i for r in recetas.principales for i in set(r)); nombres=sorted(frecuencia,key=lambda n:(-frecuencia[n],n))[:800]; idx={n:i for i,n in enumerate(nombres)}; X=np.zeros((len(nombres),len(nombres)))
 co= {}
 for r in recetas.principales:
  ns=sorted(set(r)&idx.keys())
  for a in ns:
   for b in ns:
    if a!=b: X[idx[a],idx[b]]+=1
 X=normalize(X)
 if len(nombres)<3: raise ValueError("Se requieren al menos tres ingredientes")
 ks=range(2,min(11,len(nombres))); curvas=[]; mejor_k=None; mejor=-1
 for k in ks:
  km=KMeans(n_clusters=k,random_state=SEMILLA,n_init=10).fit(X); sil=silhouette_score(X,km.labels_); curvas.append((k,km.inertia_,sil))
  if sil>mejor: mejor=sil; mejor_k=k; modelo=km
 from collections import Counter
 conteos=Counter()
 for l in recetas.principales:
  ns=set(l)
  for a in ns:
   for b in ns:
    if a<b: conteos[(a,b)]+=1
 seed=__import__("json").loads((root/"datos"/"semilla"/"ingredientes.json").read_text(encoding="utf8")); categoria={n:v.get("categoria") for n,v in seed["ingredientes"].items()}
 pares=[]
 for i,a in enumerate(nombres):
  for b in nombres[i+1:]:
   if categoria.get(a)==categoria.get(b) and modelo.labels_[idx[a]]==modelo.labels_[idx[b]] and conteos[(a,b)]<=max(1,int(len(recetas)*.001)):
    pares.append({"ingrediente_a":a,"ingrediente_b":b,"necesita":a,"sustituto":b,"confianza":round(float(mejor),3),"origen":"inferida","coocurrencias":conteos[(a,b)],"aprobado":""})
 pd.DataFrame(pares[:500]).to_csv(out/"sustitutos_candidatos.csv",index=False)
 df=pd.DataFrame(curvas,columns=["k","inercia","silueta"]); df.to_csv(out/"agrupamiento.csv",index=False)
 df.to_markdown(out/"agrupamiento.md",index=False)
 import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
 plt.plot(df.k,df.inercia,marker="o"); plt.xlabel("k"); plt.ylabel("Inercia"); plt.savefig(out/"codo.png"); plt.close()
 (out/"agrupamiento.md").write_text("# Agrupamiento de ingredientes\n\nCoocurrencia receta-receta normalizada por fila; K-means se compara mediante inercia (codo) y silueta. El k informado maximiza silueta. Los pares candidatos son del mismo clúster y se observan juntos en ≤0,1% de recetas; requieren validación culinaria.\n\n"+df.to_markdown(index=False)+f"\n\nCandidatos exportados: {len(pares[:500])}.\n\n![Método del codo](codo.png)\n",encoding="utf8")
if __name__=="__main__":main()
