"""Dominio de proveedores: esquemas de entrada y reglas de negocio del registro y del cambio de estado."""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from domain.errores import ErrorNegocio

TIPOS_PROVEEDOR = ("aerolinea", "mayorista", "hotel", "aseguradora", "transporte")
ESTADOS_PROVEEDOR = ("activo", "inactivo")


class ProveedorCreate(BaseModel):
    """Datos que envía la administradora para registrar un proveedor. El dominio valida los obligatorios."""

    nit: Optional[str] = None
    razonSocial: Optional[str] = None
    tipoProveedor: Optional[str] = None
    porcentajeComision: Optional[float] = None
    servicios: Optional[List[str]] = None
    destinos: Optional[List[str]] = None

    model_config = ConfigDict(json_schema_extra={"example": {
        "nit": "900123456-7",
        "razonSocial": "Caribe Travel Mayorista S.A.S.",
        "tipoProveedor": "mayorista",
        "porcentajeComision": 12,
        "servicios": ["hospedaje", "traslado"],
        "destinos": ["Cancún", "Ciudad de México"],
    }})


class CambioEstadoProveedor(BaseModel):
    """Nuevo estado del proveedor y motivo del cambio. El dominio valida los obligatorios."""

    estado: Optional[str] = None
    motivo: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={"example": {
        "estado": "inactivo",
        "motivo": "Fin del convenio comercial",
    }})


def _vacio(valor: Optional[str]) -> bool:
    return valor is None or not str(valor).strip()


def _limpiar_lista(valores: Optional[List[str]]) -> List[str]:
    return [v.strip() for v in (valores or []) if not _vacio(v)]


class Proveedor:
    """Reglas de negocio del proveedor."""

    @staticmethod
    def validar_registro(datos: ProveedorCreate) -> None:
        """Valida los obligatorios, el tipo y la comisión pactada (RN-22)."""
        if _vacio(datos.nit):
            raise ErrorNegocio("El NIT es obligatorio")
        if _vacio(datos.razonSocial):
            raise ErrorNegocio("La razón social es obligatoria")
        if _vacio(datos.tipoProveedor):
            raise ErrorNegocio("El tipo de proveedor es obligatorio")
        tipo = datos.tipoProveedor.strip().lower()
        if tipo not in TIPOS_PROVEEDOR:
            raise ErrorNegocio("El tipo de proveedor debe ser aerolinea, mayorista, hotel, aseguradora o transporte")
        if datos.porcentajeComision is None:
            raise ErrorNegocio("La comisión pactada es obligatoria")
        if not 0 <= datos.porcentajeComision <= 100:
            raise ErrorNegocio("La comisión debe estar entre 0 y 100")
        if tipo == "aerolinea" and datos.porcentajeComision != 0:
            raise ErrorNegocio("Las aerolíneas se registran con comisión 0")
        if not _limpiar_lista(datos.servicios):
            raise ErrorNegocio("Debe informar al menos un servicio")
        if not _limpiar_lista(datos.destinos):
            raise ErrorNegocio("Debe informar al menos un destino")

    @staticmethod
    def servicios(datos: ProveedorCreate) -> List[str]:
        return _limpiar_lista(datos.servicios)

    @staticmethod
    def destinos(datos: ProveedorCreate) -> List[str]:
        return _limpiar_lista(datos.destinos)

    @staticmethod
    def validar_cambio_estado(datos: CambioEstadoProveedor) -> None:
        """Valida que el estado sea activo o inactivo y que el motivo esté informado."""
        if _vacio(datos.estado):
            raise ErrorNegocio("El estado es obligatorio")
        if datos.estado.strip().lower() not in ESTADOS_PROVEEDOR:
            raise ErrorNegocio("El estado debe ser activo o inactivo")
        if _vacio(datos.motivo):
            raise ErrorNegocio("El motivo es obligatorio")

    @staticmethod
    def validar_estado_distinto(estado_actual: str, datos: CambioEstadoProveedor) -> None:
        """El nuevo estado debe ser distinto del actual."""
        if datos.estado.strip().lower() == estado_actual:
            raise ErrorNegocio("El proveedor ya se encuentra en ese estado")
