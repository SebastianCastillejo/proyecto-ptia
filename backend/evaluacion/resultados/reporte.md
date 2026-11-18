# Evaluación del sistema

Listas de prueba derivadas del dataset: 99.


## Métricas: reglas

```json
{
  "precision_at_5": 0.37373737373737376,
  "acierto_primero": 0.7474747474747475,
  "original_top5": 0.9696969696969697,
  "promedio_recetas": 3.7777777777777777,
  "latencia_media_ms": 65.52358787986591,
  "latencia_p95_ms": 64.64582991320638
}
```

## Métricas: modelo elegido

```json
{
  "precision_at_5": 0.37373737373737376,
  "acierto_primero": 0.5454545454545454,
  "original_top5": 0.7878787878787878,
  "promedio_recetas": 3.7777777777777777,
  "latencia_media_ms": 172.96199797948992,
  "latencia_p95_ms": 489.259980013594
}
```

Exactitud de normalización: 1.000 (150 casos). Fallos: 0.

Metas (medidas honestas):

- Precisión@5 ≥0.80: 0.374 — no cumple
- Normalización ≥0.90: 1.000 — cumple
- Latencia p95 <2s: 489.3 ms — cumple
- Sustituciones ≥0.80: pendiente de revisión humana; no hay etiquetas.

## Muestras de casos

### Caso 1: mejillones en salsa chilena

Entrada: `ajo, chorro generoso de aceite oliva, guindilla, harina, media cebolla, arroz alverjitas`

Esperado: `10007` en el top 5.

Obtenido: `2687, 10007, 2777, 2217, 9859`.

Análisis: aprovechable según cobertura de principales: True; original primero: False.

### Caso 2: pan de muerto relleno de nata

Entrada: `azucar, crema batir, harina, huevo, leche tibia, levadura, mantequilla, media crema, sopera de ralladura de naranja, kilos panceta de cerdo`

Esperado: `10165` en el top 5.

Obtenido: `11165, 14486, 14198, 14095, 10933`.

Análisis: aprovechable según cobertura de principales: True; original primero: False.

### Caso 3: vieiras horneadas al cava

Entrada: `botellin de cava, cebolla cabezona, hojas de laurel perejil, huevo, maizena, mantequilla, naranja, plancha de hojaldre congelado, vieiras, hojas laurel`

Esperado: `10063` en el top 5.

Obtenido: `10063, 8553, 8840, 8225, 8830`.

Análisis: aprovechable según cobertura de principales: False; original primero: True.

Sustituciones ofrecidas: `cebolla larga → cebolla cabezona en huevos pericos colombianos con cebolla y tomate`.

Ranking sin sustituciones: `10063, 8840, 8225, 8830, 11848`; con sustituciones: `10063, 8553, 8840, 8225, 8830`. Cambio observado: True.

### Caso 4: como hacer salpicon de jaiba

Entrada: `ajo partidos finamen, cebolla mediana partida, cerveza, cilantro culantro, hojas de laurel, kilo de pulpa de jaiba limpia, perejil, tomtae`

Esperado: `10015` en el top 5.

Obtenido: `10015, 6020, 12016`.

Análisis: aprovechable según cobertura de principales: False; original primero: True.

Normalización esperada: `tomate`; obtenida: `tomate` (correccion).


## Revisión humana pendiente

- Completar etiquetas en `etiquetas_manuales.csv`.
- Validar `sustituciones_revision.csv` y `ml/resultados/sustitutos_candidatos.csv`.
- Precisión@5 por debajo de 0,80: revisar cobertura y los alias del vocabulario, y volver a ajustar el umbral/modelo en validación; conservar intactas las listas de prueba.
- La extracción todavía conserva algunas descripciones compuestas; revisar `no_mapeados.csv` y ejemplos de limpieza antes de afirmar cobertura semántica.
