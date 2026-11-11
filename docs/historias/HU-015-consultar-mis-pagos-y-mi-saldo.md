## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y he realizado uno o varios pagos a mi orden,
Para tener claro cuánto he pagado y cuánto me falta, con el detalle de cada pago,
Que el sistema me muestre los pagos de mi compra con el resultado de cada transacción y mi saldo pendiente.

## 🔁 Flujo Esperado

- El cliente realiza la consulta desde el portal web, que invoca el endpoint.
- El sistema consume el endpoint /api/v1/ventas/{ventaId}/pagos de `pagos.api` con el método GET.
- La capa API valida el formato del JSON y delega el caso de uso a `ConsultarPagosService`.
- El servicio verifica que la orden exista.
- El repositorio en memoria devuelve los pagos de la orden y el dominio calcula el saldo.
- Se reciben o consultan los campos:
- ventaId / Identificador de la orden (parámetro de ruta)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint GET que recibe el ventaId como parámetro de ruta.
- [ ] Se listan los pagos de la orden con fecha, medio, monto y estado: `aprobado`, `pendiente` o `rechazado`.
- [ ] El saldo es el valor de la orden menos los pagos aprobados (RN-45).
- [ ] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`; sin token, o con el token vencido, responde 401.
- [ ] El cliente solo accede a sus propios recursos; si el recurso pertenece a otro cliente, responde 403.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Pagos consultados exitosamente",
  "data": {
    "ventaId": "VEN-00012",
    "valorTotal": 8081600,
    "totalAprobado": 5000000,
    "saldoPendiente": 3081600,
    "pagos": [
      {
        "pagoId": "PAG-00031",
        "fechaPago": "2026-11-05T10:15:00-05:00",
        "medioPago": "tarjeta_credito",
        "monto": 5000000,
        "estado": "aprobado"
      }
    ]
  },
  "success": true
}
```

- [ ] Si la orden no tiene pagos, el backend retorna:

```json
{
  "message": "La orden no tiene pagos registrados",
  "data": {
    "ventaId": "VEN-00013",
    "valorTotal": 3150000,
    "totalAprobado": 0,
    "saldoPendiente": 3150000,
    "pagos": []
  },
  "success": true
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
  "message": "Pagos consultados exitosamente",
  "data": {
    "ventaId": "VEN-00012",
    "valorTotal": 8081600,
    "totalAprobado": 5000000,
    "saldoPendiente": 3081600,
    "pagos": [
      {
        "pagoId": "PAG-00031",
        "fechaPago": "2026-11-05T10:15:00-05:00",
        "medioPago": "tarjeta_credito",
        "monto": 5000000,
        "estado": "aprobado"
      }
    ]
  },
  "success": true
}

````

- [ ] Si la orden no tiene pagos, el backend retorna:

```json
{
  "message": "La orden no tiene pagos registrados",
  "data": {
    "ventaId": "VEN-00013",
    "valorTotal": 3150000,
    "totalAprobado": 0,
    "saldoPendiente": 3150000,
    "pagos": []
  },
  "success": true
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La orden VEN-00012 tiene un pago aprobado de 5.000.000.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00012/pagos.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.pagos contiene el pago con estado "aprobado" y data.saldoPendiente = 3081600
  - Campo message contiene el texto: "Pagos consultados exitosamente"

### ✅ Caso 2:

- **Precondición:** La orden VEN-00013 no tiene pagos.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00013/pagos.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo data.pagos es una lista vacía y data.saldoPendiente = data.valorTotal
  - Campo message contiene el texto: "La orden no tiene pagos registrados"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "ventaId" (texto)
  - "valorTotal" (número)
  - "totalAprobado" (número)
  - "saldoPendiente" (número)
  - "pagos" (lista)
  - "message" (texto)
  - "success" (booleano)

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

- [ ] El endpoint devuelve los pagos de la orden y su saldo.
- [ ] El saldo coincide con el valor de la orden menos los pagos.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar la suma de pagos y el saldo.
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
