"""Servicio de pagos: procesa el pago en línea y automatiza la orden pagada."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from domain.errores import ConflictoError, NoEncontradoError, PagoRechazadoError, PermisoDenegadoError
from domain.pago import Pago, PagoCreate
from repository.cliente_repository import ClienteRepository
from repository.cotizacion_repository import CotizacionRepository
from repository.factura_repository import FacturaRepository
from repository.liquidacion_repository import LiquidacionRepository
from repository.pago_repository import PagoRepository
from repository.reserva_repository import ReservaRepository
from repository.tarifa_repository import TarifaRepository
from repository.venta_repository import VentaRepository
from service.pasarela_service import PasarelaPagosSimulada

ZONA_COLOMBIA = timezone(timedelta(hours=-5))


class AutomatizarOrdenPagadaService:
    """Cuando la orden queda pagada: liquida proveedores, confirma la reserva y genera la factura."""

    def __init__(self, liquidaciones: LiquidacionRepository, reservas: ReservaRepository,
                 facturas: FacturaRepository, cotizaciones: CotizacionRepository,
                 tarifas: TarifaRepository, clientes: ClienteRepository):
        self._liquidaciones = liquidaciones
        self._reservas = reservas
        self._facturas = facturas
        self._cotizaciones = cotizaciones
        self._tarifas = tarifas
        self._clientes = clientes

    def ejecutar(self, venta: dict, fecha: str) -> None:
        """RN-48, RN-49 (liquidación neta), RN-61, RN-62 (reserva con localizadores) y RN-53, RN-57 (factura)."""
        cotizacion = self._cotizaciones.buscar_por_id(venta["cotizacionId"]) or {}
        tarifas_menor = {(t["proveedorId"], t["tipoServicio"]): t["tarifaNetaMenor"]
                         for t in self._tarifas.buscar_por_destino(cotizacion.get("destino", ""))}
        self._liquidaciones.guardar_todas(Pago.liquidar(venta, cotizacion.get("pasajeros", []), tarifas_menor))

        reserva_id = self._reservas.siguiente_reserva_id()
        numero_reserva = int(reserva_id.split("-")[1])
        self._reservas.guardar({
            "reservaId": reserva_id,
            "ventaId": venta["ventaId"],
            "estado": "confirmada",
            "fechaConfirmacion": fecha,
            "segmentos": [{"tipoServicio": s["tipoServicio"], "proveedor": s["proveedor"],
                           "localizador": Pago.localizador(s["proveedor"], numero_reserva, posicion)}
                          for posicion, s in enumerate(venta["segmentos"], start=1)],
        })

        cliente = self._clientes.buscar_por_id(venta["clienteId"]) or {}
        factura_id = self._facturas.siguiente_factura_id()
        numero_factura = int(factura_id.split("-")[1])
        self._facturas.guardar({
            "facturaId": factura_id,
            "numeroFactura": f"OCC-{fecha[:4]}-{numero_factura:05d}",
            "cufe": Pago.cufe_simulado(factura_id, venta["ventaId"], fecha),
            "ventaId": venta["ventaId"],
            "documentoCliente": cliente.get("documento"),
            "nombreCliente": cliente.get("nombre"),
            "valorTotal": venta["valorTotal"],
            "fechaEmision": fecha,
            "estado": "emitida",
        })


class ProcesarPagoService:
    """Caso de uso del pago en línea de una orden de venta."""

    def __init__(self, ventas: VentaRepository, pagos: PagoRepository, reservas: ReservaRepository,
                 facturas: FacturaRepository, pasarela: PasarelaPagosSimulada,
                 automatizacion: AutomatizarOrdenPagadaService):
        self._ventas = ventas
        self._pagos = pagos
        self._reservas = reservas
        self._facturas = facturas
        self._pasarela = pasarela
        self._automatizacion = automatizacion

    def _presentar(self, pago: dict) -> dict:
        venta = self._ventas.buscar_por_id(pago["ventaId"])
        return Pago.presentar(pago, venta, self._reservas.buscar_por_venta(venta["ventaId"]),
                              self._facturas.buscar_por_venta(venta["ventaId"]))

    def procesar(self, cliente_id: str, datos: PagoCreate) -> Tuple[str, dict]:
        """HU-013: devuelve el resultado (aprobado, pendiente o repetido) y los datos del pago."""
        Pago.validar_solicitud(datos)
        venta_id = datos.ventaId.strip()
        medio = datos.medioPago.strip().lower()
        clave = datos.claveIdempotencia.strip()
        venta = self._ventas.buscar_por_id(venta_id)
        if venta is None:
            raise NoEncontradoError("La orden de venta no existe")
        if venta["clienteId"] != cliente_id:
            raise PermisoDenegadoError("No tiene permisos para realizar esta acción")

        original: Optional[dict] = self._pagos.buscar_por_clave(clave)
        if original is not None:
            if not Pago.es_mismo_intento(original, venta_id, datos.monto, medio):
                raise ConflictoError("La clave de idempotencia ya se usó en otro intento de pago")
            return "repetido", self._presentar(original)

        Pago.validar_monto(venta, datos.monto, self._pagos.total_pse_pendiente(venta_id))
        transaccion_id = self._pagos.siguiente_transaccion_id()
        estado = self._pasarela.cobrar(medio, datos.datosPago, datos.monto, transaccion_id)
        fecha = datetime.now(ZONA_COLOMBIA).replace(microsecond=0).isoformat()
        pago = self._pagos.guardar({
            "pagoId": self._pagos.siguiente_pago_id(),
            "ventaId": venta_id,
            "transaccionId": transaccion_id,
            "medioPago": medio,
            "monto": datos.monto,
            "estado": estado,
            "claveIdempotencia": clave,
            "fechaPago": fecha,
        })
        if estado == "rechazado":
            raise PagoRechazadoError("La transacción fue rechazada por la entidad financiera", self._presentar(pago))
        if estado == "aprobado":
            total_aprobado, saldo, estado_orden = Pago.aplicar_aprobado(venta, datos.monto)
            venta = self._ventas.actualizar_pago(venta_id, total_aprobado, saldo, estado_orden)
            if estado_orden == "pagada":
                self._automatizacion.ejecutar(venta, fecha)
        return estado, self._presentar(pago)
