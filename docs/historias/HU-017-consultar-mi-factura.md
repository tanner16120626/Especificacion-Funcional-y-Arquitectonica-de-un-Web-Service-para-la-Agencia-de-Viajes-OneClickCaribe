## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y ya pagué mi orden en su totalidad,
Para tener el soporte fiscal de mi compra,
Que el sistema me muestre la factura generada automáticamente para mi orden.

## 🔁 Flujo Esperado

- El cliente realiza la consulta desde el portal web, que invoca el endpoint.
- El sistema consume el endpoint /api/v1/ventas/{ventaId}/factura de `facturacion.api` con el método GET.
- La capa API valida el token de acceso del cliente y delega el caso de uso a `ConsultarFacturaService`.
- El servicio verifica que la orden exista, que pertenezca al cliente del token y que esté pagada (RN-53).
- El repositorio en memoria devuelve la factura generada automáticamente cuando un pago aprobado dejó el saldo en cero (HU-013 o HU-014), emitida a nombre del cliente titular (RN-57), con un CUFE simulado porque la integración con la DIAN no está disponible (RN-51).
- Se reciben o consultan los campos:
- ventaId / Identificador de la orden (parámetro de ruta)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint GET que recibe el ventaId como parámetro de ruta.
- [x] La factura solo existe para órdenes pagadas en su totalidad (RN-53); si la orden aún no está pagada, responde 409 con el mensaje "La factura se genera cuando la orden esté pagada en su totalidad".
- [x] La factura está a nombre del cliente titular, con su documento y su nombre (RN-57), y no se elimina (RN-56).
- [x] El CUFE se genera de forma simulada (RN-51).
- [x] La factura generada al pagar una orden con HU-013 o HU-014 se puede consultar en la misma sesión.
- [x] Si la orden no existe, se responde 404 con el mensaje "La orden de venta no existe".
- [x] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`. Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido responde 401 con "La sesión expiró. Inicie sesión nuevamente".
- [x] El cliente solo consulta las facturas de sus propias órdenes; si la orden pertenece a otro cliente, o la cuenta no tiene rol cliente, responde 403 con el mensaje "No tiene permisos para realizar esta acción".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (factura precargada FAC-00006 de la orden VEN-00010):

```json
{
  "success": true,
  "data": {
    "facturaId": "FAC-00006",
    "numeroFactura": "OCC-2026-00006",
    "cufe": "SIM-8f3a2c91d7e4",
    "ventaId": "VEN-00010",
    "documentoCliente": "1098765432",
    "nombreCliente": "María Fernanda Rojas Díaz",
    "valorTotal": 8081600,
    "fechaEmision": "2026-11-02T10:00:05-05:00",
    "estado": "emitida"
  },
  "message": "Factura consultada exitosamente"
}
```

- [x] Si la orden aún no está pagada, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "La factura se genera cuando la orden esté pagada en su totalidad"
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Consultar mi factura

- **Método HTTP:** `GET`
- **Ruta:** `/api/v1/ventas/{ventaId}/factura`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "success": true,
  "data": {
    "facturaId": "FAC-00006",
    "numeroFactura": "OCC-2026-00006",
    "cufe": "SIM-8f3a2c91d7e4",
    "ventaId": "VEN-00010",
    "documentoCliente": "1098765432",
    "nombreCliente": "María Fernanda Rojas Díaz",
    "valorTotal": 8081600,
    "fechaEmision": "2026-11-02T10:00:05-05:00",
    "estado": "emitida"
  },
  "message": "Factura consultada exitosamente"
}

````

- [x] Si la factura se genera en la misma sesión al pagar la orden VEN-00014 con HU-013, el backend retorna (fechaEmision corresponde a la fecha y hora del pago que dejó el saldo en cero; FAC-00007 es el primer identificador libre, el número de factura lleva el año de emisión y el CUFE simulado se calcula con la factura, la orden y la fecha de emisión, por lo que cambia con la hora del pago):

```json
{
  "success": true,
  "data": {
    "facturaId": "FAC-00007",
    "numeroFactura": "OCC-2026-00007",
    "cufe": "SIM-af8d092fdffb",
    "ventaId": "VEN-00014",
    "documentoCliente": "1098765432",
    "nombreCliente": "María Fernanda Rojas Díaz",
    "valorTotal": 8081600,
    "fechaEmision": "2026-11-11T10:45:00-05:00",
    "estado": "emitida"
  },
  "message": "Factura consultada exitosamente"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La cliente CLI-00188 (registrada con HU-001) inició sesión con HU-002 y su orden precargada VEN-00010 está pagada, con la factura FAC-00006 emitida.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00010/factura con su token.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.nombreCliente corresponde al cliente titular
  - Campo message contiene el texto: "Factura consultada exitosamente"

### ✅ Caso 2:

- **Precondición:** La orden precargada VEN-00013 tiene saldo pendiente.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00013/factura.
- **Resultado esperado:**

  - Código HTTP 409 Conflict
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La factura se genera cuando la orden esté pagada en su totalidad"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "facturaId" (texto)
    - "numeroFactura" (texto)
    - "cufe" (texto)
    - "ventaId" (texto)
    - "documentoCliente" (texto)
    - "nombreCliente" (texto)
    - "valorTotal" (número)
    - "fechaEmision" (fecha ISO 8601)
    - "estado" (texto)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** El repositorio no contiene la orden VEN-09999.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-09999/factura.
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
  - Campo message contiene el texto: "No fue posible consultar la factura"

## ✅ Definición de Hecho

# Historia: Consultar mi factura

## 📦 Alcance Funcional

- [x] El endpoint devuelve la factura de una orden pagada.
- [x] La factura está a nombre del cliente titular.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar el estado de pago de la orden y los datos de la factura.
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
