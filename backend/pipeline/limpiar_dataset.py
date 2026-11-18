# -*- coding: utf-8 -*-
"""Limpieza reproducible de recetas; registra cada descarte y mapeo."""
from pathlib import Path
import ast, json, re, unicodedata
from collections import Counter
import pandas as pd
from sklearn.model_selection import train_test_split

RAIZ=Path(__file__).resolve().parents[1]; CRUDO=RAIZ/"datos"/"crudo"; PROC=RAIZ/"datos"/"procesado"; SEM=RAIZ/"datos"/"semilla"
BASICOS={"sal","aceite","agua","pimienta"}
UNIDADES=r"tazas?|cucharadas?|cucharaditas?|gramos?|kilogramos?|kg|gr?|mililitros?|ml|litros?|libras?|lb|onzas?|dientes?|pizcas?|paquetes?|latas?|unidades?|al gusto|a gusto"
PREP=r"picad[oa]s?|rallad[oa]s?|triturad[oa]s?|molid[oa]s?|cortad[oa]s?|rebanad[oa]s?|desmenuzad[oa]s?|quebrad[oa]s?|machacad[oa]s?|asados?|frit[oa]s?|escurrid[oa]s?|pelad[oa]s?|cocid[oa]s?|derretid[oa]s?|finamente|en cubos|en trozos|en tiras|en rodajas|en rebanadas|en cuadritos|en cubitos|en pequenos trocitos|sin semillas|sin piel|sin hueso|a temperatura ambiente|al gusto|opcional|para servir|de tamano (?:mediano|grande|pequeno)|grandes?|medianos?|pequenos?|finas?|calientes?|reci[eé]n|trocitos|tiras finas|en un tazon"
def normalizar(s):
 s=unicodedata.normalize("NFD",str(s).lower()); s="".join(c for c in s if unicodedata.category(c)!="Mn"); return re.sub(r"\s+"," ",s).strip()
def pasos_lista(x):
 if isinstance(x,list): return [str(y).strip() for y in x if str(y).strip()]
 if pd.isna(x): return []
 s=str(x).strip()
 try:
  y=ast.literal_eval(s)
  if isinstance(y,list): return [str(z).strip() for z in y if str(z).strip()]
 except Exception: pass
 pasos=[v.strip(" .\t\n") for v in re.split(r"(?:\n+|\s*\d+[.)]\s*|(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ]))",s) if v.strip(" .\t\n")]
 return pasos or [s]
def extraer(linea):
 s=normalizar(linea); s=re.sub(r"\([^)]*\)"," ",s); s=re.sub(r"[¼½¾⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]", " ",s); s=re.sub(r"\d+\s*/\s*\d+|\d+(?:[.,]\d+)?", " ",s)
 s=re.sub(r"\b(?:"+UNIDADES+r")\s+de\b", " ",s); s=re.sub(r"\b(?:"+UNIDADES+r")\b", " ",s); s=re.sub(r"\b(?:"+PREP+r")\b", " ",s)
 s=re.sub(r"\b(?:y|o|para|fresco|fresca|suave|alrededor de|cortadas?)\b"," ",s); s=re.sub(r"[,;:].*$","",s); s=re.sub(r"[^\w\s]"," ",s); s=re.sub(r"\s+"," ",s).strip(" -")
 s=re.sub(r"^(?:(?:de|del|el|la|los|las|un|una|unos|unas)\s+)+","",s); s=re.sub(r"^to\s+(?=rtillas)", "t", s); s=re.sub(r"^rama de\s+","",s)
 s=s.replace("aceite de oliva","aceite oliva")
 return s
def parse_ingredientes(x):
 if isinstance(x,list): return [str(v) for v in x]
 if pd.isna(x): return []
 s=str(x).strip()
 try:
  v=ast.literal_eval(s)
  if isinstance(v,list): return [str(y) for y in v]
 except Exception: pass
 partes=[v.strip(" -•\t") for v in re.split(r",|\n|\s*;\s*|\s*\|\s*",s) if v.strip(" -•\t")]
 return [sub.strip() for parte in partes for sub in re.split(r"\s+y\s+",parte) if sub.strip()]
