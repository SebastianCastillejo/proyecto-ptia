# Aprovecha: temas del proyecto y guía de uso

## ¿Qué es Aprovecha?

Aprovecha es una aplicación web que recomienda recetas a partir de los ingredientes que la persona tiene disponibles. También muestra qué ingredientes puede usar, cuáles le faltan y, cuando hay una opción aprobada, qué ingrediente podría sustituir.

## Temas y tecnologías utilizados

| Tema | Uso en el proyecto |
|---|---|
| Agentes racionales y función de utilidad | El sistema busca ordenar recetas según qué tan bien aprovechan los ingredientes disponibles y explica el resultado. |
| Representación del conocimiento | Las recetas y sus ingredientes se guardan en SQLite; las relaciones entre ingredientes se representan con un grafo. |
| Normalización de texto | Limpia nombres de ingredientes y reconoce variantes, sinónimos, plurales y algunos errores de escritura. |
| Recuperación de información | Busca recetas candidatas mediante los ingredientes ingresados. |
| Ingeniería de características | Calcula cobertura, ingredientes faltantes, coincidencias y señales para estimar la utilidad de cada receta. |
| Aprendizaje supervisado | Compara perceptrón, regresión logística, árbol de decisión y red neuronal con etiquetas débiles derivadas de recetas. |
| Sistemas basados en reglas | Sirven como baseline y alternativa si el modelo aprendido no está disponible. |
| Agrupamiento y sustituciones | Propone candidatos de sustitución mediante coocurrencia y agrupamiento; requieren aprobación humana antes de activarse. |
| Evaluación de sistemas | Mide precisión, recuperación, F1, Precisión@5 y latencia, y conserva también las metas que no se alcanzan. |
| Desarrollo web cliente-servidor | Interfaz en React y Vite; API en FastAPI. La interfaz puede usar datos simulados o conectarse al backend. |
| Ética y trazabilidad | Se informa la procedencia del dataset, los límites de las etiquetas automáticas y que las listas enviadas no se guardan como historial. |

## ¿Cómo se ve y cómo se usa?

La aplicación tiene tres pantallas principales:

1. **Inicio:** presenta el buscador de ingredientes. La persona escribe un ingrediente y puede elegir una sugerencia; los ingredientes seleccionados aparecen como etiquetas que se pueden quitar. También puede activar el interruptor de despensa para indicar que cuenta con básicos de cocina. Al continuar, solicita recomendaciones.
2. **Resultados:** muestra las recetas recomendadas en tarjetas. Cada tarjeta resume la receta, su aprovechamiento y los ingredientes disponibles o faltantes. Se puede abrir una receta para ver el detalle.
3. **Detalle de receta:** presenta información de la receta, ingredientes, pasos de preparación y la explicación de por qué fue recomendada. Si existen sustituciones aprobadas, se muestran como sugerencias.

El orden de resultados depende de los ingredientes ingresados y del modelo o reglas activos. Las recomendaciones son orientativas: una sustitución sugerida no garantiza equivalencia culinaria.

## Cómo ejecutar en Windows

Se necesitan Node.js y Python instalados. Abre **dos ventanas de PowerShell** y déjalas abiertas mientras usas la aplicación.

### 1. Backend

En la primera ventana:

```powershell
cd C:\Users\Usuario\Desktop\ptia\backend
```

Si ya existe el entorno virtual, actívalo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Luego inicia el servidor:

```powershell
uvicorn app.main:app --reload
```

La documentación interactiva de la API estará en <http://localhost:8000/docs>.

Si todavía no existe `.venv`, créalo e instala dependencias antes de activarlo:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

La base de datos debe estar preparada según [la guía del backend](../backend/README.md). Si al iniciar aparece un error indicando que no existe la base, sigue allí los pasos de descarga, limpieza y construcción de datos.

### 2. Frontend

En la segunda ventana:

```powershell
cd C:\Users\Usuario\Desktop\ptia\frontend
npm install
npm run dev
```

Abre <http://localhost:5173>. Para usar el backend, el archivo `frontend/.env` debe tener:

```env
VITE_USE_MOCK=false
VITE_BACKEND_URL=http://localhost:8000
```

Después de cambiar `.env`, reinicia Vite con `Ctrl+C` y ejecuta `npm run dev` otra vez. Si `VITE_USE_MOCK=true`, el frontend usa recetas simuladas y no necesita el backend.

## Evaluación y límites conocidos

La evaluación automatizada actual reportó F1 de validación de 0,957 para el árbol seleccionado. En las listas finales, Precisión@5 fue 0,374, por debajo de la meta de 0,80. La normalización alcanzó 1,000 en 150 casos generados automáticamente; esos casos no son una validación humana independiente. La latencia p95 medida fue 489 ms.

El corpus contiene nombres de ingredientes extraídos de texto libre y algunos pueden ser frases incompletas o términos que necesitan revisión. Los candidatos de sustitución y las etiquetas débiles no se deben presentar como validados por expertos hasta que se revisen manualmente. Los informes detallados están en `backend/evaluacion/resultados/` y `backend/ml/resultados/`.

## Estructura del repositorio

- `frontend/`: interfaz React, sus páginas y componentes.
- `backend/app/`: API y motor de recomendación.
- `backend/pipeline/`: descarga y preparación de datos.
- `backend/ml/`: construcción de ejemplos y entrenamiento de modelos.
- `backend/evaluacion/`: casos, métricas e informes.
- `docs/`: guías y contrato de comunicación entre frontend y backend.
