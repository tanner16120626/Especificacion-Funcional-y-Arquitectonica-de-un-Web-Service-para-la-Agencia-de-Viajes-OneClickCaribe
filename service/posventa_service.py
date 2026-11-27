"""Servicio de posventa: registra las consultas de los clientes sobre sus órdenes."""
from datetime import datetime, timedelta, timezone

from domain.consulta import Consulta, ConsultaCreate
from domain.errores import NoEncontradoError, PermisoDenegadoError
from repository.consulta_repository import ConsultaRepository
from repository.venta_repository import VentaRepository

ZONA_COLOMBIA = timezone(timedelta(hours=-5))


class RegistrarConsultaService:
    """Caso de uso del registro de una consulta posventa."""

    def __init__(self, ventas: VentaRepository, consultas: ConsultaRepository):
        self._ventas = ventas
        self._consultas = consultas

    def registrar(self, cliente_id: str, datos: ConsultaCreate) -> dict:
        """HU-018: consulta abierta vinculada a una orden del cliente (RN-83, RN-85); no modifica la venta (RN-81)."""
        Consulta.validar_solicitud(datos)
        venta = self._ventas.buscar_por_id(datos.ventaId.strip())
        if venta is None:
            raise NoEncontradoError("La orden de venta no existe")
        if venta["clienteId"] != cliente_id:
            raise PermisoDenegadoError("No tiene permisos para realizar esta acción")
        fecha = datetime.now(ZONA_COLOMBIA).replace(microsecond=0).isoformat()
        consulta = Consulta.nueva(self._consultas.siguiente_consulta_id(), datos, fecha)
        return Consulta.presentar(self._consultas.guardar(consulta))
