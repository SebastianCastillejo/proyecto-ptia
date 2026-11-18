# Backend de Aprovecha

API FastAPI, motor híbrido explicable, conocimiento culinario en SQLite/NetworkX y entrenamiento supervisado clásico. No hay generación de texto ni datos de usuario guardados.

## Instalación y ejecución

Requiere Python 3.11 o superior. Desde la raíz del repo:

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/Activate.ps1
pip install -r backend/requirements.txt
cd backend
python pipeline/descargar_dataset.py
python pipeline/limpiar_dataset.py
python pipeline/construir_base.py
python ml/construir_dataset.py
python ml/entrenar_modelos.py
python ml/tiempo_preparacion.py
python ml/agrupamiento_ingredientes.py
python pipeline/construir_base.py  # incorpora tiempos estimados y sustitutos aprobados
python evaluacion/generar_casos.py
python evaluacion/generar_casos_normalizacion.py
python evaluacion/generar_revision_sustituciones.py
python evaluacion/evaluar.py
python evaluacion/evaluar_etiquetas_manuales.py  # al llenar aprovechable_si_no
python -m uvicorn app.main:app --reload --port 8000
```

En Linux/macOS activa `.venv/bin/activate`. Los datos crudos y la base se generan localmente y no se versionan. Los reportes de evaluación y las etiquetas manuales son artefactos del curso. La regresión de tiempo actualiza el Parquet; reconstruye SQLite después para servir esos tiempos. El agrupamiento deja todos sus candidatos sin aprobar y no los activa hasta que una persona los marque `sí`.

## Arquitectura y trazabilidad

| Componente | Responsabilidad | Relación con el flujo del documento |
|---|---|---|
| `app/motor/normalizador.py` | Limpia entradas, resuelve sinónimos, plurales y errores | Normalización de ingredientes |
| `app/motor/recuperacion.py` | Índice invertido, recuperación de candidatos | Recuperación de recetas |
| `app/motor/caracteristicas.py` | C, A, faltantes, sustituciones y señales del par | Características de utilidad |
| `app/motor/puntuacion.py` | Utilidad de reglas o probabilidad de modelo | Función de utilidad aprendida |
| `app/motor/recomendador.py` | Ranking, estados de ingredientes y explicación | Agente racional híbrido |
| `app/conocimiento/` | SQLite para recetas, NetworkX para relaciones culinarias | Base de conocimiento |
| `pipeline/` | Descarga, normalización de datos y construcción de SQLite | Preparación del corpus |
| `ml/` | Pares con supervisión débil, modelos, tiempo y clústeres | Aprendizaje del curso |
| `evaluacion/` | Listas tomadas de prueba, métricas de API e informe | Evaluación del sistema |

El documento del curso citado como sección 6.d no está incluido en este repositorio; la tabla relaciona los componentes con las etapas del motor descritas en la solicitud.

## Modelo y explicación

`MODELO_PUNTUACION` admite `reglas`, `perceptron`, `logistica`, `arbol` o `red`. La selección entrenada se guarda en `ml/resultados/modelo_elegido.json`; sin ese archivo se utiliza `reglas`. Si el artefacto del modelo activo falta, la API lo registra y conserva el baseline. La puntuación se explica mediante cobertura, aprovechamiento, faltantes y reemplazos visibles.

El conjunto de aprendizaje genera etiquetas débiles desde la receta objetivo y cobertura de ingredientes; no equivale a juicio culinario experto. Las métricas por etiqueta manual y la calidad de sustituciones solo serán conclusivas cuando el equipo llene los CSV de revisión.

## Evaluación

Los comandos de ML escriben resultados y figuras en `ml/resultados/`. `python evaluacion/evaluar.py` usa TestClient y escribe `evaluacion/resultados/reporte.md` y `reporte.json`. Metas que no se cumplen deben permanecer reportadas como tales. `pytest` se ejecuta desde `backend/` con `python -m pytest`.

## Ética y licencia

- Transparencia: cada receta trae utilidad, cobertura y una frase con lo usado y lo faltante; los modelos tabulares se pueden inspeccionar.
- Datos: no hay cuentas, historial ni persistencia de ingredientes enviados por el usuario.
- Supervisión: las sugerencias son opcionales para la persona; sustituciones inferidas y etiquetas requieren revisión humana.
- Integridad: semilla pseudoaleatoria 42, particiones por receta y resultados reproducibles; el informe conserva métricas no alcanzadas.
- Dataset: el corpus declara licencia OpenRAIL. Revisa las condiciones del recurso original antes de redistribuir datos o derivados; se conservan atribución y procedencia.

## Limitaciones conocidas

La extracción actual parte de ingredientes en texto libre y reglas léxicas. El nombre limpio observado no demuestra que sea un concepto culinario canónico; se deben revisar sinónimos y `no_mapeados.csv`. Los tiempos heurísticos se marcan como estimados. La base de demo contiene únicamente las recetas obtenidas al ejecutar el pipeline, nunca el fixture de 11 recetas del frontend.
