"""Repositorio en memoria de consultas posventa."""
from typing import Optional

from repository.datos_iniciales import CONSULTAS_POSVENTA, copia


class ConsultaRepository:
    """Guarda, consulta y actualiza las consultas posventa en la base de datos temporal."""

    def __init__(self):
        self._consultas = copia(CONSULTAS_POSVENTA)

    def buscar_por_id(self, consulta_id: str) -> Optional[dict]:
        return next((c for c in self._consultas if c["consultaId"] == consulta_id), None)

    def actualizar(self, consulta_id: str, cambios: dict) -> dict:
        consulta = self.buscar_por_id(consulta_id)
        consulta.update(cambios)
        return consulta

    def siguiente_consulta_id(self) -> str:
        mayor = max((int(x["consultaId"].split("-")[1]) for x in self._consultas), default=0)
        return f"CON-{mayor + 1:05d}"

    def guardar(self, consulta: dict) -> dict:
        self._consultas.append(consulta)
        return consulta


consulta_repository = ConsultaRepository()
