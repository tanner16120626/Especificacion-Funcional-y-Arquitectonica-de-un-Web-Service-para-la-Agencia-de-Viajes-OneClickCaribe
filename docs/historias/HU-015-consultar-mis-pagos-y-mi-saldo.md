## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y he realizado uno o varios pagos a mi orden,
Para tener claro cuánto he pagado y cuánto me falta, con el detalle de cada pago,
Que el sistema me muestre los pagos de mi compra con el resultado de cada transacción y mi saldo pendiente.

## 🔁 Flujo Esperado

- El cliente realiza la consulta desde el portal web, que invoca el endpoint.
- El sistema consume el endpoint /api/v1/ventas/{ventaId}/pagos de `pagos.api` con el método GET.
- La capa API valida el token de acceso del cliente y delega el caso de uso a `ConsultarPagosService`.
- El servicio verifica que la orden exista y que pertenezca al cliente del token.
- El repositorio en memoria devuelve los pagos de la orden, incluidos los registrados con HU-013 y actualizados con HU-014 en la misma sesión, y el dominio calcula el saldo.
- Se reciben o consultan los campos:
- ventaId / Identificador de la orden (parámetro de ruta)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint GET que recibe el ventaId como parámetro de ruta.
- [x] Se listan los pagos de la orden en orden de fecha, con pagoId, fecha, medio, monto y estado: `aprobado`, `pendiente` o `rechazado`; nunca se muestran los datos de pago ni los de la tarjeta.
- [x] totalAprobado suma solo los pagos aprobados y el saldo es el valor de la orden menos esos pagos (RN-45); un pago PSE pendiente aparece en la lista sin descontarse del saldo.
- [x] Si la orden no tiene pagos, responde 200 con la lista vacía, el saldo igual al valor de la orden y el mensaje "La orden no tiene pagos registrados".
- [x] Si la orden no existe, se responde 404 con el mensaje "La orden de venta no existe".
- [x] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`. Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido responde 401 con "La sesión expiró. Inicie sesión nuevamente".
- [x] El cliente solo consulta los pagos de sus propias órdenes; si la orden pertenece a otro cliente, o la cuenta no tiene rol cliente, responde 403 con el mensaje "No tiene permisos para realizar esta acción".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (VEN-00012 después del abono PAG-00021 registrado con HU-013; fechaPago corresponde a la fecha y hora en que se procesó cada pago):

```json
{
  "success": true,
  "data": {
    "ventaId": "VEN-00012",
    "valorTotal": 8081600,
    "totalAprobado": 5000000,
    "saldoPendiente": 3081600,
    "pagos": [
      {
        "pagoId": "PAG-00021",
        "fechaPago": "2026-11-11T10:15:00-05:00",
        "medioPago": "tarjeta_credito",
        "monto": 5000000,
        "estado": "aprobado"
      }
    ]
  },
  "message": "Pagos consultados exitosamente"
}
```

- [x] Si la orden no tiene pagos, el backend retorna:

```json
{
  "success": true,
  "data": {
    "ventaId": "VEN-00013",
    "valorTotal": 3150000,
    "totalAprobado": 0,
    "saldoPendiente": 3150000,
    "pagos": []
  },
  "message": "La orden no tiene pagos registrados"
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Consultar mis pagos y mi saldo

- **Método HTTP:** `GET`
- **Ruta:** `/api/v1/ventas/{ventaId}/pagos`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "success": true,
  "data": {
    "ventaId": "VEN-00012",
    "valorTotal": 8081600,
    "totalAprobado": 5000000,
    "saldoPendiente": 3081600,
    "pagos": [
      {
        "pagoId": "PAG-00021",
        "fechaPago": "2026-11-11T10:15:00-05:00",
        "medioPago": "tarjeta_credito",
        "monto": 5000000,
        "estado": "aprobado"
      },
      {
        "pagoId": "PAG-00022",
        "fechaPago": "2026-11-11T10:20:00-05:00",
        "medioPago": "pse",
        "monto": 3081600,
        "estado": "pendiente"
      }
    ]
  },
  "message": "Pagos consultados exitosamente"
}

````

- [x] Cuando la pasarela aprueba el PSE PAG-00022 con HU-014, el backend retorna:

```json
{
  "success": true,
  "data": {
    "ventaId": "VEN-00012",
    "valorTotal": 8081600,
    "totalAprobado": 8081600,
    "saldoPendiente": 0,
    "pagos": [
      {
        "pagoId": "PAG-00021",
        "fechaPago": "2026-11-11T10:15:00-05:00",
        "medioPago": "tarjeta_credito",
        "monto": 5000000,
        "estado": "aprobado"
      },
      {
        "pagoId": "PAG-00022",
        "fechaPago": "2026-11-11T10:20:00-05:00",
        "medioPago": "pse",
        "monto": 3081600,
        "estado": "aprobado"
      }
    ]
  },
  "message": "Pagos consultados exitosamente"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La cliente CLI-00188 (registrada con HU-001) inició sesión con HU-002 y la orden VEN-00012 tiene un pago aprobado de 5.000.000 (PAG-00021, registrado con HU-013).
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00012/pagos con su token.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.pagos contiene el pago con estado "aprobado" y data.saldoPendiente = 3081600
  - Campo message contiene el texto: "Pagos consultados exitosamente"

### ✅ Caso 2:

- **Precondición:** La orden precargada VEN-00013 no tiene pagos.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00013/pagos.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo data.pagos es una lista vacía y data.saldoPendiente = data.valorTotal
  - Campo message contiene el texto: "La orden no tiene pagos registrados"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "ventaId" (texto)
    - "valorTotal" (número)
    - "totalAprobado" (número)
    - "saldoPendiente" (número)
    - "pagos" (lista), donde cada pago tiene:
      - "pagoId" (texto)
      - "fechaPago" (fecha ISO 8601)
      - "medioPago" (texto)
      - "monto" (número)
      - "estado" (texto)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** El repositorio no contiene la orden VEN-09999.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-09999/pagos.
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
  - Campo message contiene el texto: "No fue posible consultar los pagos"

## ✅ Definición de Hecho

# Historia: Consultar mis pagos y mi saldo

## 📦 Alcance Funcional

- [x] El endpoint devuelve los pagos de la orden y su saldo.
- [x] El saldo coincide con el valor de la orden menos los pagos aprobados.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar la suma de pagos y el saldo.
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
