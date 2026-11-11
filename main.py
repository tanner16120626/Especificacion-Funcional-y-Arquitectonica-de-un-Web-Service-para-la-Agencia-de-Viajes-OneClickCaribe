"""Punto de entrada de la API REST de One Click Caribe."""
import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_redoc_html
from starlette.exceptions import HTTPException as StarletteHTTPException

from api import (
    auth_router,
    clientes_router,
    cotizaciones_router,
    facturacion_router,
    pagos_router,
    posventa_router,
    proveedores_router,
    reservas_router,
    ventas_router,
)
from api.respuesta import respuesta, respuesta_error

app = FastAPI(
    title=os.getenv("APP_NAME", "Web Service One Click Caribe"),
    version="1.0.0",
    redoc_url=None,
)

MENSAJES_HTTP = {
    "Not Found": "El recurso solicitado no existe",
    "Method Not Allowed": "Método no permitido para este recurso",
}


@app.exception_handler(StarletteHTTPException)
async def manejar_error_http(request: Request, error: StarletteHTTPException):
    """Toda excepción HTTP se responde con success, data y message."""
    detalle = error.detail
    if isinstance(detalle, dict):
        return respuesta_error(detalle.get("message", ""), error.status_code, detalle.get("data"))
    return respuesta_error(MENSAJES_HTTP.get(str(detalle), str(detalle)), error.status_code)


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(request: Request, error: RequestValidationError):
    """Los errores de formato del JSON se responden con código 400 y success, data y message."""
    mensajes = []
    for detalle in error.errors():
        campo = ".".join(str(parte) for parte in detalle.get("loc", ()) if parte not in ("body", "query", "path", "header"))
        tipo = detalle.get("type", "")
        if tipo == "missing":
            mensajes.append(f"El campo '{campo}' es obligatorio")
        elif tipo == "json_invalid":
            mensajes.append("El cuerpo de la solicitud no es un JSON válido")
        else:
            mensajes.append(f"El campo '{campo}' no es válido: {detalle.get('msg', '')}")
    mensaje = "; ".join(mensajes) if mensajes else "Los datos enviados no son válidos"
    return respuesta_error(mensaje, 400)


@app.exception_handler(Exception)
async def manejar_error_interno(request: Request, error: Exception):
    """Cualquier error no controlado se responde con código 500 y success, data y message."""
    return respuesta_error("Ocurrió un error interno en el servidor", 500)


@app.get("/health", tags=["Sistema"])
def health():
    """Verifica que el servicio esté disponible."""
    return respuesta(
        data={"status": "ok", "version": "1.0.0", "environment": os.getenv("APP_ENV", "development")},
        message="Servicio disponible",
    )


@app.get("/redoc", include_in_schema=False)
def redoc():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.1.5/bundles/redoc.standalone.js",
    )


for modulo in (
    auth_router,
    clientes_router,
    proveedores_router,
    cotizaciones_router,
    ventas_router,
    pagos_router,
    reservas_router,
    facturacion_router,
    posventa_router,
):
    app.include_router(modulo.router)
