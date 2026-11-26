## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y pagué mi compra por PSE,
Para que mi pago quede confirmado en cuanto el banco lo apruebe, a cualquier hora y sin intervención de la agencia,
Que el sistema reciba la confirmación de la pasarela de pagos, valide su autenticidad y actualice mi compra automáticamente.

## 🔁 Flujo Esperado

- La pasarela de pagos envía automáticamente la notificación en JSON al endpoint (webhook) cuando el banco resuelve la transacción.
- El sistema consume el endpoint /api/v1/pagos/notificaciones de `pagos.api` con el método POST.
- La capa API valida el formato del JSON y delega el caso de uso a `ProcesarNotificacionPagoService`.
- La capa API valida la firma de la notificación con la clave compartida con la pasarela; si no coincide, la rechaza.
- El dominio busca el pago por su transaccionId y verifica que el monto notificado coincida con el registrado.
- Si la transacción ya fue procesada, responde sin volver a aplicarla (idempotencia).
- Si el resultado es `aprobado` y el saldo llega a cero, la orden queda `pagada` (RN-45) y se liquidan proveedores (RN-48, RN-49), se confirma la reserva (RN-61, RN-62) y se genera la factura (RN-53, RN-57) automáticamente.
- Se reciben o consultan los campos:
- transaccionId / Identificador de la transacción en la pasarela
- estado / `aprobado` o `rechazado`
- monto / Valor de la transacción
- firma / Firma de seguridad de la notificación


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint POST que recibe en el cuerpo JSON transaccionId, estado, monto y firma.
- [ ] Se valida la firma con la clave compartida con la pasarela; una firma inválida se rechaza con 401.
- [ ] El monto notificado debe coincidir con el de la transacción registrada.
- [ ] Una notificación repetida no se aplica dos veces.
- [ ] Si el pago queda aprobado y el saldo llega a cero, se ejecuta la automatización de liquidación, reserva y factura.
- [ ] Este endpoint no usa el token del cliente: lo invoca la pasarela de pagos y se autentica con la firma de la notificación.
- [ ] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Notificación procesada exitosamente",
  "data": {
    "pagoId": "PAG-00032",
    "transaccionId": "TRX-5583244",
    "estadoPago": "aprobado",
    "saldoPendiente": 0,
    "estadoOrden": "pagada",
    "reservaConfirmada": true,
    "facturaGenerada": true
  },
  "success": true
}
```

- [ ] Si la notificación ya fue procesada, el backend retorna:

```json
{
  "message": "La notificación ya fue procesada",
  "data": {
    "pagoId": "PAG-00032",
    "transaccionId": "TRX-5583244",
    "estadoPago": "aprobado"
  },
  "success": true
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
  "message": "Notificación procesada exitosamente",
  "data": {
    "pagoId": "PAG-00032",
    "transaccionId": "TRX-5583244",
    "estadoPago": "aprobado",
    "saldoPendiente": 0,
    "estadoOrden": "pagada",
    "reservaConfirmada": true,
    "facturaGenerada": true
  },
  "success": true
}

````

- [ ] Si la notificación ya fue procesada, el backend retorna:

```json
{
  "message": "La notificación ya fue procesada",
  "data": {
    "pagoId": "PAG-00032",
    "transaccionId": "TRX-5583244",
    "estadoPago": "aprobado"
  },
  "success": true
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** El pago PAG-00032 por PSE está pendiente y cubre el saldo de la orden VEN-00012.
- **Acción:** Ejecutar el endpoint POST /api/v1/pagos/notificaciones con transaccionId TRX-5583244, estado "aprobado", el monto correcto y una firma válida.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.estadoOrden = "pagada" y data.reservaConfirmada = true y data.facturaGenerada = true
  - Campo message contiene el texto: "Notificación procesada exitosamente"

### ✅ Caso 2:

- **Precondición:** La transacción TRX-5583244 ya fue procesada.
- **Acción:** Ejecutar de nuevo el endpoint con la misma notificación.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - El pago y la orden no cambian
  - Campo message contiene el texto: "La notificación ya fue procesada"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "pagoId" (texto)
  - "transaccionId" (texto)
  - "estadoPago" (texto)
  - "saldoPendiente" (número)
  - "estadoOrden" (texto)
  - "reservaConfirmada" (booleano)
  - "facturaGenerada" (booleano)
  - "message" (texto)
  - "success" (booleano)

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

- [ ] El endpoint actualiza el pago según la notificación de la pasarela.
- [ ] Solo se aceptan notificaciones con firma válida y una notificación repetida no se aplica dos veces.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar la firma, la coincidencia del monto y la idempotencia de la notificación.
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

- [ ] Se devuelve código HTTP 500 cuando falla el acceso al repositorio de datos.
- [ ] El campo `message` en el JSON incluye un texto amigable y claro para el usuario técnico o frontend.
