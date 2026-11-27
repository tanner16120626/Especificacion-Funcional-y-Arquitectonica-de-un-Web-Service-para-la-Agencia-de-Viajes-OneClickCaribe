"""Repositorio en memoria de consultas posventa."""
from repository.datos_iniciales import CONSULTAS_POSVENTA, copia


class ConsultaRepository:
    """Guarda las consultas posventa en la base de datos temporal."""

    def __init__(self):
        self._consultas = copia(CONSULTAS_POSVENTA)

    def siguiente_consulta_id(self) -> str:
        mayor = max((int(x["consultaId"].split("-")[1]) for x in self._consultas), default=0)
        return f"CON-{mayor + 1:05d}"

    def guardar(self, consulta: dict) -> dict:
        self._consultas.append(consulta)
        return consulta


consulta_repository = ConsultaRepository()
