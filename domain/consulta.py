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


class RespuestaConsultaUpdate(BaseModel):
    """Respuesta del asesor a una consulta posventa; con cerrar = true la consulta queda cerrada."""

    respuesta: Optional[str] = None
    asesor: Optional[str] = None
    cerrar: Optional[bool] = None

    model_config = ConfigDict(json_schema_extra={"example": {
        "respuesta": "Su tarifa incluye una maleta de 23 kg y un equipaje de mano.",
        "asesor": "Tanner Cedeño",
        "cerrar": True,
    }})


ESTADOS_RESPONDIBLES = ("abierta", "en_atencion")


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
    def validar_respuesta(datos: RespuestaConsultaUpdate) -> None:
        """La respuesta y el asesor son obligatorios; cerrar indica si la consulta queda resuelta."""
        if _vacio(datos.respuesta):
            raise ErrorNegocio("La respuesta es obligatoria")
        if _vacio(datos.asesor):
            raise ErrorNegocio("El asesor es obligatorio")
        if datos.cerrar is None:
            raise ErrorNegocio("El indicador cerrar es obligatorio")

    @staticmethod
    def validar_respondible(consulta: dict) -> None:
        """Solo se responde una consulta abierta o en atención."""
        if consulta["estado"] not in ESTADOS_RESPONDIBLES:
            raise ErrorNegocio("La consulta ya está cerrada")

    @staticmethod
    def respuesta(datos: RespuestaConsultaUpdate, fecha: str) -> dict:
        """Cambios de la consulta: con cerrar queda cerrada; si no, en atención. No modifica la venta (RN-81)."""
        return {
            "estado": "cerrada" if datos.cerrar else "en_atencion",
            "respuesta": datos.respuesta.strip(),
            "asesor": datos.asesor.strip(),
            "fechaRespuesta": fecha,
        }

    @staticmethod
    def presentar_respuesta(consulta: dict) -> dict:
        """Consulta respondida que devuelve la API."""
        return {
            "consultaId": consulta["consultaId"],
            "estado": consulta["estado"],
            "respuesta": consulta["respuesta"],
            "asesor": consulta["asesor"],
            "fechaRespuesta": consulta["fechaRespuesta"],
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
