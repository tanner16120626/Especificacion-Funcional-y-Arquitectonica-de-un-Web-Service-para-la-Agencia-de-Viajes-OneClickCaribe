"""Servicio de cotizaciones: genera la cotización automática con el catálogo y las reglas del dominio."""
from datetime import datetime, timedelta, timezone

from domain.catalogo import Catalogo
from domain.cotizacion import Cotizacion, CotizacionCreate
from domain.errores import ConflictoError, NoEncontradoError
from repository.cliente_repository import ClienteRepository
from repository.cotizacion_repository import CotizacionRepository
from repository.proveedor_repository import ProveedorRepository
from repository.tarifa_repository import TarifaRepository

ZONA_COLOMBIA = timezone(timedelta(hours=-5))


class GenerarCotizacionService:
    """Caso de uso de la solicitud de cotización."""

    def __init__(self, cotizaciones: CotizacionRepository, clientes: ClienteRepository,
                 proveedores: ProveedorRepository, tarifas: TarifaRepository):
        self._cotizaciones = cotizaciones
        self._clientes = clientes
        self._proveedores = proveedores
        self._tarifas = tarifas

    def _ofertas_activas(self, destino: str) -> list:
        """Tarifas del destino cuyo proveedor está activo (RN-13), en orden de servicioId."""
        ofertas = []
        for tarifa in sorted(self._tarifas.buscar_por_destino(destino), key=lambda t: t["servicioId"]):
            proveedor = self._proveedores.buscar_por_id(tarifa["proveedorId"])
            if proveedor is not None and proveedor["estado"] == "activo":
                ofertas.append((tarifa, proveedor))
        return ofertas

    def generar(self, cliente_id: str, datos: CotizacionCreate) -> dict:
        """HU-008: cotiza por pasajero con la tarifa vigente y la comisión pactada (RN-06, RN-22, RN-23, RN-26)."""
        ahora = datetime.now(ZONA_COLOMBIA).replace(microsecond=0)
        Cotizacion.validar_solicitud(datos, ahora.date())
        if self._clientes.buscar_por_id(cliente_id) is None:
            raise NoEncontradoError("El cliente no se encuentra registrado")
        ofertas = self._ofertas_activas(datos.destino)
        if not ofertas:
            raise NoEncontradoError("No hay servicios disponibles para el destino")
        servicios = []
        for tipo in Cotizacion.servicios_solicitados(datos):
            oferta = next(((t, p) for t, p in ofertas if t["tipoServicio"] == tipo), None)
            if oferta is None or not Catalogo.disponible(oferta[0]["sinCupo"], datos.fechaInicio, datos.fechaFin):
                raise ConflictoError("Uno de los servicios no tiene disponibilidad para las fechas solicitadas")
            tarifa, proveedor = oferta
            servicios.append({
                "tipoServicio": tipo,
                "proveedorId": proveedor["proveedorId"],
                "proveedor": proveedor["razonSocial"],
                "tarifaNetaAdulto": tarifa["tarifaNetaAdulto"],
                "tarifaNetaMenor": tarifa["tarifaNetaMenor"],
                "porcentajeComision": Cotizacion.porcentaje_comision(proveedor),
            })
        calculo = Cotizacion.calcular(datos.pasajeros, servicios)
        cotizacion = {
            "cotizacionId": self._cotizaciones.siguiente_cotizacion_id(),
            "clienteId": cliente_id,
            "destino": ofertas[0][0]["destino"],
            "fechaInicio": datos.fechaInicio.isoformat(),
            "fechaFin": datos.fechaFin.isoformat(),
            "pasajeros": [{"nombre": p.nombre.strip(), "edad": p.edad} for p in datos.pasajeros],
            "tipoAcomodacion": datos.tipoAcomodacion.strip() if datos.tipoAcomodacion else None,
            "detalle": calculo["detalle"],
            "cantidadPasajeros": len(datos.pasajeros),
            "valorPorPasajero": calculo["valorPorPasajero"],
            "totalCotizacion": calculo["totalCotizacion"],
            "comisionTotal": calculo["comisionTotal"],
            "fechaEmision": ahora.isoformat(),
            "vigenteHasta": ahora.replace(hour=23, minute=59, second=59).isoformat(),
            "estado": "emitida",
            "respuesta": None,
            "motivo": None,
        }
        self._cotizaciones.guardar(cotizacion)
        return {
            "cotizacionId": cotizacion["cotizacionId"],
            "clienteId": cotizacion["clienteId"],
            "destino": cotizacion["destino"],
            "fechaInicio": cotizacion["fechaInicio"],
            "fechaFin": cotizacion["fechaFin"],
            "cantidadPasajeros": cotizacion["cantidadPasajeros"],
            "pasajeros": calculo["pasajeros"],
            "detalle": [{clave: d[clave] for clave in ("tipoServicio", "proveedor", "tarifaNeta", "porcentajeComision",
                                                       "precioVentaPorPasajero")} for d in calculo["detalle"]],
            "valorPorPasajero": cotizacion["valorPorPasajero"],
            "totalCotizacion": cotizacion["totalCotizacion"],
            "fechaEmision": cotizacion["fechaEmision"],
            "vigenteHasta": cotizacion["vigenteHasta"],
            "estado": cotizacion["estado"],
        }
