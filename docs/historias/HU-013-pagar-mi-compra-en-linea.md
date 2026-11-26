## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y tengo una compra pendiente de pago,
Para pagar mi viaje en cualquier momento, total o por abonos, con PSE o tarjeta, y tener la confirmación de inmediato,
Que el sistema procese mi pago a través de la pasarela de pagos y me informe el resultado de la transacción.

## 🔁 Flujo Esperado

- El cliente diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/pagos de `pagos.api` con el método POST.
- La capa API valida el token de acceso del cliente y el formato del JSON, y delega el caso de uso a `ProcesarPagoService`.
- El dominio valida que el pago esté asociado a una orden del cliente con saldo (RN-44), que el monto no supere el saldo disponible y que el medio sea `pse`, `tarjeta_credito` o `tarjeta_debito`.
- La claveIdempotencia evita cobrar dos veces el mismo intento de pago, aunque el cliente lo envíe varias veces.
- El servicio envía la transacción a la pasarela de pagos (API externa, simulada en este proyecto) y registra su resultado: `aprobado`, `rechazado` o `pendiente` (PSE).
- Si el pago es aprobado, el saldo se recalcula; si llega a cero, la orden queda `pagada` (RN-45) y el sistema liquida a los proveedores al valor neto (RN-48, RN-49), confirma la reserva (RN-61, RN-62) y genera la factura (RN-53, RN-57) automáticamente. Si queda saldo, la orden pasa a `pago_parcial`.
- Se reciben o consultan los campos:
- ventaId / Identificador de la orden
- monto / Valor a pagar
- medioPago / `pse`, `tarjeta_credito` o `tarjeta_debito`
- datosPago / Token de la tarjeta o banco para PSE (nunca el número de la tarjeta)
- claveIdempotencia / Identificador único del intento de pago


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint POST que recibe en el cuerpo JSON ventaId, monto, medioPago, datosPago y claveIdempotencia.
- [x] Solo se aceptan los medios `pse`, `tarjeta_credito` y `tarjeta_debito`; con otro medio responde 400 con "El medio de pago debe ser pse, tarjeta_credito o tarjeta_debito".
- [x] La tarjeta llega como token de la pasarela, con el prefijo `tok_`, y el sistema nunca recibe ni guarda su número; si datosPago no es un token responde 400 con "Los datos de la tarjeta deben ser el token de la pasarela con el prefijo tok_; no envíe el número de la tarjeta". Para PSE, datosPago indica el banco con el prefijo `banco_`; si no, responde 400 con "Para pagos por PSE, los datos de pago deben indicar el banco con el prefijo banco_".
- [x] La pasarela de pagos está simulada y responde siempre igual según datosPago:

  | medioPago | datosPago | Resultado |
  |---|---|---|
  | `tarjeta_credito` o `tarjeta_debito` | `tok_aprobado` (o cualquier otro token `tok_`) | 201, pago `aprobado` |
  | `tarjeta_credito` o `tarjeta_debito` | `tok_rechazado` | 402, pago `rechazado` |
  | `tarjeta_credito` o `tarjeta_debito` | `tok_no_disponible` | 503, no se registra el cobro |
  | `pse` | `banco_bancolombia` (o cualquier otro banco `banco_`) | 201, pago `pendiente` hasta la confirmación del banco (HU-014) |
  | `pse` | `banco_no_disponible` | 503, no se registra el cobro |

