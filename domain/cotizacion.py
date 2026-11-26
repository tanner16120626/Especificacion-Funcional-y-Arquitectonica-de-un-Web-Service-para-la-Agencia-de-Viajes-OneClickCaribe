"""Dominio de cotizaciones: esquema de la solicitud, validaciones, cálculo del precio y vigencia."""
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from domain.errores import ErrorNegocio

SERVICIOS_COTIZABLES = ("tiquete_aereo", "hospedaje", "traslado", "asistencia_medica")
RESPUESTAS_COTIZACION = ("aceptada", "rechazada")
EDAD_MAXIMA = 120
EDAD_MAYORIA = 18


class RespuestaCotizacion(BaseModel):
    """Respuesta del cliente a su cotización. El motivo es obligatorio si la rechaza (RN-30)."""

    respuesta: Optional[str] = None
    motivo: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={"example": {"respuesta": "aceptada", "motivo": None}})


class PasajeroCotizacion(BaseModel):
    """Pasajero de la cotización: solo nombre y edad (Ley 1581 de 2012)."""

    nombre: Optional[str] = None
    edad: Optional[int] = None


class CotizacionCreate(BaseModel):
    """Solicitud de cotización del cliente. El cliente se identifica por su token, no por el cuerpo."""

    destino: Optional[str] = None
    fechaInicio: Optional[date] = None
    fechaFin: Optional[date] = None
    pasajeros: Optional[List[PasajeroCotizacion]] = None
    servicios: Optional[List[str]] = None
    tipoAcomodacion: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={"example": {
        "destino": "Cancún",
        "fechaInicio": "2026-12-10",
        "fechaFin": "2026-12-15",
        "pasajeros": [
            {"nombre": "María Fernanda Rojas Díaz", "edad": 32},
            {"nombre": "Andrés Felipe Rojas", "edad": 33},
        ],
        "servicios": ["tiquete_aereo", "hospedaje", "traslado", "asistencia_medica"],
        "tipoAcomodacion": "doble",
    }})


def _vacio(valor: Optional[str]) -> bool:
    return valor is None or not str(valor).strip()


