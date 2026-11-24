## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y ya tengo una orden de venta,
Para saber en qué va mi compra: cuánto he pagado, cuánto debo y si mi reserva y mi factura están listas,
Que el sistema me muestre el estado completo de mi compra en una sola consulta.

## 🔁 Flujo Esperado

- El cliente realiza la consulta desde el portal web, que invoca el endpoint.
- El sistema consume el endpoint /api/v1/ventas/{ventaId} de `ventas.api` con el método GET.
- La capa API valida el token de acceso del cliente y delega el caso de uso a `ConsultarOrdenService`.
- El repositorio en memoria busca la orden por su identificador y el servicio verifica que pertenezca al cliente del token.
- El servicio reúne el total pagado, el saldo y si la reserva y la factura ya fueron generadas.
- Se reciben o consultan los campos:
- ventaId / Identificador de la orden (parámetro de ruta)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint GET que recibe el ventaId como parámetro de ruta.
- [x] Se informa el estado de la orden: `pendiente_pago`, `pago_parcial` o `pagada`; el total pagado solo incluye pagos aprobados por la pasarela (RN-45).
- [x] Se informa si la reserva está confirmada y si la factura está generada.
- [x] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`. Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido responde 401 con "La sesión expiró. Inicie sesión nuevamente".
- [x] El cliente solo consulta sus propias órdenes; si la orden pertenece a otro cliente, o la cuenta no tiene rol cliente, responde 403 con el mensaje "No tiene permisos para realizar esta acción".
- [x] Si la orden no existe, se responde 404 con el mensaje "La orden de venta no existe".
- [x] Una orden generada con HU-011 se puede consultar en la misma sesión.


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (VEN-00012 se muestra como queda al iniciar el servicio, sin abonos; cuando se registra un pago aprobado con HU-013, totalPagado y saldoPendiente cambian y el estado pasa a `pago_parcial` o `pagada`):

```json
{
  "success": true,
  "data": {
    "ventaId": "VEN-00012",
    "clienteId": "CLI-00188",
    "valorTotal": 8081600,
    "totalPagado": 0,
    "saldoPendiente": 8081600,
    "estado": "pendiente_pago",
    "reservaConfirmada": false,
    "facturaGenerada": false
  },
  "message": "Orden consultada exitosamente"
}
```

- [x] Si la orden ya está pagada, el backend retorna:

```json
{
  "success": true,
  "data": {
    "ventaId": "VEN-00010",
    "clienteId": "CLI-00188",
    "valorTotal": 8081600,
    "totalPagado": 8081600,
    "saldoPendiente": 0,
    "estado": "pagada",
    "reservaConfirmada": true,
    "facturaGenerada": true
  },
  "message": "Orden consultada exitosamente"
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Consultar el estado de mi compra

- **Método HTTP:** `GET`
- **Ruta:** `/api/v1/ventas/{ventaId}`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "success": true,
  "data": {
    "ventaId": "VEN-00012",
    "clienteId": "CLI-00188",
    "valorTotal": 8081600,
    "totalPagado": 0,
    "saldoPendiente": 8081600,
    "estado": "pendiente_pago",
    "reservaConfirmada": false,
    "facturaGenerada": false
  },
  "message": "Orden consultada exitosamente"
}

````

- [x] Si la orden ya está pagada, el backend retorna:

```json
{
  "success": true,
  "data": {
    "ventaId": "VEN-00010",
    "clienteId": "CLI-00188",
    "valorTotal": 8081600,
    "totalPagado": 8081600,
    "saldoPendiente": 0,
    "estado": "pagada",
    "reservaConfirmada": true,
    "facturaGenerada": true
  },
  "message": "Orden consultada exitosamente"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La cliente CLI-00188 (registrada con HU-001) inició sesión con HU-002 y su orden precargada VEN-00012 está pendiente de pago, sin abonos.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00012 con su token.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.estado = "pendiente_pago", data.totalPagado = 0 y data.saldoPendiente = 8081600
  - Campo message contiene el texto: "Orden consultada exitosamente"

### ✅ Caso 2:

- **Precondición:** La orden precargada VEN-00010 de la cliente CLI-00188 está pagada en su totalidad, con su reserva RES-00008 confirmada y su factura FAC-00006 emitida.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00010 con el token de la cliente.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo data.estado = "pagada" y data.saldoPendiente = 0
  - Campo data.reservaConfirmada = true y data.facturaGenerada = true
  - Campo message contiene el texto: "Orden consultada exitosamente"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "ventaId" (texto)
    - "clienteId" (texto)
    - "valorTotal" (número)
    - "totalPagado" (número)
    - "saldoPendiente" (número)
    - "estado" (texto)
    - "reservaConfirmada" (booleano)
    - "facturaGenerada" (booleano)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** El repositorio no contiene la orden VEN-09999.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-09999.
- **Resultado esperado:**

  - Código HTTP 404 Not Found
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La orden de venta no existe"

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible consultar la orden"

## ✅ Definición de Hecho

# Historia: Consultar el estado de mi compra

## 📦 Alcance Funcional

- [x] El endpoint devuelve el estado completo de la orden.
- [x] El saldo pendiente refleja los pagos aprobados registrados en la orden.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar el cálculo del saldo y el estado de la orden.
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
