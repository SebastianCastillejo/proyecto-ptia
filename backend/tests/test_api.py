# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient
from app.main import app
from app.api import rutas

client=TestClient(app)
def test_contrato_normalizar():
 r=client.post("/api/ingredientes/normalizar",json={"texto":"jitomate, tomtae"}); assert r.status_code==200
 assert set(r.json())=={"ingredientes"}; assert set(r.json()["ingredientes"][0])=={"entrada","nombre","metodo"}
def test_recomendaciones_422():
 assert client.post("/api/recomendaciones",json={"ingredientes":[]}).status_code==422
 assert client.post("/api/recomendaciones",json={"ingredientes":["arroz"],"limite":11}).status_code==422
def test_recomendaciones_forma(monkeypatch):
 monkeypatch.setattr(rutas,"recomendar",lambda *_a,**_k:[])
 r=client.post("/api/recomendaciones",json={"ingredientes":["arroz"],"limite":5})
 assert r.status_code==200 and r.json()=={"recetas":[]}
def test_campos_opcionales_se_omiten_solo_si_no_estan(monkeypatch):
 base={"id":"arroz","nombre":"Arroz","tiempo_min":10,"imagen_url":None,"cobertura":1,"aprovechamiento":1,"utilidad":1,"usados":1,"total_usuario":1,"faltantes":[],"sustituciones":[],"ingredientes":[{"nombre":"arroz","tipo":"principal","estado":"tiene"}],"explicacion":"Listo."}
 monkeypatch.setattr(rutas,"recomendar",lambda *_a,**_k:[base])
 r=client.post("/api/recomendaciones",json={"ingredientes":["arroz"]}).json()["recetas"][0]
 assert r["imagenUrl"] is None and "sustituto" not in r["ingredientes"][0]
def test_receta_404(monkeypatch):
 monkeypatch.setattr(rutas,"obtener_receta",lambda _id:None)
 r=client.get("/api/recetas/no-existe"); assert r.status_code==404 and r.json()=={"detail":"No encontramos esa receta."}
def test_sugerencias_forma(monkeypatch):
 monkeypatch.setattr(rutas,"sugerencias",lambda _n:["arroz"])
 assert client.get("/api/ingredientes/sugerencias").json()=={"ingredientes":["arroz"]}
def test_detalle_forma(monkeypatch):
 monkeypatch.setattr(rutas,"obtener_receta",lambda _id:{"id":"a","nombre":"A","tiempo_min":10,"porciones":2,"imagen_url":None,"pasos":["P"]})
 assert client.get("/api/recetas/a").json()=={"id":"a","nombre":"A","tiempoMin":10,"porciones":2,"imagenUrl":None,"pasos":["P"]}
def test_error_validacion_cuerpo():
 r=client.post("/api/ingredientes/normalizar",json={})
 assert r.status_code==422 and isinstance(r.json()["detail"],str)
def test_salud_forma(monkeypatch):
 monkeypatch.setattr(rutas,"contar_recetas",lambda:12)
 r=client.get("/api/salud"); assert r.json()["recetas"]==12 and "modeloPuntuacion" in r.json()
