"""Servicio de ventas: genera la orden de venta y consulta el estado de la compra."""
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone

from domain.errores import ConflictoError, NoEncontradoError, PermisoDenegadoError
from domain.venta import OrdenVentaCreate, Venta
from repository.cotizacion_repository import CotizacionRepository
from repository.factura_repository import FacturaRepository
from repository.reserva_repository import ReservaRepository
from repository.venta_repository import VentaRepository

ZONA_COLOMBIA = timezone(timedelta(hours=-5))


class GenerarOrdenVentaService:
    """Caso de uso de la confirmación de la compra."""

    def __init__(self, ventas: VentaRepository, cotizaciones: CotizacionRepository):
        self._ventas = ventas
        self._cotizaciones = cotizaciones

    def generar(self, cliente_id: str, datos: OrdenVentaCreate) -> dict:
        """HU-011: genera la orden con código propio (RN-32) y los precios de la cotización (RN-31, RN-33, RN-34)."""
        Venta.validar_solicitud(datos)
        cotizacion_id = datos.cotizacionId.strip()
        cotizacion = self._cotizaciones.buscar_por_id(cotizacion_id)
        if cotizacion is None:
            raise NoEncontradoError("La cotización no existe")
        if cotizacion["clienteId"] != cliente_id:
            raise PermisoDenegadoError("No tiene permisos para realizar esta acción")
        existente = self._ventas.buscar_por_cotizacion(cotizacion_id)
        if existente:
            raise ConflictoError("La cotización ya tiene una orden de venta",
                                 {"ventaId": existente["ventaId"], "cotizacionId": existente["cotizacionId"]})
        ahora = datetime.now(ZONA_COLOMBIA).replace(microsecond=0)
        Venta.validar_cotizacion(cotizacion, ahora)
        modalidad = datos.modalidadPago.strip().lower()
        fecha_limite = datos.fechaLimiteSaldo if modalidad == "parcial" else None
        Venta.validar_fecha_limite(fecha_limite, date.fromisoformat(cotizacion["fechaInicio"]))
        venta = {
            "ventaId": self._ventas.siguiente_venta_id(),
            "cotizacionId": cotizacion_id,
            "clienteId": cliente_id,
            "valorTotal": cotizacion["totalCotizacion"],
            "modalidadPago": modalidad,
            "fechaLimiteSaldo": fecha_limite.isoformat() if fecha_limite else None,
            "totalAprobado": 0,
            "saldoPendiente": cotizacion["totalCotizacion"],
            "estado": "pendiente_pago",
            "segmentos": deepcopy(cotizacion["detalle"]),
            "fechaCreacion": ahora.isoformat(),
        }
        return Venta.presentar(self._ventas.guardar(venta))


class ConsultarOrdenService:
    """Caso de uso de la consulta del estado de la compra."""

    def __init__(self, ventas: VentaRepository, reservas: ReservaRepository, facturas: FacturaRepository):
        self._ventas = ventas
        self._reservas = reservas
        self._facturas = facturas

    def consultar(self, cliente_id: str, venta_id: str) -> dict:
        """HU-012: total pagado, saldo, estado y si la reserva y la factura ya fueron generadas (RN-45)."""
        venta = self._ventas.buscar_por_id(venta_id)
        if venta is None:
            raise NoEncontradoError("La orden de venta no existe")
        if venta["clienteId"] != cliente_id:
            raise PermisoDenegadoError("No tiene permisos para realizar esta acción")
        return Venta.presentar_estado(venta, self._reservas.buscar_por_venta(venta_id),
                                      self._facturas.buscar_por_venta(venta_id))
