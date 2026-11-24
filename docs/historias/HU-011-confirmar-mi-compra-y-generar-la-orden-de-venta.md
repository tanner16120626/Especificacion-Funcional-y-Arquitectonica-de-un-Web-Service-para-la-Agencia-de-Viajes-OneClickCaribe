## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y acepté mi cotización,
Para formalizar mi compra y poder pagarla, total o por abonos,
Que el sistema genere automáticamente la orden de venta a partir de mi cotización aceptada, con la modalidad de pago que elija.

## 🔁 Flujo Esperado

- El cliente diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/ventas de `ventas.api` con el método POST.
- La capa API valida el token de acceso del cliente y el formato del JSON, y delega el caso de uso a `GenerarOrdenVentaService`.
- El servicio verifica que la cotización pertenezca al cliente del token y que no tenga ya una orden, y el dominio valida que esté aceptada y vigente (RN-31).
- La orden recibe un código propio vinculado a la cotización (RN-32) y copia sus precios, que ya no se modifican (RN-34).
- Si la modalidad es parcial, la fecha límite del saldo es obligatoria y anterior al viaje (RN-33).
- Se reciben o consultan los campos:
- cotizacionId / Identificador de la cotización aceptada
- modalidadPago / `total` o `parcial`
- fechaLimiteSaldo / Fecha límite para pagar el saldo (obligatoria si es parcial)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint POST que recibe en el cuerpo JSON cotizacionId, modalidadPago y fechaLimiteSaldo.
- [x] Solo se genera la orden de una cotización aceptada y vigente (RN-31); si no está aceptada se responde 400 con el mensaje "Solo se genera la orden de una cotización aceptada", y si ya pasó su vigencia, 400 con el mensaje "La cotización está vencida y no puede generar una orden de venta".
- [x] La orden tiene un ventaId propio, distinto del cotizacionId y vinculado a él (RN-32).
- [x] Si la modalidad es parcial, fechaLimiteSaldo es obligatoria y anterior a la fecha de inicio del viaje (RN-33); sin ella se responde 400 con el mensaje "La fecha límite del saldo es obligatoria", y si no es anterior al viaje, 400 con el mensaje "La fecha límite del saldo debe ser anterior a la fecha de inicio del viaje". Si la modalidad es total, fechaLimiteSaldo queda en null.
- [x] Los precios se copian de la cotización y no se modifican después (RN-34).
- [x] Una cotización solo tiene una orden de venta; si ya la tiene, se responde 409 con el mensaje "La cotización ya tiene una orden de venta" y en data la orden existente.
- [x] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`. Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido responde 401 con "La sesión expiró. Inicie sesión nuevamente".
- [x] El cliente solo usa sus propias cotizaciones; si la cotización pertenece a otro cliente, o la cuenta no tiene rol cliente, responde 403 con el mensaje "No tiene permisos para realizar esta acción".
- [x] Si la cotización no existe, se responde 404 con el mensaje "La cotización no existe".
- [x] Los errores de formato del JSON se responden con código 400 y la estructura success, data y message. Mensajes exactos: sin cotizacionId, "El identificador de la cotización es obligatorio"; sin modalidadPago, "La modalidad de pago es obligatoria"; modalidad distinta de total o parcial, "La modalidad de pago debe ser total o parcial"; fechaLimiteSaldo con otro formato, "El campo 'fechaLimiteSaldo' debe ser una fecha con formato AAAA-MM-DD".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (fechaCreacion corresponde a la fecha y hora en que se genera la orden; VEN-00014 es el primer identificador libre, porque VEN-00010, VEN-00012 y VEN-00013 ya están precargadas):

```json
{
  "success": true,
  "data": {
    "ventaId": "VEN-00014",
    "cotizacionId": "COT-00045",
    "clienteId": "CLI-00188",
    "valorTotal": 8081600,
    "modalidadPago": "parcial",
    "fechaLimiteSaldo": "2026-11-30",
    "totalPagado": 0,
    "saldoPendiente": 8081600,
    "estado": "pendiente_pago",
    "fechaCreacion": "2026-11-11T10:25:00-05:00"
  },
  "message": "Orden de venta generada exitosamente"
}
```

- [x] Si la cotización ya tiene una orden, el backend retorna:

```json
{
  "success": false,
  "data": {
    "ventaId": "VEN-00014",
    "cotizacionId": "COT-00045"
  },
  "message": "La cotización ya tiene una orden de venta"
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Confirmar mi compra y generar la orden de venta

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/ventas`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "success": true,
  "data": {
    "ventaId": "VEN-00014",
    "cotizacionId": "COT-00045",
    "clienteId": "CLI-00188",
    "valorTotal": 8081600,
    "modalidadPago": "parcial",
    "fechaLimiteSaldo": "2026-11-30",
    "totalPagado": 0,
    "saldoPendiente": 8081600,
    "estado": "pendiente_pago",
    "fechaCreacion": "2026-11-11T10:25:00-05:00"
  },
  "message": "Orden de venta generada exitosamente"
}

````

- [x] Si la cotización ya tiene una orden, el backend retorna:

```json
{
  "success": false,
  "data": {
    "ventaId": "VEN-00014",
    "cotizacionId": "COT-00045"
  },
  "message": "La cotización ya tiene una orden de venta"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La cliente CLI-00188 (registrada con HU-001) inició sesión con HU-002 y su cotización precargada COT-00045 está aceptada, vigente y sin orden.
- **Acción:** Ejecutar el endpoint POST /api/v1/ventas con cotizacionId COT-00045, modalidad parcial y fecha límite 2026-11-30.
- **Resultado esperado:**

  - Código HTTP 201 Created
  - Campo success = true
  - Campo data.ventaId = "VEN-00014" y data.cotizacionId = "COT-00045"
  - Campo data.estado = "pendiente_pago" y data.saldoPendiente = 8081600
  - Campo message contiene el texto: "Orden de venta generada exitosamente"

### ✅ Caso 2:

- **Precondición:** La cotización COT-00045 ya tiene la orden VEN-00014, generada en el Caso 1.
- **Acción:** Ejecutar de nuevo el endpoint POST /api/v1/ventas con cotizacionId COT-00045.
- **Resultado esperado:**

  - Código HTTP 409 Conflict
  - No se crea una nueva orden
  - Campo success = false
  - Campo data.ventaId = "VEN-00014", la orden existente
  - Campo message contiene el texto: "La cotización ya tiene una orden de venta"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "ventaId" (texto)
    - "cotizacionId" (texto)
    - "clienteId" (texto)
    - "valorTotal" (número)
    - "modalidadPago" (texto)
    - "fechaLimiteSaldo" (fecha ISO 8601, o null si la modalidad es total)
    - "totalPagado" (número)
    - "saldoPendiente" (número)
    - "estado" (texto)
    - "fechaCreacion" (fecha ISO 8601)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** La cotización COT-00046 fue rechazada con HU-010, o se envía modalidad parcial sin fecha límite.
- **Acción:** Ejecutar el endpoint con cada uno de esos casos.
- **Resultado esperado:**

  - Código HTTP 400 Bad Request
  - No se crea la orden
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "Solo se genera la orden de una cotización aceptada" o "La fecha límite del saldo es obligatoria", según el caso

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible generar la orden de venta"

## ✅ Definición de Hecho

# Historia: Confirmar mi compra y generar la orden de venta

## 📦 Alcance Funcional

- [x] El endpoint genera la orden de venta a partir de una cotización aceptada.
- [x] La orden conserva los precios de la cotización y su modalidad de pago.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar el estado de la cotización, la duplicidad y la modalidad de pago.
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
