"""Dominio de cotizaciones: esquema de la solicitud, validaciones y cálculo del precio de venta."""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from domain.errores import ErrorNegocio

SERVICIOS_COTIZABLES = ("tiquete_aereo", "hospedaje", "traslado", "asistencia_medica")
EDAD_MAXIMA = 120
EDAD_MAYORIA = 18


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
