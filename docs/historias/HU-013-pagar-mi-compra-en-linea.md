## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y tengo una compra pendiente de pago,
Para pagar mi viaje en cualquier momento, total o por abonos, con PSE o tarjeta, y tener la confirmación de inmediato,
Que el sistema procese mi pago a través de la pasarela de pagos y me informe el resultado de la transacción.

## 🔁 Flujo Esperado

- El cliente diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/pagos de `pagos.api` con el método POST.
- La capa API valida el formato del JSON y delega el caso de uso a `ProcesarPagoService`.
- El dominio valida que el pago esté asociado a una orden con saldo (RN-44), que el monto no supere el saldo y que el medio sea `pse`, `tarjeta_credito` o `tarjeta_debito`.
- La claveIdempotencia evita cobrar dos veces el mismo intento de pago, aunque el cliente lo envíe varias veces.
- El servicio envía la transacción a la pasarela de pagos (API externa, simulada en este proyecto) y registra su resultado: `aprobado`, `rechazado` o `pendiente` (PSE).
- Si el pago es aprobado, el saldo se recalcula; si llega a cero, la orden queda `pagada` (RN-45) y el sistema liquida a los proveedores al valor neto (RN-48, RN-49), confirma la reserva (RN-61, RN-62) y genera la factura (RN-53, RN-57) automáticamente.
- Se reciben o consultan los campos:
- ventaId / Identificador de la orden
- monto / Valor a pagar
- medioPago / `pse`, `tarjeta_credito` o `tarjeta_debito`
- datosPago / Token de la tarjeta o banco para PSE (nunca el número de la tarjeta)
- claveIdempotencia / Identificador único del intento de pago


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint POST que recibe en el cuerpo JSON ventaId, monto, medioPago, datosPago y claveIdempotencia.
- [ ] Solo se aceptan los medios `pse`, `tarjeta_credito` y `tarjeta_debito`; la tarjeta llega como token de la pasarela y el sistema nunca recibe ni guarda su número.
- [ ] El pago debe estar asociado a una orden existente con saldo (RN-44) y el monto no puede superar el saldo.
- [ ] Si se repite la misma claveIdempotencia, se devuelve el pago original y no se procesa un nuevo cobro.
- [ ] Si la pasarela aprueba y el saldo llega a cero, la orden queda `pagada` (RN-45) y se liquidan proveedores, se confirma la reserva y se genera la factura automáticamente.
- [ ] Si la pasarela rechaza la transacción se responde 402, y si no está disponible se responde 503.
- [ ] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`; sin token, o con el token vencido, responde 401.
- [ ] El cliente solo accede a sus propios recursos; si el recurso pertenece a otro cliente, responde 403.
- [ ] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Pago aprobado exitosamente",
  "data": {
    "pagoId": "PAG-00031",
    "ventaId": "VEN-00012",
    "transaccionId": "TRX-5583201",
    "medioPago": "tarjeta_credito",
    "monto": 5000000,
    "estado": "aprobado",
    "saldoPendiente": 3081600,
    "estadoOrden": "pago_parcial",
    "reservaConfirmada": false,
    "facturaGenerada": false,
    "fechaPago": "2026-11-05T10:15:00-05:00"
  },
  "success": true
}
```

- [ ] Si el pago es por PSE, la transacción queda pendiente hasta la confirmación del banco:

```json
{
  "message": "Pago en proceso. Complete la operación en su banco",
  "data": {
    "pagoId": "PAG-00032",
    "ventaId": "VEN-00012",
    "transaccionId": "TRX-5583244",
    "medioPago": "pse",
    "monto": 3081600,
    "estado": "pendiente",
    "urlPago": "https://pasarela.simulada/pse/TRX-5583244",
    "saldoPendiente": 3081600
  },
  "success": true
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Pagar mi compra en línea

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/pagos`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "message": "Pago aprobado exitosamente",
  "data": {
    "pagoId": "PAG-00031",
    "ventaId": "VEN-00012",
    "transaccionId": "TRX-5583201",
    "medioPago": "tarjeta_credito",
    "monto": 5000000,
    "estado": "aprobado",
    "saldoPendiente": 3081600,
    "estadoOrden": "pago_parcial",
    "reservaConfirmada": false,
    "facturaGenerada": false,
    "fechaPago": "2026-11-05T10:15:00-05:00"
  },
  "success": true
}

