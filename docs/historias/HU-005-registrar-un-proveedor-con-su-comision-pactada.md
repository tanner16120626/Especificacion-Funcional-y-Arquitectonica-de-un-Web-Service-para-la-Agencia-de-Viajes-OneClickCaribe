## 📖 Historia de Usuario

Dado que soy administradora de One Click Caribe y la agencia empieza a trabajar con un nuevo proveedor,
Para que sus servicios aparezcan en el portal y las cotizaciones automáticas usen la comisión pactada con él,
Que el sistema me permita registrar el proveedor con su NIT, razón social, tipo, comisión pactada, servicios y destinos.

## 🔁 Flujo Esperado

- La administradora diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/proveedores de `proveedores.api` con el método POST.
- La capa API valida el token de acceso de la administradora y el formato del JSON, y delega el caso de uso a `RegistrarProveedorService`.
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

- [x] Se expone un endpoint POST que recibe en el cuerpo JSON nit, razonSocial, tipoProveedor, porcentajeComision, servicios y destinos.
- [x] Se valida que porcentajeComision esté entre 0 y 100; para tipoProveedor `aerolinea` debe ser 0, porque el tiquete aéreo se vende al valor neto (RN-22).
- [x] Se valida que el NIT no esté registrado previamente.
- [x] El proveedor se crea en estado `activo` (RN-13).
- [x] El endpoint exige un token con rol `administradora`. Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido, 401 con "La sesión expiró. Inicie sesión nuevamente"; con un token de otro rol, 403 con "No tiene permisos para realizar esta acción".
- [x] Los errores de formato del JSON se responden con código 400 y la estructura success, data y message. Mensajes exactos: campos obligatorios, "El NIT es obligatorio", "La razón social es obligatoria", "El tipo de proveedor es obligatorio" y "La comisión pactada es obligatoria"; tipo inválido, "El tipo de proveedor debe ser aerolinea, mayorista, hotel, aseguradora o transporte"; servicios vacíos, "Debe informar al menos un servicio"; destinos vacíos, "Debe informar al menos un destino"; porcentajeComision enviado como texto, "El campo 'porcentajeComision' debe ser un número".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (fechaRegistro corresponde a la fecha y hora del registro):

```json
{
  "success": true,
  "data": {
    "proveedorId": "PRV-0041",
    "nit": "900123456-7",
    "razonSocial": "Caribe Travel Mayorista S.A.S.",
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
    "fechaRegistro": "2026-11-11T10:15:00-05:00"
  },
  "message": "Proveedor registrado exitosamente"
}
```

- [x] Si el NIT ya está registrado, el backend retorna:

```json
{
  "success": false,
  "data": {
    "proveedorId": "PRV-0041",
    "nit": "900123456-7"
  },
  "message": "El proveedor ya se encuentra registrado"
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
  "success": true,
  "data": {
    "proveedorId": "PRV-0041",
    "nit": "900123456-7",
    "razonSocial": "Caribe Travel Mayorista S.A.S.",
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
    "fechaRegistro": "2026-11-11T10:15:00-05:00"
  },
  "message": "Proveedor registrado exitosamente"
}

````

- [x] Si el NIT ya está registrado, el backend retorna:

```json
{
  "success": false,
  "data": {
    "proveedorId": "PRV-0041",
    "nit": "900123456-7"
  },
  "message": "El proveedor ya se encuentra registrado"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La administradora inició sesión con HU-002 y el repositorio no contiene un proveedor con el NIT 900123456-7.
- **Acción:** Ejecutar el endpoint POST /api/v1/proveedores con tipo mayorista, comisión 12, servicios hospedaje y traslado, y destinos Cancún y Ciudad de México.
- **Resultado esperado:**

  - Código HTTP 201 Created
  - Campo success = true
  - Campo data.proveedorId = "PRV-0041" y data.estado = "activo"
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

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "proveedorId" (texto)
    - "nit" (texto)
    - "razonSocial" (texto)
    - "tipoProveedor" (texto)
    - "porcentajeComision" (número)
    - "servicios" (lista de textos)
    - "destinos" (lista de textos)
    - "estado" (texto)
    - "fechaRegistro" (fecha ISO 8601)
  - "message" (texto)

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

- [x] El endpoint registra el proveedor con su comisión pactada.
- [x] Se impide registrar dos proveedores con el mismo NIT y aerolíneas con comisión.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar la comisión pactada, la regla de aerolíneas y la duplicidad del NIT.
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
