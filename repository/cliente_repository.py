"""Repositorio en memoria de clientes y de sus cuentas de acceso."""
from typing import Optional

from repository.datos_iniciales import CLIENTES, CUENTAS, copia

CONSECUTIVO_INICIAL = 188


class ClienteRepository:
    """Guarda y consulta clientes y cuentas en la base de datos temporal."""

    def __init__(self):
        self._clientes = copia(CLIENTES)
        self._cuentas = copia(CUENTAS)

    def buscar_por_documento(self, documento: str) -> Optional[dict]:
        return next((c for c in self._clientes if c["documento"] == documento), None)

    def siguiente_cliente_id(self) -> str:
        usados = {int(c["clienteId"].split("-")[1]) for c in self._clientes}
        numero = CONSECUTIVO_INICIAL
        while numero in usados:
            numero += 1
        return f"CLI-{numero:05d}"

    def siguiente_cuenta_id(self) -> str:
        mayor = max((int(c["cuentaId"].split("-")[1]) for c in self._cuentas), default=0)
        return f"CTA-{mayor + 1:03d}"

    def guardar(self, cliente: dict, cuenta: dict) -> dict:
        self._clientes.append(cliente)
        self._cuentas.append(cuenta)
        return cliente


cliente_repository = ClienteRepository()
