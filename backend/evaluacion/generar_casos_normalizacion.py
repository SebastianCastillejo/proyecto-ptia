# -*- coding: utf-8 -*-
"""Casos desde términos de ingredientes observados en recetas limpiadas."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import unicodedata
import pandas as pd
def sin_tildes(s):
 return "".join(c for c in unicodedata.normalize("NFD",s) if unicodedata.category(c)!="Mn")
def main():
 root=Path(__file__).resolve().parents[1]; df=pd.read_parquet(root/"datos"/"procesado"/"recetas.parquet"); registros=[]; vistos=set()
 for lista in df.principales:
  for ing in lista:
   for entrada in (ing,ing.upper(),sin_tildes(ing)):
    if entrada not in vistos: registros.append({"entrada":entrada,"esperado":ing,"origen":"término real; variante de caja o tilde"}); vistos.add(entrada)
 if "tomate" in vistos:
  registros += [{"entrada":"tomtae","esperado":"tomate","origen":"transposición de letras"},{"entrada":"jitomate","esperado":"tomate","origen":"sinónimo regional"}]
 especiales=[r for r in registros if r["entrada"] in ("tomtae","jitomate")]
 registros=[r for r in registros if r not in especiales]
 registros=(registros[:max(0,150-len(especiales))]+especiales)[:150]
 if len(registros)<150: raise SystemExit(f"Solo {len(registros)} casos encontrados; se necesitan 150 entradas distintas")
 pd.DataFrame(registros).to_csv(root/"evaluacion"/"casos_normalizacion.csv",index=False)
 print(f"Casos guardados: {len(registros)}")
if __name__=="__main__":main()
