# -*- coding: utf-8 -*-
"""Descarga e inspecciona el corpus original con Hugging Face datasets."""
from pathlib import Path
import json
from datasets import load_dataset

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "datos" / "crudo"

def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    ds = load_dataset("somosnlp/RecetasDeLaAbuela", "version_1")
    resumen = {}
    for nombre, split in ds.items():
        resumen[nombre] = {"filas": len(split), "columnas": split.column_names,
                           "ejemplos": split.select(range(min(3, len(split)))).to_list()}
        split.to_csv(str(SALIDA / f"{nombre}.csv") )
    (SALIDA / "inspeccion.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k:{"filas":v["filas"],"columnas":v["columnas"]} for k,v in resumen.items()}, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
