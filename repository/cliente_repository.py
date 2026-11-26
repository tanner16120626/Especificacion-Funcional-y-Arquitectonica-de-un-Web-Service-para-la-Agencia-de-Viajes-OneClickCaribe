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

    def buscar_por_id(self, cliente_id: str) -> Optional[dict]:
        return next((c for c in self._clientes if c["clienteId"] == cliente_id), None)

    def buscar_cuenta_por_correo(self, correo: str) -> Optional[dict]:
        correo = (correo or "").strip().lower()
        return next((c for c in self._cuentas if (c["correo"] or "").strip().lower() == correo), None)

    def correo_en_uso_por_otro(self, correo: str, cliente_id: str) -> bool:
        """Indica si el correo pertenece a otro cliente o a una cuenta que no es la del cliente."""
        correo = (correo or "").strip().lower()
        en_clientes = any((c["correo"] or "").strip().lower() == correo and c["clienteId"] != cliente_id
                          for c in self._clientes)
        en_cuentas = any((c["correo"] or "").strip().lower() == correo and c["clienteId"] != cliente_id
                         for c in self._cuentas)
        return en_clientes or en_cuentas

    def actualizar_contacto(self, cliente_id: str, telefono: Optional[str], correo: Optional[str],
                            fecha_actualizacion: str) -> dict:
        """Actualiza el contacto del cliente y el correo de su cuenta de acceso."""
        cliente = self.buscar_por_id(cliente_id)
        cliente["telefono"] = telefono
        cliente["correo"] = correo
        cliente["fechaActualizacion"] = fecha_actualizacion
        for cuenta in self._cuentas:
            if cuenta["clienteId"] == cliente_id:
                cuenta["correo"] = correo
        return cliente

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
