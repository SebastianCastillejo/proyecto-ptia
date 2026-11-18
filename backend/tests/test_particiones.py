# -*- coding: utf-8 -*-
import pandas as pd
from pathlib import Path
def test_particiones_no_se_solapan_si_hay_dataset():
 p=Path(__file__).parents[1]/"datos"/"procesado"/"particiones.json"
 if not p.exists(): return
 import json
 d=json.loads(p.read_text(encoding="utf8")); sets=[set(d[k]) for k in ("entrenamiento","validacion","prueba")]
 assert not sets[0]&sets[1] and not sets[0]&sets[2] and not sets[1]&sets[2]
