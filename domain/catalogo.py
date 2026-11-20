"""Dominio del catálogo: reglas de fechas y de disponibilidad de los servicios."""
from datetime import date
from typing import List

from domain.errores import ErrorNegocio


class Catalogo:
    """Reglas de negocio del catálogo de servicios."""

    @staticmethod
    def validar_destino(destino: str) -> None:
        if destino is None or not destino.strip():
            raise ErrorNegocio("El campo 'destino' es obligatorio")

    @staticmethod
    def validar_fechas(fecha_inicio: date, fecha_fin: date) -> None:
        if fecha_fin < fecha_inicio:
            raise ErrorNegocio("La fecha de fin no puede ser anterior a la fecha de inicio")

    @staticmethod
    def disponible(sin_cupo: List[dict], fecha_inicio: date, fecha_fin: date) -> bool:
        """RN-20: el servicio no está disponible si el rango del viaje se cruza con un periodo sin cupo."""
        for periodo in sin_cupo or []:
            desde = date.fromisoformat(periodo["desde"])
            hasta = date.fromisoformat(periodo["hasta"])
            if fecha_inicio <= hasta and fecha_fin >= desde:
                return False
        return True
