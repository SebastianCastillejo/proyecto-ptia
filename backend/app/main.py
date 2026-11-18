# -*- coding: utf-8 -*-
"""Aplicación FastAPI de "Aprovecha".

Monta todas las rutas bajo /api y activa CORS solo si se define la variable
de entorno CORS_ORIGINS (en desarrollo no hace falta gracias al proxy de Vite).
"""
import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api import rutas
from app.config import ORIGENES_CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aprovecha")

app = FastAPI(title="Aprovecha - API", version="1.0.0")

@app.exception_handler(RequestValidationError)
async def error_validacion(_solicitud: Request, error: RequestValidationError):
    """Mantiene el contrato de error legible {detail: texto} también en 422."""
    errores=error.errors()
    if any(e.get("type")=="missing" for e in errores):
        mensaje="Falta un campo obligatorio en la solicitud."
    else:
        mensaje="La solicitud contiene datos inválidos."
    return JSONResponse(status_code=422,content={"detail":mensaje})

if ORIGENES_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGENES_CORS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(rutas.enrutador, prefix="/api")
