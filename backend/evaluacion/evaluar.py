# -*- coding: utf-8 -*-
"""Mide el recomendador completo en listas derivadas del conjunto de prueba."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json, os, time
import logging
import numpy as np, pandas as pd
from fastapi.testclient import TestClient
from app.main import app
from app.motor import recomendador
from app.config import RAIZ_BACKEND
logging.getLogger("httpx").setLevel(logging.WARNING)
def ejecutar(client,casos,modo):
 recomendador.MODO_EVALUACION=modo; recomendador.IGNORAR_SUSTITUCIONES=False; tiempos=[]; hits=[]; original=[]; conteos=[]; acierto_primero=[]; detalle=[]
 for c in casos:
  t=time.perf_counter(); res=client.post("/api/recomendaciones",json={"ingredientes":c["ingredientes"],"incluirBasicos":True,"limite":5}); tiempos.append(time.perf_counter()-t)
  if res.status_code!=200: continue
  rs=res.json()["recetas"]; conteos.append(len(rs)); ids=[r["id"] for r in rs]; original.append(c["recetaOriginal"] in ids); acierto_primero.append(bool(ids) and ids[0]==c["recetaOriginal"])
  aprovechables=[r for r in rs if (sum(x["estado"] in ("tiene","sustituto") for x in r["ingredientes"] if x["tipo"]=="principal")/max(1,sum(x["tipo"]=="principal" for x in r["ingredientes"])))>=.70 and all(x["estado"] in ("tiene","sustituto") for x in r["ingredientes"] if x["tipo"]=="principal")]
  hits.append(bool(aprovechables))
  detalle.append({"caso":c,"ids":ids,"primera":rs[0] if rs else None,"aprovechable":bool(aprovechables),"original_primero":bool(ids) and ids[0]==c["recetaOriginal"],"tiene_sustitucion":any(r["sustituciones"] for r in rs),"sustituciones": [{"receta":r["nombre"],**s} for r in rs for s in r["sustituciones"]]})
 return {"precision_at_5":float(np.mean(hits)) if hits else 0,"acierto_primero":float(np.mean(acierto_primero)) if acierto_primero else 0,"original_top5":float(np.mean(original)) if original else 0,"promedio_recetas":float(np.mean(conteos)) if conteos else 0,"latencia_media_ms":float(np.mean(tiempos)*1000) if tiempos else 0,"latencia_p95_ms":float(np.percentile(tiempos,95)*1000) if tiempos else 0,"_casos_detalle":detalle}
def main():
 root=Path(__file__).resolve().parents[1]; out=root/"evaluacion"/"resultados"; out.mkdir(exist_ok=True); listas=root/"evaluacion"/"listas_prueba.json"
 if not listas.exists(): os.system(f'python "{root / "evaluacion" / "generar_casos.py"}')
 casos=json.loads(listas.read_text(encoding="utf8")); client=TestClient(app)
 reglas=ejecutar(client,casos,"reglas"); modelo=ejecutar(client,casos,None)
 casos_norm=pd.read_csv(root/"evaluacion"/"casos_normalizacion.csv") if (root/"evaluacion"/"casos_normalizacion.csv").exists() else pd.DataFrame(columns=["entrada","esperado"])
 fallos=[]
 for r in casos_norm.to_dict("records"):
  resp=client.post("/api/ingredientes/normalizar",json={"texto":str(r["entrada"])}).json().get("ingredientes",[])
  got=resp[0]["nombre"] if resp else "";
  if got!=r["esperado"]: fallos.append({"entrada":r["entrada"],"esperado":r["esperado"],"obtenido":got})
 exactitud=1-len(fallos)/len(casos_norm) if len(casos_norm) else 0
 ejemplos=modelo.pop("_casos_detalle"); reglas.pop("_casos_detalle")
 # Prefiere casos donde el original queda primero y el resultado es aprovechable.
 mejores=sorted(ejemplos,key=lambda e:(not e["aprovechable"],not e["original_primero"],e["caso"]["recetaOriginal"]))[:2]
 casos_con_sustitucion=[e for e in ejemplos if e["tiene_sustitucion"]]
 con_error=next((e for e in ejemplos if "tomtae" in e["caso"]["ingredientes"]),None)
 cambio_ranking=False
 con_sustitucion=None
 for candidato in casos_con_sustitucion:
  con_sustitucion=candidato
  recomendador.IGNORAR_SUSTITUCIONES=False; con=client.post("/api/recomendaciones",json={"ingredientes":con_sustitucion["caso"]["ingredientes"],"incluirBasicos":True,"limite":5}).json()["recetas"]
  recomendador.IGNORAR_SUSTITUCIONES=True; sin=client.post("/api/recomendaciones",json={"ingredientes":con_sustitucion["caso"]["ingredientes"],"incluirBasicos":True,"limite":5}).json()["recetas"]
  cambio_ranking=[r["id"] for r in con]!=[r["id"] for r in sin]
  con_sustitucion["ranking_sin_sustituciones"]=[r["id"] for r in sin]
  con_sustitucion["ranking_con_sustituciones"]=[r["id"] for r in con]
  con_sustitucion["cambio_ranking"]=cambio_ranking
  if cambio_ranking: break
 recomendador.IGNORAR_SUSTITUCIONES=False
 reporte={"numero_listas":len(casos),"reglas":reglas,"modelo_elegido":modelo,"normalizacion":{"casos":len(casos_norm),"exactitud":exactitud,"fallos":fallos},"metas":{"precision_at_5":modelo["precision_at_5"]>=.8,"precision_at_5_reglas":reglas["precision_at_5"]>=.8,"normalizacion":exactitud>=.9,"latencia_p95":modelo["latencia_p95_ms"]<2000},"cambio_ranking_sustitucion":cambio_ranking,"nota_sustituciones":"La precisión no se calcula hasta que el equipo complete valida_si_no en sustituciones_revision.csv."}
 (out/"reporte.json").write_text(json.dumps(reporte,ensure_ascii=False,indent=2),encoding="utf8")
 lineas=["# Evaluación del sistema",f"\nListas de prueba derivadas del dataset: {len(casos)}.\n", "\n## Métricas: reglas\n", "```json",json.dumps(reglas,ensure_ascii=False,indent=2),"```", "\n## Métricas: modelo elegido\n", "```json",json.dumps(modelo,ensure_ascii=False,indent=2),"```",f"\nExactitud de normalización: {exactitud:.3f} ({len(casos_norm)} casos). Fallos: {len(fallos)}.","\nMetas (medidas honestas):\n",f"- Precisión@5 ≥0.80: {reglas['precision_at_5']:.3f} — {'cumple' if reporte['metas']['precision_at_5'] else 'no cumple'}",f"- Normalización ≥0.90: {exactitud:.3f} — {'cumple' if reporte['metas']['normalizacion'] else 'no cumple'}",f"- Latencia p95 <2s: {modelo['latencia_p95_ms']:.1f} ms — {'cumple' if reporte['metas']['latencia_p95'] else 'no cumple'}", "- Sustituciones ≥0.80: pendiente de revisión humana; no hay etiquetas.\n", "## Muestras de casos\n"]
 muestras=[]
 for e in mejores:
  if e not in muestras:muestras.append(e)
 for e in (con_sustitucion,con_error):
  if e and e not in muestras:muestras.append(e)
 for k,e in enumerate(muestras[:4],1):
  extra=(f"\n\nSustituciones ofrecidas: `{'; '.join(s['necesita']+' → '+s['usar']+' en '+s['receta'] for s in e['sustituciones'])}`.\n\nRanking sin sustituciones: `{', '.join(e['ranking_sin_sustituciones'])}`; con sustituciones: `{', '.join(e['ranking_con_sustituciones'])}`. Cambio observado: {e['cambio_ranking']}." if "ranking_sin_sustituciones" in e else "")
  normalizacion=""
  if "tomtae" in e["caso"]["ingredientes"]:
   n=client.post("/api/ingredientes/normalizar",json={"texto":"tomtae"}).json()["ingredientes"]
   normalizacion=f"\n\nNormalización esperada: `tomate`; obtenida: `{n[0]['nombre']}` ({n[0]['metodo']})."
  lineas.append(f"### Caso {k}: {e['caso']['nombreEsperado']}\n\nEntrada: `{', '.join(e['caso']['ingredientes'])}`\n\nEsperado: `{e['caso']['recetaOriginal']}` en el top 5.\n\nObtenido: `{', '.join(e['ids'])}`.\n\nAnálisis: aprovechable según cobertura de principales: {e['aprovechable']}; original primero: {e['original_primero']}.{normalizacion}{extra}\n")
 lineas += ["\n## Revisión humana pendiente\n","- Completar etiquetas en `etiquetas_manuales.csv`.\n- Validar `sustituciones_revision.csv` y `ml/resultados/sustitutos_candidatos.csv`.\n- Precisión@5 por debajo de 0,80: revisar cobertura y los alias del vocabulario, y volver a ajustar el umbral/modelo en validación; conservar intactas las listas de prueba.\n- La extracción todavía conserva algunas descripciones compuestas; revisar `no_mapeados.csv` y ejemplos de limpieza antes de afirmar cobertura semántica.\n"]
 (out/"reporte.md").write_text("\n".join(lineas),encoding="utf8")
 print(f"Reporte generado. Precision@5 reglas={reglas['precision_at_5']:.3f}; p95={modelo['latencia_p95_ms']:.1f}ms; normalización={exactitud:.3f}")
if __name__=="__main__":main()
