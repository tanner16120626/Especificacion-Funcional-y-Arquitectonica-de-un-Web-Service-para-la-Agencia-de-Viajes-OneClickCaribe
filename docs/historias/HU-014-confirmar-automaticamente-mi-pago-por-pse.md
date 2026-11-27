## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y pagué mi compra por PSE,
Para que mi pago quede confirmado en cuanto el banco lo apruebe, a cualquier hora y sin intervención de la agencia,
Que el sistema reciba la confirmación de la pasarela de pagos, valide su autenticidad y actualice mi compra automáticamente.

## 🔁 Flujo Esperado

- La pasarela de pagos envía automáticamente la notificación en JSON al endpoint (webhook) cuando el banco resuelve la transacción.
- El sistema consume el endpoint /api/v1/pagos/notificaciones de `pagos.api` con el método POST.
- La capa API valida el formato del JSON y delega el caso de uso a `ProcesarNotificacionPagoService`.
- El servicio valida la firma de la notificación con la clave compartida con la pasarela; si no coincide, la rechaza.
- El dominio busca el pago por su transaccionId y verifica que el monto notificado coincida con el registrado.
- Si la transacción ya fue procesada (el pago ya no está pendiente), responde sin volver a aplicarla (idempotencia).
- Si el resultado es `aprobado` y el saldo llega a cero, la orden queda `pagada` (RN-45) y se liquidan proveedores (RN-48, RN-49), se confirma la reserva (RN-61, RN-62) y se genera la factura (RN-53, RN-57) automáticamente, con la misma automatización de HU-013.
- Si el resultado es `rechazado`, el pago queda rechazado, el saldo no cambia y el saldo disponible queda libre para otro pago.
- Se reciben o consultan los campos:
- transaccionId / Identificador de la transacción en la pasarela
- estado / `aprobado` o `rechazado`
- monto / Valor de la transacción
- firma / Firma de seguridad de la notificación


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint POST que recibe en el cuerpo JSON transaccionId, estado, monto y firma.
- [x] La firma es HMAC-SHA256 en hexadecimal de la cadena `transaccionId|estado|monto`, con los valores tal como se envían (por ejemplo `TRX-5580003|aprobado|3081600`). La clave compartida se toma de la variable `PASARELA_CLAVE_NOTIFICACIONES` del `.env`; si no está definida, se usa la clave de prueba `clave-pasarela-simulada-2026`.
- [x] Sin firma responde 401 con "La firma de la notificación es obligatoria"; con una firma inválida responde 401 con "La firma de la notificación no es válida".
- [x] El estado debe ser `aprobado` o `rechazado`; si no, responde 400 con "El estado debe ser aprobado o rechazado".
- [x] Si la transacción no existe responde 404 con "La transacción no existe".
- [x] El monto notificado debe coincidir con el de la transacción registrada; si no, responde 400 con "El monto no coincide con la transacción".
- [x] Una notificación repetida no se aplica dos veces: si el pago ya no está pendiente, responde 200 con el pago tal como quedó y el mensaje "La notificación ya fue procesada".
- [x] Si el pago queda aprobado se recalcula el saldo (RN-45); si llega a cero, se ejecuta la automatización de liquidación, reserva y factura de HU-013.
- [x] Si el pago queda rechazado, el saldo no cambia y el cliente puede volver a pagar ese valor con HU-013.
- [x] Después de la notificación, la consulta de HU-012 muestra el nuevo estado de la orden.
- [x] Este endpoint no usa el token del cliente: lo invoca la pasarela de pagos y se autentica con la firma de la notificación.
- [x] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message; por ejemplo, "El identificador de la transacción es obligatorio", "El estado es obligatorio", "El monto es obligatorio" o "El campo 'monto' debe ser un número entero".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (PAG-00022 y TRX-5580003 son el pago PSE de VEN-00012 registrado con HU-013, después del abono PAG-00021 con tarjeta; la respuesta no tiene campos de fecha):

