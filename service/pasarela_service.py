"""Pasarela de pagos simulada (API externa). Responde de forma fija según los datos de pago.

Tarjeta (tarjeta_credito o tarjeta_debito), con datosPago:
- "tok_rechazado": la entidad financiera rechaza la transacción.
- "tok_no_disponible": la pasarela no responde.
- cualquier otro token con prefijo "tok_" (por ejemplo "tok_aprobado"): la transacción se aprueba.

PSE, con datosPago:
- "banco_no_disponible": la pasarela no responde.
- cualquier otro banco con prefijo "banco_" (por ejemplo "banco_bancolombia"): la transacción queda pendiente
  hasta que el banco la confirme (HU-014).
"""
from domain.errores import PasarelaNoDisponibleError

TOKEN_RECHAZADO = "tok_rechazado"
TOKEN_NO_DISPONIBLE = "tok_no_disponible"
BANCO_NO_DISPONIBLE = "banco_no_disponible"


class PasarelaPagosSimulada:
    """Envía la transacción a la pasarela y devuelve su resultado: aprobado, rechazado o pendiente."""

    def cobrar(self, medio_pago: str, datos_pago: str, monto: int, transaccion_id: str) -> str:
        datos = datos_pago.strip().lower()
        if datos in (TOKEN_NO_DISPONIBLE, BANCO_NO_DISPONIBLE):
            raise PasarelaNoDisponibleError("La pasarela de pagos no está disponible. Intente más tarde")
        if medio_pago == "pse":
            return "pendiente"
        return "rechazado" if datos == TOKEN_RECHAZADO else "aprobado"


pasarela_pagos = PasarelaPagosSimulada()
