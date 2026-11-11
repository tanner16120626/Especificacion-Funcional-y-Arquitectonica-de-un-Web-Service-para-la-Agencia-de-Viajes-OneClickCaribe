## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y acepté mi cotización,
Para formalizar mi compra y poder pagarla, total o por abonos,
Que el sistema genere automáticamente la orden de venta a partir de mi cotización aceptada, con la modalidad de pago que elija.

## 🔁 Flujo Esperado

- El cliente diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/ventas de `ventas.api` con el método POST.
- La capa API valida el formato del JSON y delega el caso de uso a `GenerarOrdenVentaService`.
- El dominio valida que la cotización esté aceptada y vigente (RN-31) y que no tenga ya una orden.
- La orden recibe un código propio vinculado a la cotización (RN-32) y copia sus precios, que ya no se modifican (RN-34).
- Si la modalidad es parcial, la fecha límite del saldo es obligatoria y anterior al viaje (RN-33).
- Se reciben o consultan los campos:
- cotizacionId / Identificador de la cotización aceptada
- modalidadPago / `total` o `parcial`
- fechaLimiteSaldo / Fecha límite para pagar el saldo (obligatoria si es parcial)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint POST que recibe en el cuerpo JSON cotizacionId, modalidadPago y fechaLimiteSaldo.
- [ ] Solo se genera la orden de una cotización aceptada y vigente (RN-31).
- [ ] La orden tiene un ventaId propio, distinto del cotizacionId y vinculado a él (RN-32).
- [ ] Si la modalidad es parcial, fechaLimiteSaldo es obligatoria y anterior a la fecha de inicio del viaje (RN-33).
- [ ] Los precios se copian de la cotización y no se modifican después (RN-34).
- [ ] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`; sin token, o con el token vencido, responde 401.
- [ ] El cliente solo accede a sus propios recursos; si el recurso pertenece a otro cliente, responde 403.
- [ ] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Orden de venta generada exitosamente",
  "data": {
    "ventaId": "VEN-00012",
    "cotizacionId": "COT-00045",
    "clienteId": "CLI-00188",
    "valorTotal": 8081600,
    "modalidadPago": "parcial",
    "fechaLimiteSaldo": "2026-11-30",
    "totalPagado": 0,
    "saldoPendiente": 8081600,
    "estado": "pendiente_pago",
    "fechaCreacion": "2026-11-05T11:05:00-05:00"
  },
  "success": true
}
```

- [ ] Si la cotización ya tiene una orden, el backend retorna:

```json
{
  "message": "La cotización ya tiene una orden de venta",
  "data": {
    "ventaId": "VEN-00012",
    "cotizacionId": "COT-00045"
  },
  "success": false
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
  "message": "Orden de venta generada exitosamente",
  "data": {
    "ventaId": "VEN-00012",
    "cotizacionId": "COT-00045",
    "clienteId": "CLI-00188",
    "valorTotal": 8081600,
    "modalidadPago": "parcial",
    "fechaLimiteSaldo": "2026-11-30",
    "totalPagado": 0,
    "saldoPendiente": 8081600,
    "estado": "pendiente_pago",
    "fechaCreacion": "2026-11-05T11:05:00-05:00"
  },
  "success": true
}

````

- [ ] Si la cotización ya tiene una orden, el backend retorna:

```json
{
  "message": "La cotización ya tiene una orden de venta",
  "data": {
    "ventaId": "VEN-00012",
    "cotizacionId": "COT-00045"
  },
  "success": false
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La cotización COT-00045 está aceptada y no tiene orden.
- **Acción:** Ejecutar el endpoint POST /api/v1/ventas con cotizacionId COT-00045, modalidad parcial y fecha límite 2026-11-30.
- **Resultado esperado:**

  - Código HTTP 201 Created
  - Campo success = true
  - Campo data.estado = "pendiente_pago" y data.saldoPendiente = 8081600
  - Campo message contiene el texto: "Orden de venta generada exitosamente"

### ✅ Caso 2:

- **Precondición:** La cotización COT-00045 ya tiene la orden VEN-00012.
- **Acción:** Ejecutar de nuevo el endpoint con cotizacionId COT-00045.
- **Resultado esperado:**

  - Código HTTP 409 Conflict
  - No se crea una nueva orden
  - Campo success = false
  - Campo data.ventaId contiene la orden existente
  - Campo message contiene el texto: "La cotización ya tiene una orden de venta"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "ventaId" (texto)
  - "cotizacionId" (texto)
  - "clienteId" (texto)
  - "valorTotal" (número)
  - "modalidadPago" (texto)
  - "fechaLimiteSaldo" (fecha ISO 8601)
  - "totalPagado" (número)
  - "saldoPendiente" (número)
  - "estado" (texto)
  - "fechaCreacion" (fecha ISO 8601)
  - "message" (texto)
  - "success" (booleano)

### ❌ Caso 4: 

- **Precondición:** La cotización COT-00046 fue rechazada, o se envía modalidad parcial sin fecha límite.
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

- [ ] El endpoint genera la orden de venta a partir de una cotización aceptada.
- [ ] La orden conserva los precios de la cotización y su modalidad de pago.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar el estado de la cotización, la duplicidad y la modalidad de pago.
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
