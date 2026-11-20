"""Servicio del catálogo: consulta los servicios disponibles por destino y fechas."""
from datetime import date, datetime, timedelta, timezone

from domain.catalogo import Catalogo
from domain.errores import NoEncontradoError
from repository.proveedor_repository import ProveedorRepository
from repository.tarifa_repository import TarifaRepository

ZONA_COLOMBIA = timezone(timedelta(hours=-5))


class ConsultarCatalogoService:
    """Caso de uso de la consulta del catálogo de servicios."""

    def __init__(self, tarifas: TarifaRepository, proveedores: ProveedorRepository):
        self._tarifas = tarifas
        self._proveedores = proveedores

    def consultar(self, destino: str, fecha_inicio: date, fecha_fin: date) -> dict:
        """HU-007: servicios de proveedores activos (RN-13) del destino, con su disponibilidad (RN-20)."""
        Catalogo.validar_destino(destino)
        Catalogo.validar_fechas(fecha_inicio, fecha_fin)
        servicios = []
        destino_registrado = None
        for tarifa in self._tarifas.buscar_por_destino(destino):
            proveedor = self._proveedores.buscar_por_id(tarifa["proveedorId"])
            if proveedor is None or proveedor["estado"] != "activo":
                continue
            destino_registrado = tarifa["destino"]
            servicios.append({
                "servicioId": tarifa["servicioId"],
                "tipoServicio": tarifa["tipoServicio"],
                "proveedor": proveedor["razonSocial"],
                "tarifaNetaAdulto": tarifa["tarifaNetaAdulto"],
                "tarifaNetaMenor": tarifa["tarifaNetaMenor"],
                "disponible": Catalogo.disponible(tarifa["sinCupo"], fecha_inicio, fecha_fin),
            })
        if not servicios:
            raise NoEncontradoError("No hay servicios disponibles para el destino")
        return {
            "destino": destino_registrado,
            "fechaInicio": fecha_inicio.isoformat(),
            "fechaFin": fecha_fin.isoformat(),
            "servicios": servicios,
            "fechaHoraConsulta": datetime.now(ZONA_COLOMBIA).replace(microsecond=0).isoformat(),
        }
