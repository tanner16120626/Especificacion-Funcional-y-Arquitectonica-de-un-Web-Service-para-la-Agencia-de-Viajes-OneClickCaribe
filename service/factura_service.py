"""Servicio de facturación: consulta la factura de la orden."""
from domain.errores import NoEncontradoError, PermisoDenegadoError
from domain.factura import Factura
from repository.factura_repository import FacturaRepository
from repository.venta_repository import VentaRepository


class ConsultarFacturaService:
    """Caso de uso de la consulta de la factura."""

    def __init__(self, ventas: VentaRepository, facturas: FacturaRepository):
        self._ventas = ventas
        self._facturas = facturas

    def consultar(self, cliente_id: str, venta_id: str) -> dict:
        """HU-017: factura de una orden pagada, a nombre del cliente titular (RN-53, RN-57)."""
        venta = self._ventas.buscar_por_id(venta_id)
        if venta is None:
            raise NoEncontradoError("La orden de venta no existe")
        if venta["clienteId"] != cliente_id:
            raise PermisoDenegadoError("No tiene permisos para realizar esta acción")
        factura = self._facturas.buscar_por_venta(venta_id)
        Factura.validar_emitida(venta, factura)
        return Factura.presentar(factura)
