# -*- coding: utf-8 -*-
"""Entrena y compara los cinco rankers con escalado ajustado solo en train."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
import os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score
from app.config import SEMILLA
from app.motor.puntuacion import CARACTERISTICAS
from ml.perceptron import Perceptron

def metricas(y,p,score):
    tn,fp,fn,tp=confusion_matrix(y,p,labels=[0,1]).ravel()
    return {"exactitud":accuracy_score(y,p),"precision":precision_score(y,p,zero_division=0),"exhaustividad":recall_score(y,p,zero_division=0),"especificidad":tn/(tn+fp) if tn+fp else 0,"f1":f1_score(y,p,zero_division=0),"matriz": [[int(tn),int(fp)],[int(fn),int(tp)]]}
def main():
    raiz=Path(__file__).resolve().parents[1]; datos=pd.read_parquet(raiz/"ml"/"dataset_pares.parquet"); out=raiz/"ml"/"resultados"; modelos=raiz/"ml"/"modelos"; out.mkdir(exist_ok=True); modelos.mkdir(exist_ok=True)
    tr=datos[datos.particion=="entrenamiento"]; va=datos[datos.particion=="validacion"]; te=datos[datos.particion=="prueba"]
    if "utilidad_reglas" not in datos:
        datos["utilidad_reglas"]=0.6*datos.cobertura+0.4*datos.aprovechamiento-0.1*datos.principales_faltantes
        datos.to_parquet(raiz/"ml"/"dataset_pares.parquet",index=False)
        tr=datos[datos.particion=="entrenamiento"]; va=datos[datos.particion=="validacion"]; te=datos[datos.particion=="prueba"]
    # Permite cerrar una ejecución interrumpida sin volver a ajustar artefactos ya guardados.
    reutilizar=os.environ.get("REUTILIZAR_MODELOS")=="1" and all((modelos/f"{n}.joblib").exists() for n in ("perceptron","logistica","arbol","red"))
    if reutilizar:
        import joblib
        paquetes_existentes={n:joblib.load(modelos/f"{n}.joblib") for n in ("perceptron","logistica","arbol","red")}
        scaler=paquetes_existentes["logistica"]["escalador"]
        candidatos={n:p["modelo"] for n,p in paquetes_existentes.items()}
    else:
        scaler=StandardScaler().fit(tr[CARACTERISTICAS])
        candidatos={}
    Xtr=scaler.transform(tr[CARACTERISTICAS]); Xva=scaler.transform(va[CARACTERISTICAS]); Xte=scaler.transform(te[CARACTERISTICAS]); ytr=tr.y.to_numpy(); yva=va.y.to_numpy(); yte=te.y.to_numpy()
    if len(set(ytr))<2: raise ValueError("El entrenamiento requiere etiquetas positivas y negativas")
    resultados={}; paquetes={}
    if not reutilizar:
        candidatos={"perceptron":Perceptron(semilla=SEMILLA).fit(Xtr,ytr),"logistica":LogisticRegression(random_state=SEMILLA,max_iter=1000).fit(Xtr,ytr)}
        # Árbol: profundidad seleccionada únicamente en validación.
        arboles=[DecisionTreeClassifier(criterion="entropy",max_depth=d,random_state=SEMILLA).fit(Xtr,ytr) for d in range(3,7)]
        candidatos["arbol"]=max(arboles,key=lambda m:f1_score(yva,m.predict(Xva),zero_division=0))
        redes=[MLPClassifier(hidden_layer_sizes=(h,),activation="relu",solver=s,early_stopping=True,
                             random_state=SEMILLA,max_iter=100,batch_size=512,n_iter_no_change=8).fit(Xtr,ytr)
                for h in (16,32) for s in ("sgd","adam")]
        candidatos["red"]=max(redes,key=lambda m:f1_score(yva,m.predict(Xva),zero_division=0))
    plt.figure(); plt.plot(candidatos["perceptron"].errores_); plt.xlabel("Época"); plt.ylabel("Errores"); plt.title("Convergencia del perceptrón"); plt.savefig(out/"perceptron_errores.png"); plt.close()
    for nombre,m in candidatos.items():
        pred=m.predict(Xte); score=m.predict_proba(Xte)[:,1] if hasattr(m,"predict_proba") else m.predict(Xte).astype(float)
        resultado=metricas(yte,pred,score); ranking=te.assign(_score=score); resultado["precision_at_5"]=float(np.mean([g.sort_values("_score",ascending=False).head(5).y.mean() for _,g in ranking.groupby("nevera_id")])) if len(te) else 0
        resultados[nombre]=resultado; paquetes[nombre]={"modelo":m,"escalador":scaler};
        import joblib
        if not reutilizar: joblib.dump(paquetes[nombre],modelos/f"{nombre}.joblib")
    # Baseline comparado en la misma prueba, el umbral se elige con validación.
    reglas=datos["utilidad_reglas"].to_numpy(); umbrales=np.unique(np.quantile(tr.utilidad_reglas,np.linspace(.1,.9,17))); umbral=max(umbrales,key=lambda u:f1_score(yva,(va.utilidad_reglas>=u).astype(int),zero_division=0))
    pred=(te.utilidad_reglas>=umbral).astype(int); ranking=te.assign(_score=te.utilidad_reglas); resultados["reglas"]={**metricas(yte,pred,te.utilidad_reglas),"precision_at_5":float(np.mean([g.sort_values("_score",ascending=False).head(5).y.mean() for _,g in ranking.groupby("nevera_id")])) if len(te) else 0,"umbral":float(umbral)}
    plt.figure(figsize=(16,9)); plot_tree(candidatos["arbol"],feature_names=CARACTERISTICAS,class_names=["no","sí"],filled=True); plt.savefig(out/"arbol.png",bbox_inches="tight"); plt.close()
    (out/"arbol.txt").write_text(export_text(candidatos["arbol"],feature_names=CARACTERISTICAS),encoding="utf8")
    mlp=candidatos["red"]
    if hasattr(mlp,"loss_curve_"):
        plt.figure(); plt.plot(mlp.loss_curve_); plt.xlabel("Época"); plt.ylabel("Pérdida"); plt.title("Pérdida de la red neuronal"); plt.savefig(out/"red_perdida.png"); plt.close()
    pd.DataFrame([{ "modelo":k,**v} for k,v in resultados.items()]).to_csv(out/"metricas.csv",index=False)
    f1_reglas_validacion=f1_score(yva,(va.utilidad_reglas>=umbral).astype(int),zero_division=0)
    elegido=max(candidatos,key=lambda k:f1_score(yva,candidatos[k].predict(Xva),zero_division=0))
    f1_elegido=f1_score(yva,candidatos[elegido].predict(Xva),zero_division=0)
    coeficientes={f"{k}":float(v) for k,v in zip(CARACTERISTICAS,candidatos["logistica"].coef_[0])}
    importancias={f"{k}":float(v) for k,v in zip(CARACTERISTICAS,candidatos["arbol"].feature_importances_)}
    detalle_modelos=(f"\n## Interpretabilidad\n\nUmbral del baseline de reglas seleccionado en validación: {umbral:.4f}.\n\nÁrbol: profundidad máxima seleccionada en validación={candidatos['arbol'].max_depth}; profundidad efectiva={candidatos['arbol'].get_depth()}.\n\nCoeficientes de regresión logística sobre características estandarizadas (signo positivo aumenta score positivo):\n\n"+"\n".join(f"- {k}: {v:.4f}" for k,v in coeficientes.items())+"\n\nLos pesos manuales comparables del baseline son cobertura=0.6, aprovechamiento=0.4 y faltantes principales=-0.1; los coeficientes no son directamente equivalentes por el escalado y las demás características.\n\nImportancia de variables del árbol por ganancia de impureza/entropía:\n\n"+"\n".join(f"- {k}: {v:.4f}" for k,v in importancias.items())+f"\n\nPerceptrón convergió: {candidatos['perceptron'].convergio_}; épocas: {len(candidatos['perceptron'].errores_)}.\nRed seleccionada: una capa oculta {candidatos['red'].hidden_layer_sizes}, solver={candidatos['red'].solver}; la elección se hizo por F1 en validación.\n")
    (out/"comparacion.md").write_text("# Comparación de modelos\n\nLas etiquetas son supervisión débil generada automáticamente: la receta objetivo y candidatas con ≥70% de principales cubiertos se etiquetan como positivas. El escalador se ajusta solo en entrenamiento. La regresión logística maximiza la verosimilitud (equivale a minimizar log-verosimilitud negativa).\n\nF1 de validación selecciona el modelo de producción: **"+elegido+"**.\n\n| Modelo | Exactitud | Precisión | Exhaustividad | Especificidad | F1 | Precisión@5 |\n|---|---:|---:|---:|---:|---:|---:|\n"+"\n".join(f"| {k} | {v['exactitud']:.3f} | {v['precision']:.3f} | {v['exhaustividad']:.3f} | {v['especificidad']:.3f} | {v['f1']:.3f} | {v['precision_at_5']:.3f} |" for k,v in resultados.items())+"\n\nMatrices de confusión (filas=real [0,1], columnas=predicción [0,1]):\n\n"+"\n".join(f"- {k}: `{v['matriz']}`" for k,v in resultados.items())+detalle_modelos+"\n![Errores del perceptrón](perceptron_errores.png)\n\n![Árbol](arbol.png)\n\n![Pérdida de red](red_perdida.png)\n",encoding="utf8")
    (out/"modelo_elegido.json").write_text(json.dumps({"modelo":elegido,"validacion_f1":f1_elegido,"f1_reglas_validacion":f1_reglas_validacion},indent=2),encoding="utf8")
    print(f"Comparacion lista. Modelo elegido por F1 en validacion: {elegido}")
if __name__=="__main__":main()
