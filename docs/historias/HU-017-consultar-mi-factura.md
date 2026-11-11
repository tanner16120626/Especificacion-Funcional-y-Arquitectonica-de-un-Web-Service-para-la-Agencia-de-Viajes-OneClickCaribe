## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y ya pagué mi orden en su totalidad,
Para tener el soporte fiscal de mi compra,
Que el sistema me muestre la factura generada automáticamente para mi orden.

## 🔁 Flujo Esperado

- El cliente realiza la consulta desde el portal web, que invoca el endpoint.
- El sistema consume el endpoint /api/v1/ventas/{ventaId}/factura de `facturacion.api` con el método GET.
- La capa API valida el formato del JSON y delega el caso de uso a `ConsultarFacturaService`.
- El servicio verifica que la orden exista y esté pagada (RN-53).
- El repositorio en memoria devuelve la factura emitida a nombre del cliente titular (RN-57), con un CUFE simulado porque la integración con la DIAN no está disponible (RN-51).
- Se reciben o consultan los campos:
- ventaId / Identificador de la orden (parámetro de ruta)


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint GET que recibe el ventaId como parámetro de ruta.
- [ ] La factura solo existe para órdenes pagadas en su totalidad (RN-53).
- [ ] La factura está a nombre del cliente titular (RN-57) y no se elimina (RN-56).
- [ ] El CUFE se genera de forma simulada (RN-51).
- [ ] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`; sin token, o con el token vencido, responde 401.
- [ ] El cliente solo accede a sus propios recursos; si el recurso pertenece a otro cliente, responde 403.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Factura consultada exitosamente",
  "data": {
    "facturaId": "FAC-00006",
    "numeroFactura": "OCC-2026-00006",
    "cufe": "SIM-8f3a2c91d7e4",
    "ventaId": "VEN-00010",
    "documentoCliente": "1098765432",
    "nombreCliente": "María Fernanda Rojas Díaz",
    "valorTotal": 8081600,
    "fechaEmision": "2026-11-05T11:30:00-05:00",
    "estado": "emitida"
  },
  "success": true
}
```

- [ ] Si la orden aún no está pagada, el backend retorna:

```json
{
  "message": "La factura se genera cuando la orden esté pagada en su totalidad",
  "data": null,
  "success": false
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
  "message": "Factura consultada exitosamente",
  "data": {
    "facturaId": "FAC-00006",
    "numeroFactura": "OCC-2026-00006",
    "cufe": "SIM-8f3a2c91d7e4",
    "ventaId": "VEN-00010",
    "documentoCliente": "1098765432",
    "nombreCliente": "María Fernanda Rojas Díaz",
    "valorTotal": 8081600,
    "fechaEmision": "2026-11-05T11:30:00-05:00",
    "estado": "emitida"
  },
  "success": true
}

````

- [ ] Si la orden aún no está pagada, el backend retorna:

```json
{
  "message": "La factura se genera cuando la orden esté pagada en su totalidad",
  "data": null,
  "success": false
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La orden VEN-00010 está pagada y su factura fue generada.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00010/factura.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.nombreCliente corresponde al cliente titular
  - Campo message contiene el texto: "Factura consultada exitosamente"

### ✅ Caso 2:

- **Precondición:** La orden VEN-00012 tiene saldo pendiente.
- **Acción:** Ejecutar el endpoint GET /api/v1/ventas/VEN-00012/factura.
- **Resultado esperado:**

  - Código HTTP 409 Conflict
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La factura se genera cuando la orden esté pagada en su totalidad"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

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
  - "success" (booleano)

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

- [ ] El endpoint devuelve la factura de una orden pagada.
- [ ] La factura está a nombre del cliente titular.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar el estado de pago de la orden y los datos de la factura.
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
