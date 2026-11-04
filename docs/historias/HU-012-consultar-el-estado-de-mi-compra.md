## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y ya tengo una orden de venta,
Para saber en qué va mi compra: cuánto he pagado, cuánto debo y si mi reserva y mi factura están listas,
Que el sistema me muestre el estado completo de mi compra en una sola consulta.

## 🔁 Flujo Esperado

- El cliente realiza la consulta desde el portal web, que invoca el endpoint.
- El sistema consume el endpoint /api/v1/ventas/{ventaId} de `ventas.api` con el método GET.
- La capa API valida el formato del JSON y delega el caso de uso a `ConsultarOrdenService`.
- El repositorio en memoria busca la orden por su identificador.
- El servicio reúne el total pagado, el saldo y si la reserva y la factura ya fueron generadas.
- Se reciben o consultan los campos:
- ventaId / Identificador de la orden (parámetro de ruta)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint GET que recibe el ventaId como parámetro de ruta.
- [ ] Se informa el estado de la orden: `pendiente_pago`, `pago_parcial` o `pagada`; el total pagado solo incluye pagos aprobados por la pasarela (RN-45).
- [ ] Se informa si la reserva está confirmada y si la factura está generada.
- [ ] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`; sin token, o con el token vencido, responde 401.
- [ ] El cliente solo accede a sus propios recursos; si el recurso pertenece a otro cliente, responde 403.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Orden consultada exitosamente",
  "data": {
    "ventaId": "VEN-00012",
    "clienteId": "CLI-00188",
    "valorTotal": 8081600,
    "totalPagado": 5000000,
    "saldoPendiente": 3081600,
    "estado": "pago_parcial",
    "reservaConfirmada": false,
    "facturaGenerada": false
  },
  "success": true
}
```

- [ ] Si la orden ya está pagada, el backend retorna:

```json
{
  "message": "Orden consultada exitosamente",
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
  "success": true
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
  "message": "Orden consultada exitosamente",
  "data": {
    "ventaId": "VEN-00012",
    "clienteId": "CLI-00188",
    "valorTotal": 8081600,
    "totalPagado": 5000000,
    "saldoPendiente": 3081600,
    "estado": "pago_parcial",
    "reservaConfirmada": false,
    "facturaGenerada": false
  },
  "success": true
}

````

- [ ] Si la orden ya está pagada, el backend retorna:

```json
{
  "message": "Orden consultada exitosamente",
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
  "success": true
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La orden VEN-00012 tiene un abono de 5.000.000.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00012.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.estado = "pago_parcial" y data.saldoPendiente = 3081600
  - Campo message contiene el texto: "Orden consultada exitosamente"

### ✅ Caso 2:

- **Precondición:** La orden VEN-00010 está pagada en su totalidad.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00010.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo data.estado = "pagada"
  - Campo data.reservaConfirmada = true y data.facturaGenerada = true

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "ventaId" (texto)
  - "clienteId" (texto)
  - "valorTotal" (número)
  - "totalPagado" (número)
  - "saldoPendiente" (número)
  - "estado" (texto)
  - "reservaConfirmada" (booleano)
  - "facturaGenerada" (booleano)
  - "message" (texto)
  - "success" (booleano)

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

- [ ] El endpoint devuelve el estado completo de la orden.
- [ ] El saldo pendiente se calcula con los pagos registrados.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar el cálculo del saldo y el estado de la orden.
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