class Cotizacion:
    """Reglas de negocio de la cotización."""

    @staticmethod
    def servicios_solicitados(datos: CotizacionCreate) -> List[str]:
        """Servicios pedidos, sin vacíos ni repetidos, en el orden de la solicitud."""
        servicios = []
        for servicio in datos.servicios or []:
            if not _vacio(servicio) and servicio.strip().lower() not in servicios:
                servicios.append(servicio.strip().lower())
        return servicios

    @staticmethod
    def validar_solicitud(datos: CotizacionCreate, hoy: date) -> None:
        """Valida fechas, pasajeros (RN-07), servicios (RN-10) y acomodación (RN-09)."""
        if _vacio(datos.destino):
            raise ErrorNegocio("El destino es obligatorio")
        if datos.fechaInicio is None or datos.fechaInicio <= hoy:
            raise ErrorNegocio("La fecha de inicio debe ser posterior a hoy")
        if datos.fechaFin is None or datos.fechaFin <= datos.fechaInicio:
            raise ErrorNegocio("La fecha de fin debe ser posterior a la fecha de inicio")
        pasajeros = datos.pasajeros or []
        if not pasajeros:
            raise ErrorNegocio("Debe registrar al menos un pasajero")
        if any(_vacio(p.nombre) for p in pasajeros):
            raise ErrorNegocio("El nombre de cada pasajero es obligatorio")
        if any(p.edad is None for p in pasajeros):
            raise ErrorNegocio("La edad de cada pasajero es obligatoria")
        if any(not 0 <= p.edad <= EDAD_MAXIMA for p in pasajeros):
            raise ErrorNegocio("La edad de cada pasajero debe estar entre 0 y 120")
        servicios = Cotizacion.servicios_solicitados(datos)
        if not servicios:
            raise ErrorNegocio("Debe solicitar al menos un servicio")
        if any(s not in SERVICIOS_COTIZABLES for s in servicios):
            raise ErrorNegocio("Los servicios deben ser tiquete_aereo, hospedaje, traslado o asistencia_medica")
        if "hospedaje" in servicios and _vacio(datos.tipoAcomodacion):
            raise ErrorNegocio("El tipo de acomodación es obligatorio cuando se solicita hospedaje")

    @staticmethod
    def porcentaje_comision(proveedor: dict) -> float:
        """RN-22: las aerolíneas tienen comisión 0; los demás, la comisión pactada (HU-005)."""
        if proveedor.get("tipoProveedor") == "aerolinea":
            return 0
        return proveedor["porcentajeComision"]

    @staticmethod
    def precio_venta(tarifa_neta: int, porcentaje: float) -> int:
        """Tarifa neta más el porcentaje de comisión, en pesos enteros."""
        return round(tarifa_neta * (100 + porcentaje) / 100)

    @staticmethod
    def es_menor(edad: int) -> bool:
        """RN-23: los menores de 18 años usan la tarifa de menor."""
        return edad < EDAD_MAYORIA

    @staticmethod
    def calcular(pasajeros: List[PasajeroCotizacion], servicios: List[dict]) -> dict:
        """Calcula el valor de cada pasajero (RN-06), el valor por pasajero, el total y la comisión.

        valorPorPasajero es el valor de un adulto, o el de un menor si no viaja ningún adulto.

        Cada servicio trae tipoServicio, proveedorId, proveedor, tarifaNetaAdulto, tarifaNetaMenor
        y porcentajeComision.
        """
        detalle = [{
            "tipoServicio": s["tipoServicio"],
            "proveedorId": s["proveedorId"],
            "proveedor": s["proveedor"],
            "tarifaNeta": s["tarifaNetaAdulto"],
            "porcentajeComision": s["porcentajeComision"],
            "precioVentaPorPasajero": Cotizacion.precio_venta(s["tarifaNetaAdulto"], s["porcentajeComision"]),
        } for s in servicios]
        valores, comision_total = [], 0
        for pasajero in pasajeros:
            valor = 0
            for s in servicios:
                tarifa = s["tarifaNetaMenor"] if Cotizacion.es_menor(pasajero.edad) else s["tarifaNetaAdulto"]
                precio = Cotizacion.precio_venta(tarifa, s["porcentajeComision"])
                valor += precio
                comision_total += precio - tarifa
            valores.append({"nombre": pasajero.nombre.strip(), "edad": pasajero.edad, "valor": valor})
        valor_adulto = sum(d["precioVentaPorPasajero"] for d in detalle)
        valor_menor = sum(Cotizacion.precio_venta(s["tarifaNetaMenor"], s["porcentajeComision"]) for s in servicios)
        viaja_adulto = any(not Cotizacion.es_menor(p.edad) for p in pasajeros)
        return {
            "pasajeros": valores,
            "detalle": detalle,
            "valorPorPasajero": valor_adulto if viaja_adulto else valor_menor,
            "totalCotizacion": sum(p["valor"] for p in valores),
            "comisionTotal": comision_total,
        }

    @staticmethod
    def estado_actual(cotizacion: dict, ahora: datetime) -> str:
        """RN-28: una cotización emitida cuya vigencia ya pasó se informa como vencida."""
        if cotizacion["estado"] == "emitida" and ahora > datetime.fromisoformat(cotizacion["vigenteHasta"]):
            return "vencida"
        return cotizacion["estado"]

    @staticmethod
    def presentar(cotizacion: dict) -> dict:
        """Datos de la cotización que devuelve la API, sin los campos internos."""
        return {
            "cotizacionId": cotizacion["cotizacionId"],
            "clienteId": cotizacion["clienteId"],
            "destino": cotizacion["destino"],
            "fechaInicio": cotizacion["fechaInicio"],
            "fechaFin": cotizacion["fechaFin"],
            "cantidadPasajeros": cotizacion["cantidadPasajeros"],
            "pasajeros": [{"nombre": p["nombre"], "edad": p["edad"], "valor": p["valor"]} for p in cotizacion["pasajeros"]],
            "detalle": [{clave: d[clave] for clave in ("tipoServicio", "proveedor", "tarifaNeta", "porcentajeComision",
                                                       "precioVentaPorPasajero")} for d in cotizacion["detalle"]],
            "valorPorPasajero": cotizacion["valorPorPasajero"],
            "totalCotizacion": cotizacion["totalCotizacion"],
            "fechaEmision": cotizacion["fechaEmision"],
            "vigenteHasta": cotizacion["vigenteHasta"],
            "estado": cotizacion["estado"],
        }

    @staticmethod
    def validar_respuesta(datos: RespuestaCotizacion) -> None:
        """La respuesta debe ser aceptada o rechazada; si rechaza, el motivo es obligatorio (RN-30)."""
        if _vacio(datos.respuesta):
            raise ErrorNegocio("La respuesta es obligatoria")
        respuesta = datos.respuesta.strip().lower()
        if respuesta not in RESPUESTAS_COTIZACION:
            raise ErrorNegocio("La respuesta debe ser aceptada o rechazada")
        if respuesta == "rechazada" and _vacio(datos.motivo):
            raise ErrorNegocio("El motivo del rechazo es obligatorio")

    @staticmethod
    def validar_respondible(estado_actual: str) -> None:
        """Solo se responde una cotización emitida y vigente (RN-26, RN-28)."""
        if estado_actual == "vencida":
            raise ErrorNegocio("La cotización está vencida y no puede responderse")
        if estado_actual != "emitida":
            raise ErrorNegocio("La cotización ya fue respondida")
