# Datos del corpus

Fuente principal: [`somosnlp/RecetasDeLaAbuela`](https://huggingface.co/datasets/somosnlp/RecetasDeLaAbuela), configuración `version_1`, archivo `main.csv`. La ficha declara **OpenRAIL** y publica 20.447 registros y 14 atributos. La descarga de esta ejecución contiene **20.236 filas**. Los nombres reales observados son `Id`, `Nombre`, `URL`, `Ingredientes`, `Pasos`, `Pais`, `Duracion`, `Categoria`, `Contexto`, `Valoracion y Votos`, `Comensales`, `Tiempo`, `Dificultad` y `Valor nutricional`.

El script `pipeline/descargar_dataset.py` inspeccionó el dataset mediante `datasets.load_dataset` y dejó el perfil completo en `datos/crudo/inspeccion.json`. Ejemplos observados: `Tacos Dorados de Papa` (MEX, 01:00, vegetarianos), `Ensalada de Chayotes` (MEX, 00:25, vegetarianos) y `Huevos a la Mexicana` (MEX, 00:15, vegetarianos). En las 20.236 filas, los campos tienen este número de valores no vacíos: `Pais` 14.645; `Duracion` 13.606; `Categoria` 13.488; `Tiempo` 10.558; `Comensales` 13.609. Tras limpiar quedaron 18.668 recetas; los campos de tiempo y país se conservan si están disponibles.

## Reproducir

Desde `backend/`: `python pipeline/descargar_dataset.py`, `python pipeline/limpiar_dataset.py` y `python pipeline/construir_base.py`. El CSV y la base quedan fuera de Git. `procesado/reporte_limpieza.md` conserva filtros, distribución y ejemplos. `procesado/no_mapeados.csv` y los alias deben revisarse antes de considerar canónica una cadena extraída de texto libre.

## Transformaciones

La limpieza quita cantidades, medidas, paréntesis y términos frecuentes de preparación; divide ingredientes y pasos; deduplica nombre normalizado + ingredientes; filtra recetas con 2–12 principales, pasos y mapeo mínimo 85%; divide recetas 70/15/15 con semilla 42. La extracción léxica no resuelve por sí sola sinónimos ni ingredientes compuestos, por eso el reporte lo expone como limitación.

## Atribución y uso

La ficha atribuye el corpus a los autores de RecetasDeLaAbuela y declara OpenRAIL. Verifica los términos de la licencia original antes de redistribuir el corpus o derivados y conserva la atribución: [ficha y licencia](https://huggingface.co/datasets/somosnlp/RecetasDeLaAbuela).
