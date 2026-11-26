"""Repositorio en memoria de las tarifas de los servicios del catálogo."""
from typing import List

from repository.datos_iniciales import TARIFAS, copia


def normalizar_destino(destino: str) -> str:
    """Compara destinos sin distinguir mayúsculas ni espacios."""
    return " ".join((destino or "").split()).casefold()


class TarifaRepository:
    """Consulta las tarifas de los servicios en la base de datos temporal."""

    def __init__(self):
        self._tarifas = copia(TARIFAS)

    def buscar_por_destino(self, destino: str) -> List[dict]:
        buscado = normalizar_destino(destino)
        return [t for t in self._tarifas if normalizar_destino(t["destino"]) == buscado]


tarifa_repository = TarifaRepository()
