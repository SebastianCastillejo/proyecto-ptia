# -*- coding: utf-8 -*-
"""Construye SQLite e índices a partir de recetas.parquet y la semilla."""
from pathlib import Path
import json, sqlite3
import pandas as pd
RAIZ=Path(__file__).resolve().parents[1]; DATOS=RAIZ/"datos"; BD=DATOS/"aprovecha.db"
def main():
    recetas=pd.read_parquet(DATOS/"procesado"/"recetas.parquet").to_dict("records")
    semilla=json.loads((DATOS/"semilla"/"ingredientes.json").read_text(encoding="utf8"))
    if BD.exists(): BD.unlink()
    con=sqlite3.connect(BD); con.executescript("""
    PRAGMA journal_mode=WAL;
    CREATE TABLE recetas(id TEXT PRIMARY KEY,nombre TEXT NOT NULL,tiempo_min INTEGER,tiempo_estimado INTEGER DEFAULT 0,porciones INTEGER,imagen_url TEXT,pasos TEXT,pais TEXT,particion TEXT,origen_url TEXT);
    CREATE TABLE ingredientes(nombre TEXT PRIMARY KEY,categoria TEXT,es_basico INTEGER,frecuencia INTEGER);
    CREATE TABLE receta_ingrediente(receta_id TEXT,ingrediente TEXT,tipo TEXT,cantidad REAL DEFAULT 1,PRIMARY KEY(receta_id,ingrediente),FOREIGN KEY(receta_id) REFERENCES recetas(id));
    CREATE TABLE sinonimos(sinonimo TEXT PRIMARY KEY,canonico TEXT);
    CREATE TABLE sustitutos(necesita TEXT,usar TEXT,confianza REAL,origen TEXT,PRIMARY KEY(necesita,usar));
    CREATE TABLE indice_invertido(ingrediente TEXT,receta_id TEXT,PRIMARY KEY(ingrediente,receta_id));
    CREATE INDEX idx_ri_ingrediente ON receta_ingrediente(ingrediente);
    CREATE INDEX idx_indice_ingrediente ON indice_invertido(ingrediente);
    """)
    con.executemany("INSERT INTO ingredientes VALUES(?,?,?,?)",[(n,i.get("categoria"),int(i.get("es_basico",False)),i.get("frecuencia",0)) for n,i in semilla["ingredientes"].items()])
    con.executemany("INSERT INTO sinonimos VALUES(?,?)",semilla.get("sinonimos",{}).items())
    sustitutos=semilla.get("sustitutos",[])
    candidatos=RAIZ/"ml"/"resultados"/"sustitutos_candidatos.csv"
    if candidatos.exists():
        for row in pd.read_csv(candidatos).fillna("").to_dict("records"):
            if str(row.get("aprobado","")).strip().lower() in {"si","sí","yes","1","true"}:
                sustitutos.append([row["necesita"],row["sustituto"],float(row["confianza"]),"inferida"])
    con.executemany("INSERT OR REPLACE INTO sustitutos VALUES(?,?,?,?)",[tuple(s) for s in sustitutos])
    for r in recetas:
        con.execute("INSERT INTO recetas VALUES(?,?,?,?,?,?,?,?,?,?)",(str(r["id"]),r["nombre"],r.get("tiempoMin"),int(r.get("tiempoEstimado",False)),r.get("porciones",4),r.get("imagenUrl"),json.dumps(list(r["pasos"]),ensure_ascii=False),r.get("pais"),r["particion"],r.get("origen_url")))
        for tipo,lista in (("principal",r["principales"]),("basico",r["basicos"])):
            for ing in lista:
                con.execute("INSERT OR IGNORE INTO receta_ingrediente(receta_id,ingrediente,tipo) VALUES(?,?,?)",(str(r["id"]),ing,tipo))
                if tipo=="principal": con.execute("INSERT OR IGNORE INTO indice_invertido VALUES(?,?)",(ing,str(r["id"])))
    con.commit(); total=con.execute("SELECT COUNT(*) FROM recetas").fetchone()[0]; nis=con.execute("SELECT COUNT(*) FROM ingredientes").fetchone()[0]; con.close()
    (DATOS/"procesado"/"particiones.json").write_text(json.dumps({k:[str(r["id"]) for r in recetas if r["particion"]==k] for k in ("entrenamiento","validacion","prueba")},ensure_ascii=False,indent=2),encoding="utf8")
    print(f"Base creada: {total} recetas, {nis} ingredientes, {BD}")
if __name__=="__main__":main()
