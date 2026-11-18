# Comparación de modelos

Las etiquetas son supervisión débil generada automáticamente: la receta objetivo y candidatas con ≥70% de principales cubiertos se etiquetan como positivas. El escalador se ajusta solo en entrenamiento. La regresión logística maximiza la verosimilitud (equivale a minimizar log-verosimilitud negativa).

F1 de validación selecciona el modelo de producción: **arbol**.

| Modelo | Exactitud | Precisión | Exhaustividad | Especificidad | F1 | Precisión@5 |
|---|---:|---:|---:|---:|---:|---:|
| perceptron | 0.907 | 0.916 | 0.864 | 0.940 | 0.889 | 0.710 |
| logistica | 0.933 | 0.946 | 0.896 | 0.961 | 0.920 | 0.710 |
| arbol | 0.963 | 0.964 | 0.949 | 0.973 | 0.957 | 0.710 |
| red | 0.962 | 0.966 | 0.946 | 0.975 | 0.956 | 0.710 |
| reglas | 0.859 | 0.871 | 0.791 | 0.911 | 0.829 | 0.710 |

Matrices de confusión (filas=real [0,1], columnas=predicción [0,1]):

- perceptron: `[[3438, 219], [377, 2392]]`
- logistica: `[[3515, 142], [289, 2480]]`
- arbol: `[[3560, 97], [140, 2629]]`
- red: `[[3566, 91], [150, 2619]]`
- reglas: `[[3332, 325], [578, 2191]]`
## Interpretabilidad

Umbral del baseline de reglas seleccionado en validación: 0.4600.

Árbol: profundidad máxima seleccionada en validación=6; profundidad efectiva=6.

Coeficientes de regresión logística sobre características estandarizadas (signo positivo aumenta score positivo):

- cobertura: -2.4016
- aprovechamiento: 2.5999
- principales_faltantes: 0.7292
- basicos_faltantes: 0.0000
- n_sustituciones: -0.8334
- confianza_media: 0.6947
- n_ingredientes_receta: 0.2254
- n_ingredientes_usuario: 0.5602
- fraccion_principales_cubiertos: 5.7100
- tiempo: -0.0075

Los pesos manuales comparables del baseline son cobertura=0.6, aprovechamiento=0.4 y faltantes principales=-0.1; los coeficientes no son directamente equivalentes por el escalado y las demás características.

Importancia de variables del árbol por ganancia de impureza/entropía:

- cobertura: 0.0003
- aprovechamiento: 0.2588
- principales_faltantes: 0.0074
- basicos_faltantes: 0.0000
- n_sustituciones: 0.0000
- confianza_media: 0.0000
- n_ingredientes_receta: 0.0027
- n_ingredientes_usuario: 0.0940
- fraccion_principales_cubiertos: 0.6365
- tiempo: 0.0002

Perceptrón convergió: False; épocas: 1000.
Red seleccionada: una capa oculta (16,), solver=adam; la elección se hizo por F1 en validación.

![Errores del perceptrón](perceptron_errores.png)

![Árbol](arbol.png)

![Pérdida de red](red_perdida.png)
