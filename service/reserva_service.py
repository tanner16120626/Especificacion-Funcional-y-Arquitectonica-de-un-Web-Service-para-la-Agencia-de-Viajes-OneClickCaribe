"""Servicio de reservas: consulta la reserva confirmada de la orden."""
from domain.errores import NoEncontradoError, PermisoDenegadoError
from domain.reserva import Reserva
from repository.reserva_repository import ReservaRepository
from repository.venta_repository import VentaRepository


class ConsultarReservaService:
    """Caso de uso de la consulta de la reserva confirmada."""

    def __init__(self, ventas: VentaRepository, reservas: ReservaRepository):
        self._ventas = ventas
        self._reservas = reservas

    def consultar(self, cliente_id: str, venta_id: str) -> dict:
        """HU-016: reserva confirmada de una orden pagada, con un localizador por servicio (RN-61, RN-62)."""
        venta = self._ventas.buscar_por_id(venta_id)
        if venta is None:
            raise NoEncontradoError("La orden de venta no existe")
        if venta["clienteId"] != cliente_id:
            raise PermisoDenegadoError("No tiene permisos para realizar esta acción")
        reserva = self._reservas.buscar_por_venta(venta_id)
        Reserva.validar_confirmada(venta, reserva)
        return Reserva.presentar(reserva)