````

- [ ] Si el pago es por PSE, la transacción queda pendiente hasta la confirmación del banco:

```json
{
  "message": "Pago en proceso. Complete la operación en su banco",
  "data": {
    "pagoId": "PAG-00032",
    "ventaId": "VEN-00012",
    "transaccionId": "TRX-5583244",
    "medioPago": "pse",
    "monto": 3081600,
    "estado": "pendiente",
    "urlPago": "https://pasarela.simulada/pse/TRX-5583244",
    "saldoPendiente": 3081600
  },
  "success": true
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La orden VEN-00012 tiene saldo de 8.081.600.
- **Acción:** Ejecutar el endpoint POST /api/v1/pagos con 5.000.000 por tarjeta_credito, un token válido y una claveIdempotencia nueva.
- **Resultado esperado:**

  - Código HTTP 201 Created
  - Campo success = true
  - Campo data.estado = "aprobado" y data.saldoPendiente = 3081600
  - Campo message contiene el texto: "Pago aprobado exitosamente"

### ✅ Caso 2:

- **Precondición:** La orden VEN-00012 tiene saldo de 3.081.600.
- **Acción:** Ejecutar el endpoint POST /api/v1/pagos con 3.081.600 por pse.
- **Resultado esperado:**

  - Código HTTP 201 Created
  - Campo data.estado = "pendiente" y data.urlPago contiene la dirección para completar el pago
  - El saldo no cambia hasta que la pasarela confirme la transacción

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "pagoId" (texto)
  - "ventaId" (texto)
  - "transaccionId" (texto)
  - "medioPago" (texto)
  - "monto" (número)
  - "estado" (texto)
  - "saldoPendiente" (número)
  - "estadoOrden" (texto)
  - "reservaConfirmada" (booleano)
  - "facturaGenerada" (booleano)
  - "fechaPago" (fecha ISO 8601)
  - "message" (texto)
  - "success" (booleano)

### ❌ Caso 4: 

- **Precondición:** La pasarela rechaza la tarjeta, o el monto supera el saldo.
- **Acción:** Ejecutar el endpoint con cada uno de esos casos.
- **Resultado esperado:**

  - Código HTTP 402 Payment Required si la pasarela rechaza, o 400 Bad Request si el monto supera el saldo
  - El saldo no cambia
  - Campo success = false
  - Campo message contiene el texto: "La transacción fue rechazada por la entidad financiera" o "El monto supera el saldo pendiente", según el caso

### ❌ Caso 5: 

- **Precondición:** La pasarela de pagos no responde.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de falla de la pasarela.
- **Resultado esperado:**
  - Código HTTP 503 Service Unavailable
  - No se registra el cobro y el saldo no cambia
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La pasarela de pagos no está disponible. Intente más tarde"

## ✅ Definición de Hecho

# Historia: Pagar mi compra en línea

## 📦 Alcance Funcional

- [ ] El endpoint procesa el pago con la pasarela y registra su resultado.
- [ ] Un mismo intento de pago nunca se cobra dos veces.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar los medios de pago, el monto frente al saldo, la idempotencia y las respuestas de la pasarela.
- [ ] Se cubrieron los casos de error y de excepción.
- [ ] Las pruebas funcionales están documentadas y pasadas.

## 📄 Documentación Técnica

- [ ] Endpoint documentado en Swagger / OpenAPI.
- [ ] Se describe:

  - Propósito del endpoint
  - Campos de entrada y salida
  - Ejemplo de respuesta exitosa
  - Ejemplo de error

## 🔐 Manejo de Errores

- [ ] Se devuelve código HTTP 503 cuando la pasarela de pagos no está disponible y 500 cuando falla el acceso al repositorio de datos.
- [ ] El campo `message` en el JSON incluye un texto amigable y claro para el usuario técnico o frontend.
