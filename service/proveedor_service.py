"""Servicio de proveedores: orquesta el registro aplicando las reglas del dominio."""
from datetime import datetime, timedelta, timezone

from domain.errores import ConflictoError
from domain.proveedor import Proveedor, ProveedorCreate
from repository.proveedor_repository import ProveedorRepository

ZONA_COLOMBIA = timezone(timedelta(hours=-5))


def _numero(valor: float):
    """Devuelve la comisión como entero cuando no tiene decimales (12 en lugar de 12.0)."""
    return int(valor) if float(valor).is_integer() else valor


class RegistrarProveedorService:
    """Caso de uso del registro de proveedores."""

    def __init__(self, repositorio: ProveedorRepository):
        self._repositorio = repositorio

    def registrar(self, datos: ProveedorCreate) -> dict:
        """HU-005: registra el proveedor activo con su comisión pactada (RN-13, RN-22)."""
        Proveedor.validar_registro(datos)
        nit = datos.nit.strip()
        existente = self._repositorio.buscar_por_nit(nit)
        if existente:
            raise ConflictoError(
                "El proveedor ya se encuentra registrado",
                {"proveedorId": existente["proveedorId"], "nit": existente["nit"]},
            )
        proveedor = {
            "proveedorId": self._repositorio.siguiente_proveedor_id(),
            "nit": nit,
            "razonSocial": datos.razonSocial.strip(),
            "tipoProveedor": datos.tipoProveedor.strip().lower(),
            "porcentajeComision": _numero(datos.porcentajeComision),
            "servicios": Proveedor.servicios(datos),
            "destinos": Proveedor.destinos(datos),
            "estado": "activo",
            "fechaRegistro": datetime.now(ZONA_COLOMBIA).replace(microsecond=0).isoformat(),
        }
        return dict(self._repositorio.guardar(proveedor))
