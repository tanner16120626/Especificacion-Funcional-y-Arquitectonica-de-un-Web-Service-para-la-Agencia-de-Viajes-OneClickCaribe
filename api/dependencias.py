"""Dependencias de seguridad para los endpoints que exigen token de acceso."""
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from service.seguridad_service import TokenVencidoError, verificar_token

esquema_bearer = HTTPBearer(auto_error=False)


def obtener_usuario_actual(
    credenciales: Optional[HTTPAuthorizationCredentials] = Depends(esquema_bearer),
) -> dict:
    """Valida el token del encabezado Authorization: Bearer y devuelve sus datos."""
    if credenciales is None or not credenciales.credentials:
        raise HTTPException(status_code=401, detail="Token de acceso inválido o ausente")
    try:
        return verificar_token(credenciales.credentials)
    except TokenVencidoError:
        raise HTTPException(status_code=401, detail="La sesión expiró. Inicie sesión nuevamente")
    except ValueError:
        raise HTTPException(status_code=401, detail="Token de acceso inválido o ausente")


def requiere_rol(*roles: str):
    """Permite el acceso solo a los usuarios autenticados con alguno de los roles indicados."""

    def verificar(usuario: dict = Depends(obtener_usuario_actual)) -> dict:
        if usuario.get("rol") not in roles:
            raise HTTPException(status_code=403, detail="No tiene permisos para realizar esta acción")
        return usuario

    return verificar
