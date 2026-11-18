# -*- coding: utf-8 -*-
"""Calcula acuerdo humano de sustituciones únicamente con etiquetas completas."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
def main():
 p=Path(__file__).resolve().parent/"sustituciones_revision.csv"
 if not p.exists(): print("Pendiente: completar valida_si_no en sustituciones_revision.csv"); return
 df=pd.read_csv(p); x=df.valida_si_no.astype(str).str.strip().str.lower(); x=x[x.isin(["si","sí","no"])]
 if not len(x): print("No hay etiquetas humanas todavía."); return
 print(f"Acuerdo positivo: {(x.isin(['si','sí'])).mean():.3f} ({len(x)} etiquetas)")
if __name__=="__main__":main()
