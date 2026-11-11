"""Formato único de respuesta de la API: success, data y message."""
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def respuesta(data: Any = None, message: str = "", status_code: int = 200, success: bool = True) -> JSONResponse:
    """Construye la respuesta JSON con la estructura success, data y message."""
    contenido = {"success": success, "data": data, "message": message}
    return JSONResponse(status_code=status_code, content=jsonable_encoder(contenido))


def respuesta_error(message: str, status_code: int, data: Any = None) -> JSONResponse:
    """Construye una respuesta de error con success en false."""
    return respuesta(data=data, message=message, status_code=status_code, success=False)
