# -*- coding: utf-8 -*-
import json
from pathlib import Path
from app.motor.normalizador import Normalizador
from app.motor.caracteristicas import calcular_caracteristicas
from app.motor.recomendador import recomendar
from app.motor.explicacion import ordenar_recomendaciones
from ml.perceptron import Perceptron

SEED=json.loads((Path(__file__).parents[1]/"datos"/"semilla"/"ingredientes.json").read_text(encoding="utf8"))
VOC={''.join(c for c in __import__('unicodedata').normalize('NFD',n.lower()) if __import__('unicodedata').category(c)!='Mn'):n for n in SEED['ingredientes']}
SIN={k:v for k,v in SEED['sinonimos'].items()}
def test_normalizador_etapas():
 n=Normalizador(VOC,SIN)
 assert n.normalizar("arroz")["metodo"]=="exacto"
 assert n.normalizar("jitomate")["nombre"]=="tomate"
 assert n.normalizar("tomates")["metodo"]=="plural"
 assert n.normalizar("lentejas")["metodo"] in ("exacto","plural")
 assert n.normalizar("tomtae")["nombre"]=="tomate"
 assert n.normalizar("xyzabc")["metodo"]=="desconocido"
def test_caracteristicas_numeros_conocidos():
 r={"principales":["arroz","pollo","tomate"],"basicos":["sal"]}; sus={"pollo":[("pavo",.8,"manual")]}
 f=calcular_caracteristicas(["arroz","pavo"],r,sus,True)
 assert f["cobertura"]==pytest.approx((1+.8+.3)/3.3)
 assert f["aprovechamiento"]==1
 assert f["principales_faltantes"]==1
 assert f["utilidad_reglas"]==pytest.approx(.6*f["cobertura"]+.4-.1)
def test_basicos_activados_y_desactivados():
 r={"principales":["arroz","pollo"],"basicos":["sal"]}
 assert calcular_caracteristicas(["arroz","pollo"],r,{},True)["cobertura"]==1
 assert calcular_caracteristicas(["arroz","pollo"],r,{},False)["cobertura"]==pytest.approx(2/2.3)
def test_umbral_de_cobertura_y_desempate():
 baja={"id":"baja","nombre":"Baja","tiempoMin":10,"principales":["arroz","pollo","tomate","papa","zanahoria"],"basicos":[]}
 assert recomendar(["arroz","pollo"],True,5,recetas=[baja],modo="reglas")==[]
 orden=ordenar_recomendaciones([
  {"id":"lenta","utilidad":.5,"faltantes":["a"],"tiempoMin":30},
  {"id":"menos_completa","utilidad":.5,"faltantes":["a","b"],"tiempoMin":5},
  {"id":"rapida","utilidad":.5,"faltantes":["a"],"tiempoMin":20},
 ])
 assert [x["id"] for x in orden]==["rapida","lenta","menos_completa"]
def test_paridad_orden_mock():
 data=json.loads((Path(__file__).parent/"fixtures"/"mock.json").read_text(encoding="utf8"))
 got=recomendar(["arroz","pollo","jitomate","cebolla de huevo"],True,5,recetas=data["RECETAS"],modo="reglas")
 assert [x["id"] for x in got]==["arroz-con-pollo","huevos-pericos","patacones-hogao","lentejas-arroz","pasta-tomate"]
 assert got[0]["cobertura"]==.682 and got[0]["utilidad"]==.609
def test_perceptron_and_or_y_no_xor():
 import numpy as np
 X=np.array([[0,0],[0,1],[1,0],[1,1]])
 for y in (np.array([0,0,0,1]),np.array([0,1,1,1])):
  p=Perceptron(eta=.1,max_epocas=1000).fit(X,y); assert p.convergio_; assert (p.predict(X)==y).all()
 xor=np.array([0,1,1,0]); p=Perceptron(eta=.1,max_epocas=50).fit(X,xor); assert not p.convergio_

import pytest
