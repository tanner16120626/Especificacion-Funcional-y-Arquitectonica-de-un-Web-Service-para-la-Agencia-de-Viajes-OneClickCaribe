"""Repositorio en memoria de cotizaciones."""
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


cotizacion_repository = CotizacionRepository()