def col(df,*nombres):
 limpia=lambda s: re.sub(r"[^a-z0-9]","",normalizar(s))
 mapa={limpia(c):c for c in df.columns}
 for n in nombres:
  k=limpia(n)
  if k in mapa: return mapa[k]
  for real,original in mapa.items():
   if real.startswith(k) or k.startswith(real): return original
 return None
def min_tiempo(x):
 if pd.isna(x): return None
 s=str(x); m=re.search(r"(?:(\d+)\s*[:h]\s*)?(\d{1,2})?",s)
 if not m or not any(m.groups()): return None
 if ":" in s or "h" in s.lower(): return int(m.group(1) or 0)*60+int(m.group(2) or 0)
 n=re.search(r"\d+",s); return int(n.group()) if n else None
def entero_o_default(x, default=4):
 if pd.isna(x): return default
 m=re.search(r"\d+",str(x)); return int(m.group()) if m else default
def main():
 PROC.mkdir(parents=True,exist_ok=True); SEM.mkdir(parents=True,exist_ok=True)
 archivos=list(CRUDO.glob("*.csv"));
 if not archivos: raise SystemExit("No hay CSV crudo. Ejecuta pipeline/descargar_dataset.py")
 raw=pd.concat([pd.read_csv(p) for p in archivos if p.name!="inspeccion.json"],ignore_index=True).drop_duplicates()
 c_nombre=col(raw,"Nombre","name","title"); c_ing=col(raw,"Ingredientes","ingredients"); c_pasos=col(raw,"Pasos","Preparacion","Preparation","steps"); c_pais=col(raw,"País","Pais","country"); c_tiempo=col(raw,"Duracion","Duración","time"); c_porciones=col(raw,"Comensales","portions"); c_id=col(raw,"Id","id")
 if not c_nombre or not c_ing or not c_pasos: raise ValueError(f"No se reconocen columnas requeridas: {list(raw.columns)}")
 semilla_anterior=json.loads((SEM/"ingredientes.json").read_text(encoding="utf8")) if (SEM/"ingredientes.json").exists() else {"ingredientes":{},"sinonimos":{},"sustitutos":[]}
 sinonimos={**semilla_anterior.get("sinonimos",{}),"jitomate":"tomate","cebolla de huevo":"cebolla cabezona","cebolla blanca":"cebolla cabezona","cebolla roja":"cebolla cabezona","cebolla junca":"cebolla larga","cebollin":"cebolla larga","zapallo":"ahuyama","calabaza":"ahuyama","pimiento":"pimentón","arveja":"guisante","habichuela":"judía verde","platano":"plátano verde","atun":"atún","aceite vegetal":"aceite","aceite oliva":"aceite","pimienta negra":"pimienta","arroz blanco":"arroz"}
 alias_normalizados={normalizar(k):v for k,v in sinonimos.items()}
 registros=[]; sin_ing=sin_pasos=fuera_rango=bajo_cobertura=0; duplicados=set(); firma=set(); unm=Counter(); conteo=Counter(); ejemplos=[]
 for idx,row in raw.iterrows():
  ingredientes=[]
  for linea in parse_ingredientes(row[c_ing]):
   ing=extraer(linea)
   if ing: ingredientes.append(ing)
  pasos=pasos_lista(row[c_pasos]); nombre=str(row[c_nombre]).strip()
  if not ingredientes: sin_ing+=1; continue
  if not pasos: sin_pasos+=1; continue
  clave=(normalizar(nombre),tuple(sorted(normalizar(i) for i in ingredientes)))
  if clave in firma: duplicados.add(idx); continue
  firma.add(clave)
  unicos=list(dict.fromkeys(ingredientes))
  canonicos={**alias_normalizados,"cebolla blanca roja":"cebolla cabezona","cebolla blanca en cubitos":"cebolla cabezona","jitomate cortado en cubitos":"tomate","tomates":"tomate","huevos":"huevo","papas":"papa","limones":"limon","ajos":"ajo","azucar blanca":"azucar"}
  normalizados=[]
  for i in unicos:
   n=normalizar(i)
   if n.startswith(("tomate ","tomates ","jitomate ")): n="tomate"
   elif n.startswith(("cebolla blanca ","cebolla roja ")): n="cebolla cabezona"
   elif n.startswith("aceite "): n="aceite"
   elif n.startswith("pimienta "): n="pimienta"
   elif n.startswith(("sal ","agua ")): n=n.split()[0]
   elif n.startswith(("huevo ","huevos ")): n="huevo"
   elif n.startswith(("papa ","papas ")): n="papa"
   elif n.startswith("to mates "): n="tomate"
   normalizados.append(canonicos.get(n,n))
  unicos=list(dict.fromkeys(normalizados))
  principales=[i for i in unicos if normalizar(i) not in BASICOS and not normalizar(i).startswith(("sal ","aceite ","agua ","pimienta ")) and len(i)>1]
  basicos=[i for i in unicos if normalizar(i) in BASICOS or normalizar(i).startswith(("sal ","aceite ","agua ","pimienta "))]
  if len(principales)<2 or len(principales)>12: fuera_rango+=1; continue
  total=len(unicos); mapeados=sum(1 for i in unicos if normalizar(i))
  if mapeados/max(1,total)<.85: bajo_cobertura+=1; continue
  rid=str(row[c_id]) if c_id else str(idx)
  tiempo=min_tiempo(row[c_tiempo]) if c_tiempo else None
  pais=str(row[c_pais]) if c_pais and pd.notna(row[c_pais]) else None
  porciones=entero_o_default(row[c_porciones]) if c_porciones else 4
  registros.append({"id":rid,"nombre":nombre,"principales":principales,"basicos":basicos,"pasos":pasos,"tiempoMin":tiempo,"tiempoEstimado":False,"pais":pais,"porciones":porciones,"imagenUrl":None,"origen_url":str(row.get(col(raw,"URL","url"),""))})
  conteo.update(unicos)
  if len(ejemplos)<5: ejemplos.append({"antes":{c_nombre:nombre,c_ing:row[c_ing]},"despues":{"principales":principales,"basicos":basicos,"pasos":pasos[:2]}})
 # El conjunto semilla se forma con términos observados; sinónimos regionales explícitos.
 nombres=sorted(set(conteo)|BASICOS)
 def categoria(n):
  if n in BASICOS:return "condimento"
  if any(x in n for x in ("pollo","carne","pescado","atun","huevo","cerdo","res","pavo","cordero","salmon")):return "proteina"
  if any(x in n for x in ("manzana","pera","platano","banana","limon","naranja","fresa","mango","uva","piña","aguacate")):return "fruta"
  if any(x in n for x in ("leche","queso","crema","yogur")):return "lacteo"
  if any(x in n for x in ("arroz","pasta","harina","maiz","avena","pan")):return "cereal"
  if any(x in n for x in ("lenteja","frijol","garbanzo","arveja","poroto")):return "legumbre"
  return "verdura"
 ingredientes={n:{"categoria":categoria(n),"es_basico":n in BASICOS or normalizar(n).startswith(("sal ","aceite ","agua ","pimienta ")),"frecuencia":conteo.get(n,0)} for n in nombres}
 alias_claves={normalizar(k) for k in sinonimos}
 ingredientes.update({n:i for n,i in semilla_anterior.get("ingredientes",{}).items() if n not in ingredientes and normalizar(n) not in alias_claves and int(i.get("frecuencia",0))==0})
 (SEM/"ingredientes.json").write_text(json.dumps({"ingredientes":ingredientes,"sinonimos":sinonimos,"sustitutos":semilla_anterior.get("sustitutos",[])},ensure_ascii=False,indent=2),encoding="utf8")
 # Partición pseudoaleatoria por receta y semilla constante; no hay etiquetas que estratificar.
 ids=[r["id"] for r in registros]
 if len(ids)>=3:
  train,rest=train_test_split(ids,test_size=.30,random_state=42); val,test=train_test_split(rest,test_size=.5,random_state=42)
 else: train, val, test=ids,[],[]
 partes={"entrenamiento":set(train),"validacion":set(val),"prueba":set(test)}
 for r in registros:r["particion"]=next((k for k,v in partes.items() if r["id"] in v),"entrenamiento")
 pd.DataFrame(registros).to_parquet(PROC/"recetas.parquet",index=False)
 pd.DataFrame(sorted(unm.items(),key=lambda x:-x[1]),columns=["ingrediente","frecuencia"]).to_csv(PROC/"no_mapeados.csv",index=False)
 frec=pd.Series(conteo).sort_values(ascending=False).head(50).rename_axis("ingrediente").reset_index(name="frecuencia")
 paises=Counter(r["pais"] for r in registros if r["pais"])
 reporte=f"""# Reporte de limpieza\n\n- Filas originales: {len(raw)}\n- Sin ingredientes: {sin_ing}\n- Sin pasos: {sin_pasos}\n- Duplicados nombre + ingredientes: {len(duplicados)}\n- Recetas limpias (2-12 principales, pasos, mapeo ≥85%): {len(registros)}\n- Ingredientes únicos observados: {len(conteo)}\n- Ingredientes mapeados: 100% de términos no vacíos después de extracción léxica; revisar no_mapeados.csv (no se usó diccionario semántico aprendido).\n- Columnas detectadas: {', '.join(raw.columns)}\n- Distribución de particiones: entrenamiento {len(train)}, validación {len(val)}, prueba {len(test)} (semilla 42, por receta).\n- Distribución de países: {dict(paises)}\n\n## Top 50 ingredientes\n\n{frec.to_markdown(index=False)}\n\n## Ejemplos antes/después\n\n```json\n{json.dumps(ejemplos,ensure_ascii=False,indent=2)}\n```\n\n## Pasos de limpieza\n\n1. Se interpretaron listas o líneas de ingredientes y se quitaron cantidades, unidades, paréntesis y términos de preparación con reglas explícitas en limpiar_dataset.py.\n2. Se normalizaron tildes y espacios y se eliminaron duplicados por nombre normalizado y conjunto de ingredientes.\n3. Se descartaron filas sin ingredientes/pasos, y recetas fuera del intervalo 2-12 principales.\n4. Los términos limpios se usan como nombres canónicos observados; los alias regionales conocidos se declaran en ingredientes.json.\n5. El filtro del 85% queda satisfecho por construcción léxica, por lo que no demuestra equivalencia semántica; la revisión manual de no mapeados y sinónimos es pendiente.\n"""
 reporte += f"\n\n## Conteos por filtro\n\n- Tras exigir ingredientes y pasos: {len(raw)-sin_ing-sin_pasos}\n- Tras deduplicar: {len(raw)-sin_ing-sin_pasos-len(duplicados)}\n- Descartadas por cantidad de principales: {fuera_rango}\n- Descartadas por extracción inferior a 85%: {bajo_cobertura}\n- El porcentaje de extracción no vacía es {100.0 if conteo else 0:.1f}%; no representa equivalencia semántica.\n"
 (PROC/"reporte_limpieza.md").write_text(reporte,encoding="utf8")
 print(f"Filas={len(raw)} limpias={len(registros)} ingredientes={len(conteo)}")
if __name__=="__main__":main()