- [x] El pago debe estar asociado a una orden existente con saldo (RN-44). Si la orden no existe responde 404 con "La orden de venta no existe", y si ya está pagada responde 409 con "La orden ya está pagada y no tiene saldo pendiente".
- [x] El monto es obligatorio y mayor que cero ("El monto es obligatorio", "El monto debe ser mayor que cero"). Si supera el saldo pendiente responde 400 con "El monto supera el saldo pendiente".
- [x] El saldo disponible es el saldo pendiente menos los pagos PSE pendientes de la misma orden; si el monto lo supera responde 400 con "El monto supera el saldo disponible, porque hay un pago PSE pendiente de confirmación".
- [x] Si se repite la misma claveIdempotencia, se devuelve el pago original con el mismo pagoId, código 200 y el mensaje "El pago ya fue procesado con esta clave de idempotencia", y no se procesa un nuevo cobro. Si la clave se usó con otra orden, otro monto u otro medio, responde 409 con "La clave de idempotencia ya se usó en otro intento de pago".
- [x] Si la pasarela aprueba, se recalculan el total aprobado y el saldo; con saldo cero la orden queda `pagada` (RN-45) y se liquida a los proveedores al valor neto (RN-48, RN-49), se confirma la reserva con un localizador por servicio (RN-61, RN-62) y se genera la factura a nombre del cliente titular (RN-53, RN-57) automáticamente. Si queda saldo, la orden pasa a `pago_parcial`.
- [x] Si la pasarela rechaza la transacción se responde 402 con "La transacción fue rechazada por la entidad financiera", el pago queda registrado como `rechazado` y el saldo no cambia; si no está disponible se responde 503 con "La pasarela de pagos no está disponible. Intente más tarde" y no se registra el cobro.
- [x] Después del pago, la consulta de HU-012 muestra el nuevo total pagado, el saldo y el estado de la orden.
- [x] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`. Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido responde 401 con "La sesión expiró. Inicie sesión nuevamente".
- [x] El cliente solo paga sus propias órdenes; si la orden pertenece a otro cliente, o la cuenta no tiene rol cliente, responde 403 con el mensaje "No tiene permisos para realizar esta acción".
- [x] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message; por ejemplo, "El identificador de la orden es obligatorio", "El medio de pago es obligatorio", "Los datos de pago son obligatorios", "La clave de idempotencia es obligatoria" o "El campo 'monto' debe ser un número entero".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (fechaPago corresponde a la fecha y hora en que se procesa el pago; PAG-00021 y TRX-5580002 son los primeros identificadores libres, porque PAG-00020 y TRX-5580001 ya están precargados):

```json
{
  "success": true,
  "data": {
    "pagoId": "PAG-00021",
    "ventaId": "VEN-00012",
    "transaccionId": "TRX-5580002",
    "medioPago": "tarjeta_credito",
    "monto": 5000000,
    "estado": "aprobado",
    "saldoPendiente": 3081600,
    "estadoOrden": "pago_parcial",
    "reservaConfirmada": false,
    "facturaGenerada": false,
    "fechaPago": "2026-11-11T10:15:00-05:00"
  },
  "message": "Pago aprobado exitosamente"
}
```

- [x] Si el pago es por PSE, la transacción queda pendiente hasta la confirmación del banco:

```json
{
  "success": true,
  "data": {
    "pagoId": "PAG-00022",
    "ventaId": "VEN-00012",
    "transaccionId": "TRX-5580003",
    "medioPago": "pse",
    "monto": 3081600,
    "estado": "pendiente",
    "urlPago": "https://pasarela.simulada/pse/TRX-5580003",
    "saldoPendiente": 3081600
  },
  "message": "Pago en proceso. Complete la operación en su banco"
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
  "success": true,
  "data": {
    "pagoId": "PAG-00021",
    "ventaId": "VEN-00012",
    "transaccionId": "TRX-5580002",
    "medioPago": "tarjeta_credito",
    "monto": 5000000,
    "estado": "aprobado",
    "saldoPendiente": 3081600,
    "estadoOrden": "pago_parcial",
    "reservaConfirmada": false,
    "facturaGenerada": false,
    "fechaPago": "2026-11-11T10:15:00-05:00"
  },
  "message": "Pago aprobado exitosamente"
}

````

- [x] Si el pago aprobado deja el saldo en cero, la orden queda pagada, con la reserva confirmada y la factura generada (VEN-00014 se genera con HU-011 a partir de COT-00045; antes se registra el pago rechazado PAG-00023):

