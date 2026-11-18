# Aprovecha · Recomendador de recetas por ingredientes disponibles

Proyecto del curso PTIA (Escuela Colombiana de Ingeniería Julio Garavito), Grupo 03:
Sebastian Castillejo y Juan Vera.

El usuario escribe lo que tiene en la cocina y el sistema le recomienda las cinco recetas
que mejor lo aprovechan, con lo que le falta y qué puede sustituir.

## Estructura

```
ptia/
├── frontend/          Interfaz web (React + Vite), basada en el prototipo de interfaz
├── backend/           API FastAPI, motor híbrido, pipeline de datos y modelos
└── docs/
    └── contrato-api.md   Lo que el front espera del back
```

## Correr el front en local

Requisitos: Node.js 18 o superior.

```bash
cd frontend
cp .env.example .env      # en Windows: copy .env.example .env
npm install
npm run dev
```

Abrir http://localhost:5173. Por defecto funciona **sin backend** (`VITE_USE_MOCK=true`),
usando un motor simulado con 11 recetas de ejemplo.

## Conectar con el backend

1. Levantar la API en el puerto 8000 cumpliendo `docs/contrato-api.md`.
2. En `frontend/.env` poner `VITE_USE_MOCK=false`.
3. Reiniciar `npm run dev`. Las llamadas a `/api/...` se redirigen al backend.

Más detalle de la arquitectura del front en `frontend/README.md`.

## Backend, datos y evaluación

Consulta [backend/README.md](backend/README.md) para instalar dependencias, descargar y limpiar RecetasDeLaAbuela, construir SQLite, entrenar y evaluar los modelos. Desde la raíz puedes lanzar ambos servidores con `bash dev.sh` en Linux/macOS o `./dev.ps1` en Windows. Primero prepara `backend/datos/aprovecha.db` siguiendo la guía del backend. Para probar la API sin modo mock, en `frontend/.env` usa `VITE_USE_MOCK=false`; el ejemplo conserva `true` para que el mock siga disponible.

La propuesta usa reglas como respaldo, modelos supervisados interpretables para utilidad, una base SQLite y un grafo de ingredientes. La respuesta explica cada ranking. No persiste las listas enviadas por los usuarios. Los candidatos y etiquetas generados automáticamente se someten a revisión humana, y los reportes conservan metas incumplidas. El dataset declara licencia OpenRAIL; consulta [backend/datos/README.md](backend/datos/README.md) antes de redistribuirlo o sus derivados.
