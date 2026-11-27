"""Pasarela de pagos simulada (API externa). Responde de forma fija según los datos de pago.

Tarjeta (tarjeta_credito o tarjeta_debito), con datosPago:
- "tok_rechazado": la entidad financiera rechaza la transacción.
- "tok_no_disponible": la pasarela no responde.
- cualquier otro token con prefijo "tok_" (por ejemplo "tok_aprobado"): la transacción se aprueba.

PSE, con datosPago:
- "banco_no_disponible": la pasarela no responde.
- cualquier otro banco con prefijo "banco_" (por ejemplo "banco_bancolombia"): la transacción queda pendiente
  hasta que el banco la confirme (HU-014).

Notificaciones (HU-014): la pasarela firma cada notificación con HMAC-SHA256 en hexadecimal sobre la cadena
"transaccionId|estado|monto", con la clave compartida PASARELA_CLAVE_NOTIFICACIONES del .env o, si no está
definida, con la clave de prueba CLAVE_NOTIFICACIONES_POR_DEFECTO.
"""
import os

from domain.errores import PasarelaNoDisponibleError

CLAVE_NOTIFICACIONES_POR_DEFECTO = "clave-pasarela-simulada-2026"

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


def clave_notificaciones() -> str:
    """Clave compartida con la pasarela para firmar las notificaciones."""
    return os.getenv("PASARELA_CLAVE_NOTIFICACIONES") or CLAVE_NOTIFICACIONES_POR_DEFECTO


pasarela_pagos = PasarelaPagosSimulada()
