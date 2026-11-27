"""Dominio de posventa: reglas del registro de una consulta del cliente."""
from typing import Optional

from pydantic import BaseModel, ConfigDict

from domain.errores import ErrorNegocio

CATEGORIAS_CONSULTA = ("equipaje", "documentos", "itinerario", "check_in", "servicios_adicionales", "otro")


class ConsultaCreate(BaseModel):
    """Solicitud del cliente para registrar una consulta posventa sobre su orden."""

    ventaId: Optional[str] = None
    categoria: Optional[str] = None
    descripcion: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={"example": {
        "ventaId": "VEN-00010",
        "categoria": "equipaje",
        "descripcion": "¿Puedo llevar una maleta adicional de 23 kg en el vuelo de regreso?",
    }})


def _vacio(valor: Optional[str]) -> bool:
    return valor is None or not str(valor).strip()


class Consulta:
    """Reglas de negocio de la consulta posventa."""

    @staticmethod
    def validar_solicitud(datos: ConsultaCreate) -> None:
        """Valida los campos; solo se aceptan las categorías permitidas, que no modifican la venta (RN-81)."""
        if _vacio(datos.ventaId):
            raise ErrorNegocio("El identificador de la orden es obligatorio")
        if _vacio(datos.categoria):
            raise ErrorNegocio("La categoría es obligatoria")
        if datos.categoria.strip().lower() not in CATEGORIAS_CONSULTA:
            raise ErrorNegocio("La categoría de la consulta no es válida")
        if _vacio(datos.descripcion):
            raise ErrorNegocio("La descripción es obligatoria")

    @staticmethod
    def nueva(consulta_id: str, datos: ConsultaCreate, fecha: str) -> dict:
        """RN-83: la consulta queda vinculada a la orden; RN-85: queda abierta y sin fecha de vencimiento.
        La respuesta, el asesor y la fecha de respuesta quedan vacíos hasta que el asesor responda (HU-019)."""
        return {
            "consultaId": consulta_id,
            "ventaId": datos.ventaId.strip(),
            "categoria": datos.categoria.strip().lower(),
            "descripcion": datos.descripcion.strip(),
            "estado": "abierta",
            "respuesta": None,
            "asesor": None,
            "fechaRegistro": fecha,
            "fechaRespuesta": None,
        }

    @staticmethod
    def presentar(consulta: dict) -> dict:
        """Consulta registrada que devuelve la API."""
        return {
            "consultaId": consulta["consultaId"],
            "ventaId": consulta["ventaId"],
            "categoria": consulta["categoria"],
            "descripcion": consulta["descripcion"],
            "estado": consulta["estado"],
            "fechaRegistro": consulta["fechaRegistro"],
        }