```json
{
  "success": true,
  "data": {
    "pagoId": "PAG-00022",
    "transaccionId": "TRX-5580003",
    "estadoPago": "aprobado",
    "saldoPendiente": 0,
    "estadoOrden": "pagada",
    "reservaConfirmada": true,
    "facturaGenerada": true
  },
  "message": "Notificación procesada exitosamente"
}
```

- [x] Si la notificación ya fue procesada, el backend retorna el pago tal como quedó:

```json
{
  "success": true,
  "data": {
    "pagoId": "PAG-00022",
    "transaccionId": "TRX-5580003",
    "estadoPago": "aprobado",
    "saldoPendiente": 0,
    "estadoOrden": "pagada",
    "reservaConfirmada": true,
    "facturaGenerada": true
  },
  "message": "La notificación ya fue procesada"
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Confirmar automáticamente mi pago por PSE

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/pagos/notificaciones`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "success": true,
  "data": {
    "pagoId": "PAG-00022",
    "transaccionId": "TRX-5580003",
    "estadoPago": "aprobado",
    "saldoPendiente": 0,
    "estadoOrden": "pagada",
    "reservaConfirmada": true,
    "facturaGenerada": true
  },
  "message": "Notificación procesada exitosamente"
}

````

- [x] Si el banco rechaza la transacción, el backend retorna (PAG-00023 y TRX-5580004 son el pago PSE de VEN-00014, la orden generada con HU-011 a partir de COT-00045):

```json
{
  "success": true,
  "data": {
    "pagoId": "PAG-00023",
    "transaccionId": "TRX-5580004",
    "estadoPago": "rechazado",
    "saldoPendiente": 8081600,
    "estadoOrden": "pendiente_pago",
    "reservaConfirmada": false,
    "facturaGenerada": false
  },
  "message": "Notificación procesada exitosamente"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** Con HU-013, la orden VEN-00012 recibió un abono aprobado de 5.000.000 (PAG-00021) y el pago PAG-00022 por PSE de 3.081.600 está pendiente y cubre el saldo.
- **Acción:** Ejecutar el endpoint POST /api/v1/pagos/notificaciones con transaccionId "TRX-5580003", estado "aprobado", monto 3081600 y su firma válida.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.estadoOrden = "pagada" y data.reservaConfirmada = true y data.facturaGenerada = true
  - Campo message contiene el texto: "Notificación procesada exitosamente"

### ✅ Caso 2:

- **Precondición:** La transacción TRX-5580003 ya fue procesada.
- **Acción:** Ejecutar de nuevo el endpoint con la misma notificación.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - El pago y la orden no cambian
  - Campo message contiene el texto: "La notificación ya fue procesada"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "pagoId" (texto)
    - "transaccionId" (texto)
    - "estadoPago" (texto)
    - "saldoPendiente" (número)
    - "estadoOrden" (texto)
    - "reservaConfirmada" (booleano)
    - "facturaGenerada" (booleano)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** La notificación llega con una firma inválida, o con un monto distinto al registrado.
- **Acción:** Ejecutar el endpoint con cada uno de esos casos.
- **Resultado esperado:**

  - Código HTTP 401 Unauthorized si la firma es inválida, o 400 Bad Request si el monto no coincide
  - El pago no cambia
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La firma de la notificación no es válida" o "El monto no coincide con la transacción", según el caso

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible procesar la notificación"

## ✅ Definición de Hecho

# Historia: Confirmar automáticamente mi pago por PSE

## 📦 Alcance Funcional

- [x] El endpoint actualiza el pago según la notificación de la pasarela.
- [x] Solo se aceptan notificaciones con firma válida y una notificación repetida no se aplica dos veces.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar la firma, la coincidencia del monto y la idempotencia de la notificación.
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

- [x] Se devuelve código HTTP 500 cuando falla el acceso al repositorio de datos.
- [x] El campo `message` en el JSON incluye un texto amigable y claro para el usuario técnico o frontend.
