# -*- coding: utf-8 -*-
from app.motor import puntuacion

class Escalador:
 def transform(self,x): return x
class Modelo:
 def predict_proba(self,x):
  import numpy as np
  return np.array([[.2,.8]])
def test_modelos_y_fallback(monkeypatch):
 f={"cobertura":.6,"aprovechamiento":.5,"principales_faltantes":1,"basicos_faltantes":0,"n_sustituciones":1,"confianza_media":.8,"n_ingredientes_receta":5,"n_ingredientes_usuario":3,"fraccion_principales_cubiertos":.7,"tiempo":20,"utilidad_reglas":.45}
 monkeypatch.setattr(puntuacion,"_cargar",lambda _n:{"modelo":Modelo(),"escalador":Escalador()})
 for nombre in ("perceptron","logistica","arbol","red"):
  score,activo=puntuacion.puntuar(f,nombre); assert score==.8 and activo==nombre
 monkeypatch.setattr(puntuacion,"_cargar",lambda _n:None)
 score,activo=puntuacion.puntuar(f,"logistica"); assert score==.45 and activo=="reglas"
