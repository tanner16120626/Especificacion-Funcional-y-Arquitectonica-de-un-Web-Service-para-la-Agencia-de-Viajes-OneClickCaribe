"""Repositorio en memoria de cotizaciones."""
from typing import Optional

from repository.datos_iniciales import COTIZACIONES, copia


class CotizacionRepository:
    """Guarda y consulta cotizaciones en la base de datos temporal."""

    def __init__(self):
        self._cotizaciones = copia(COTIZACIONES)

    def siguiente_cotizacion_id(self) -> str:
        mayor = max((int(c["cotizacionId"].split("-")[1]) for c in self._cotizaciones), default=0)
        return f"COT-{mayor + 1:05d}"

    def guardar(self, cotizacion: dict) -> dict:
        self._cotizaciones.append(cotizacion)
        return cotizacion

    def buscar_por_id(self, cotizacion_id: str) -> Optional[dict]:
        return next((c for c in self._cotizaciones if c["cotizacionId"] == cotizacion_id), None)

    def actualizar_estado(self, cotizacion_id: str, estado: str) -> dict:
        cotizacion = self.buscar_por_id(cotizacion_id)
        cotizacion["estado"] = estado
        return cotizacion

    def registrar_respuesta(self, cotizacion_id: str, respuesta: str, motivo: Optional[str], fecha_respuesta: str) -> dict:
        """Guarda la respuesta del cliente; el estado de la cotización pasa a ser la respuesta."""
        cotizacion = self.buscar_por_id(cotizacion_id)
        cotizacion["respuesta"] = respuesta
        cotizacion["motivo"] = motivo
        cotizacion["estado"] = respuesta
        cotizacion["fechaRespuesta"] = fecha_respuesta
        return cotizacion


cotizacion_repository = CotizacionRepository()
