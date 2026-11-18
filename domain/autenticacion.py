"""Dominio de autenticación: esquema de entrada del inicio de sesión y su error de negocio."""
from pydantic import BaseModel, ConfigDict

from domain.errores import ErrorNegocio


class LoginRequest(BaseModel):
    """Credenciales que envía el usuario para iniciar sesión en el portal."""

    correo: str
    contrasena: str

    model_config = ConfigDict(json_schema_extra={"example": {
        "correo": "mfrojas@correo.com",
        "contrasena": "Cliente2026*",
    }})


class CredencialesInvalidasError(ErrorNegocio):
    """El correo no existe o la contraseña no coincide. Se responde con código 401."""

    status_code = 401
