## 📖 Historia de Usuario

Dado que soy administradora de One Click Caribe y la agencia empieza a trabajar con un nuevo proveedor,
Para que sus servicios aparezcan en el portal y las cotizaciones automáticas usen la comisión pactada con él,
Que el sistema me permita registrar el proveedor con su NIT, razón social, tipo, comisión pactada, servicios y destinos.

## 🔁 Flujo Esperado

- La administradora diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/proveedores de `proveedores.api` con el método POST.
- La capa API valida el formato del JSON y delega el caso de uso a `RegistrarProveedorService`.
- El dominio valida que el porcentaje de comisión esté entre 0 y 100, y que las aerolíneas tengan comisión 0, porque el tiquete aéreo se vende al valor neto (RN-22).
- El repositorio en memoria verifica que el NIT no esté registrado.
- El proveedor queda activo; solo los proveedores activos se ofrecen en el portal (RN-13).
- Se reciben o consultan los campos:
- nit / NIT del proveedor
- razonSocial / Razón social
- tipoProveedor / `aerolinea`, `mayorista`, `hotel`, `aseguradora` o `transporte`
- porcentajeComision / Comisión pactada (0 a 100)
- servicios / Servicios que ofrece
- destinos / Destinos que atiende


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint POST que recibe en el cuerpo JSON nit, razonSocial, tipoProveedor, porcentajeComision, servicios y destinos.
- [ ] Se valida que porcentajeComision esté entre 0 y 100; para tipoProveedor `aerolinea` debe ser 0, porque el tiquete aéreo se vende al valor neto (RN-22).
- [ ] Se valida que el NIT no esté registrado previamente.
- [ ] El proveedor se crea en estado `activo` (RN-13).
- [ ] El endpoint exige un token con rol `administradora`; un token de otro rol responde 403 y la ausencia de token, 401.
- [ ] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Proveedor registrado exitosamente",
  "data": {
    "proveedorId": "PRV-0021",
    "nit": "900123456-7",
    "razonSocial": "PriceTravel Colombia S.A.S.",
    "tipoProveedor": "mayorista",
    "porcentajeComision": 12,
    "servicios": [
      "hospedaje",
      "traslado"
    ],
    "destinos": [
      "Cancún",
      "Ciudad de México"
    ],
    "estado": "activo",
    "fechaRegistro": "2026-11-05T10:15:00-05:00"
  },
  "success": true
}
```

- [ ] Si el NIT ya está registrado, el backend retorna:

```json
{
  "message": "El proveedor ya se encuentra registrado",
  "data": {
    "proveedorId": "PRV-0021",
    "nit": "900123456-7"
  },
  "success": false
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Registrar un proveedor con su comisión pactada

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/proveedores`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "message": "Proveedor registrado exitosamente",
  "data": {
    "proveedorId": "PRV-0021",
    "nit": "900123456-7",
    "razonSocial": "PriceTravel Colombia S.A.S.",
    "tipoProveedor": "mayorista",
    "porcentajeComision": 12,
    "servicios": [
      "hospedaje",
      "traslado"
    ],
    "destinos": [
      "Cancún",
      "Ciudad de México"
    ],
    "estado": "activo",
    "fechaRegistro": "2026-11-05T10:15:00-05:00"
  },
  "success": true
}

````

- [ ] Si el NIT ya está registrado, el backend retorna:

```json
{
  "message": "El proveedor ya se encuentra registrado",
  "data": {
    "proveedorId": "PRV-0021",
    "nit": "900123456-7"
  },
  "success": false
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** El repositorio no contiene un proveedor con el NIT 900123456-7.
- **Acción:** Ejecutar el endpoint POST /api/v1/proveedores con tipo mayorista, comisión 12, servicios hospedaje y traslado, y destinos Cancún y Ciudad de México.
- **Resultado esperado:**

  - Código HTTP 201 Created
  - Campo success = true
  - Campo data.estado = "activo"
  - Campo message contiene el texto: "Proveedor registrado exitosamente"

### ✅ Caso 2:

- **Precondición:** El repositorio ya contiene el proveedor con el NIT 900123456-7.
- **Acción:** Ejecutar el endpoint POST /api/v1/proveedores con el mismo NIT.
- **Resultado esperado:**

  - Código HTTP 409 Conflict
  - No se crea un nuevo proveedor
  - Campo success = false
  - Campo data.proveedorId contiene el proveedor existente
  - Campo message contiene el texto: "El proveedor ya se encuentra registrado"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "proveedorId" (texto)
  - "nit" (texto)
  - "razonSocial" (texto)
  - "tipoProveedor" (texto)
  - "porcentajeComision" (número)
  - "servicios" (lista)
  - "destinos" (lista)
  - "estado" (texto)
  - "fechaRegistro" (fecha ISO 8601)
  - "message" (texto)
  - "success" (booleano)

### ❌ Caso 4: 

- **Precondición:** La administradora envía una aerolínea con comisión 10, o una comisión de 150.
- **Acción:** Ejecutar el endpoint POST /api/v1/proveedores con cada uno de esos datos inválidos.
- **Resultado esperado:**

  - Código HTTP 400 Bad Request
  - No se crea el proveedor
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "Las aerolíneas se registran con comisión 0" o "La comisión debe estar entre 0 y 100", según el caso

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible registrar el proveedor"

## ✅ Definición de Hecho

# Historia: Registrar un proveedor con su comisión pactada

## 📦 Alcance Funcional

- [ ] El endpoint registra el proveedor con su comisión pactada.
- [ ] Se impide registrar dos proveedores con el mismo NIT y aerolíneas con comisión.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar la comisión pactada, la regla de aerolíneas y la duplicidad del NIT.
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