```json
{
  "success": true,
  "data": {
    "pagoId": "PAG-00024",
    "ventaId": "VEN-00014",
    "transaccionId": "TRX-5580005",
    "medioPago": "tarjeta_credito",
    "monto": 8081600,
    "estado": "aprobado",
    "saldoPendiente": 0,
    "estadoOrden": "pagada",
    "reservaConfirmada": true,
    "facturaGenerada": true,
    "fechaPago": "2026-11-11T10:45:00-05:00"
  },
  "message": "Pago aprobado exitosamente"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La cliente CLI-00188 (registrada con HU-001) inició sesión con HU-002 y su orden precargada VEN-00012 tiene saldo de 8.081.600, sin abonos.
- **Acción:** Ejecutar el endpoint POST /api/v1/pagos con 5.000.000 por tarjeta_credito, datosPago "tok_aprobado" y una claveIdempotencia nueva.
- **Resultado esperado:**

  - Código HTTP 201 Created
  - Campo success = true
  - Campo data.estado = "aprobado", data.saldoPendiente = 3081600 y data.estadoOrden = "pago_parcial"
  - Campo message contiene el texto: "Pago aprobado exitosamente"
  - Al repetir la misma solicitud responde 200 con el mismo pagoId y el texto "El pago ya fue procesado con esta clave de idempotencia", y el saldo no cambia

### ✅ Caso 2:

- **Precondición:** La orden VEN-00012 tiene saldo de 3.081.600.
- **Acción:** Ejecutar el endpoint POST /api/v1/pagos con 3.081.600 por pse y datosPago "banco_bancolombia".
- **Resultado esperado:**

  - Código HTTP 201 Created
  - Campo data.estado = "pendiente" y data.urlPago contiene la dirección para completar el pago
  - Campo message contiene el texto: "Pago en proceso. Complete la operación en su banco"
  - El saldo no cambia hasta que la pasarela confirme la transacción (HU-014), y un nuevo pago de la orden responde 400 con "El monto supera el saldo disponible, porque hay un pago PSE pendiente de confirmación"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint con tarjeta.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos (con PSE pendiente, data contiene pagoId, ventaId, transaccionId, medioPago, monto, estado, urlPago y saldoPendiente):

  - "success" (booleano)
  - "data" (objeto), con los campos:
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

### ❌ Caso 4: 

- **Precondición:** La pasarela rechaza la tarjeta (datosPago "tok_rechazado"), o el monto supera el saldo.
- **Acción:** Ejecutar el endpoint con cada uno de esos casos.
- **Resultado esperado:**

  - Código HTTP 402 Payment Required si la pasarela rechaza, con data.estado = "rechazado", o 400 Bad Request si el monto supera el saldo, con data = null
  - El saldo no cambia
  - Campo success = false
  - Campo message contiene el texto: "La transacción fue rechazada por la entidad financiera" o "El monto supera el saldo pendiente", según el caso

### ❌ Caso 5: 

- **Precondición:** La pasarela de pagos no responde (datosPago "tok_no_disponible" con tarjeta o "banco_no_disponible" con PSE).
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de falla de la pasarela.
- **Resultado esperado:**
  - Código HTTP 503 Service Unavailable
  - No se registra el cobro y el saldo no cambia
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La pasarela de pagos no está disponible. Intente más tarde"

## ✅ Definición de Hecho

# Historia: Pagar mi compra en línea

## 📦 Alcance Funcional

- [x] El endpoint procesa el pago con la pasarela y registra su resultado.
- [x] Un mismo intento de pago nunca se cobra dos veces.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar los medios de pago, el monto frente al saldo, la idempotencia y las respuestas de la pasarela.
- [x] Se cubrieron los casos de error y de excepción.
- [x] Las pruebas funcionales están documentadas y pasadas.

## 📄 Documentación Técnica

- [x] Endpoint documentado en Swagger / OpenAPI.
- [x] Se describe:

  - Propósito del endpoint
  - Campos de entrada y salida
  - Ejemplo de respuesta exitosa
  - Ejemplo de error

## 🔐 Manejo de Errores

- [x] Se devuelve código HTTP 503 cuando la pasarela de pagos no está disponible y 500 cuando falla el acceso al repositorio de datos, con el mensaje "No fue posible procesar el pago".
- [x] El campo `message` en el JSON incluye un texto amigable y claro para el usuario técnico o frontend.
