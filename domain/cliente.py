"""Dominio de clientes: esquemas de entrada y salida, y reglas de negocio del registro."""
import re
from typing import Optional

from pydantic import BaseModel, ConfigDict

from domain.errores import ErrorNegocio

TIPOS_CLIENTE = ("individual", "pareja", "grupo_familiar")
VERSION_POLITICA_DATOS = "1.0"
LONGITUD_MINIMA_CONTRASENA = 8


class ClienteCreate(BaseModel):
    """Datos que envía el cliente para registrarse en el portal."""

    documento: Optional[str] = None
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    nacionalidad: Optional[str] = None
    tipoCliente: Optional[str] = None
    contrasena: Optional[str] = None
    aceptaTratamientoDatos: Optional[bool] = None

    model_config = ConfigDict(json_schema_extra={"example": {
        "documento": "1098765432",
        "nombre": "María Fernanda Rojas Díaz",
        "telefono": "+573001234567",
        "correo": "mfrojas@correo.com",
        "nacionalidad": "CO",
        "tipoCliente": "pareja",
        "contrasena": "Cliente2026*",
        "aceptaTratamientoDatos": True,
    }})


class AutorizacionDatos(BaseModel):
    """Registro de la autorización del tratamiento de datos personales (Ley 1581 de 2012)."""

    aceptada: bool
    versionPolitica: str
    fechaAutorizacion: str


class ClienteResponse(BaseModel):
    """Datos del cliente que devuelve la API. Nunca incluye la contraseña."""

    clienteId: str
    documento: str
    nombre: str
    telefono: Optional[str] = None
    correo: Optional[str] = None
    nacionalidad: str
    tipoCliente: str
    autorizacionDatos: AutorizacionDatos
    fechaRegistro: str


def _vacio(valor: Optional[str]) -> bool:
    return valor is None or not str(valor).strip()


class Cliente:
    """Reglas de negocio del cliente."""

    @staticmethod
    def validar_registro(datos: ClienteCreate) -> None:
        """Aplica las reglas RN-01 y RN-04, la contraseña y la autorización de datos."""
        if _vacio(datos.documento):
            raise ErrorNegocio("El documento es obligatorio")
        if _vacio(datos.nombre):
            raise ErrorNegocio("El nombre es obligatorio")
        if _vacio(datos.nacionalidad):
            raise ErrorNegocio("La nacionalidad del cliente es obligatoria")
        if not re.fullmatch(r"[A-Za-z]{2}", datos.nacionalidad.strip()):
            raise ErrorNegocio("La nacionalidad debe ser un código ISO de 2 letras")
        if _vacio(datos.telefono) and _vacio(datos.correo):
            raise ErrorNegocio("Debe informar al menos un dato de contacto: teléfono o correo")
        if _vacio(datos.tipoCliente):
            raise ErrorNegocio("El tipo de cliente es obligatorio")
        tipo = datos.tipoCliente.strip().lower()
        if tipo == "corporativo":
            raise ErrorNegocio("Solo se registran clientes persona natural")
        if tipo not in TIPOS_CLIENTE:
            raise ErrorNegocio("El tipo de cliente debe ser individual, pareja o grupo_familiar")
        if _vacio(datos.contrasena) or len(datos.contrasena) < LONGITUD_MINIMA_CONTRASENA:
            raise ErrorNegocio("La contraseña debe tener mínimo 8 caracteres")
        if datos.aceptaTratamientoDatos is not True:
            raise ErrorNegocio("Debe autorizar el tratamiento de sus datos personales")
