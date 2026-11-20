## 📖 Historia de Usuario

Dado que soy administradora de One Click Caribe y la agencia deja de trabajar con un proveedor, o retoma la relación con él,
Para que sus servicios dejen de ofrecerse en el portal, o vuelvan a ofrecerse, sin perder su historial,
Que el sistema me permita cambiar el estado del proveedor entre activo e inactivo, indicando el motivo.

## 🔁 Flujo Esperado

- La administradora diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/proveedores/{proveedorId}/estado de `proveedores.api` con el método PATCH.
- La capa API valida el token de acceso de la administradora y el formato del JSON, y delega el caso de uso a `CambiarEstadoProveedorService`.
- El dominio valida que el nuevo estado sea distinto del actual y que el motivo esté informado.
- El proveedor no se elimina: cambia de estado y conserva su historial.
- El estado queda registrado en el repositorio; con él, el catálogo (HU-007) y las cotizaciones (HU-008) excluyen a los proveedores inactivos (RN-13), y las cotizaciones ya emitidas conservan su precio (RN-34).
- Se reciben o consultan los campos:
- proveedorId / Identificador del proveedor (parámetro de ruta)
- estado / `activo` o `inactivo`
- motivo / Motivo del cambio de estado


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint PATCH que recibe en el cuerpo JSON los campos estado y motivo.
- [x] El proveedor nunca se elimina; solo cambia entre `activo` e `inactivo`.
- [x] El nuevo estado debe ser distinto del actual y el motivo es obligatorio.
- [x] El estado queda registrado en el repositorio, que es el dato con el que el catálogo (HU-007) y las cotizaciones nuevas (HU-008) excluyen a los proveedores inactivos (RN-13).
- [x] El endpoint exige un token con rol `administradora`. Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido, 401 con "La sesión expiró. Inicie sesión nuevamente"; con un token de otro rol, 403 con "No tiene permisos para realizar esta acción".
- [x] Los errores de formato del JSON se responden con código 400 y la estructura success, data y message. Mensajes exactos: sin estado, "El estado es obligatorio"; estado distinto de activo o inactivo, "El estado debe ser activo o inactivo"; sin motivo o con motivo vacío, "El motivo es obligatorio".
- [x] Si el proveedor no existe, se responde 404 con el mensaje "El proveedor no se encuentra registrado".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (fechaCambioEstado corresponde a la fecha y hora del cambio de estado):

```json
{
  "success": true,
  "data": {
    "proveedorId": "PRV-0021",
    "razonSocial": "PriceTravel Colombia S.A.S.",
    "estado": "inactivo",
    "motivo": "Fin del convenio comercial",
    "fechaCambioEstado": "2026-11-11T10:15:00-05:00"
  },
  "message": "Proveedor desactivado exitosamente"
}
```

- [x] Si el proveedor se reactiva, el backend retorna:

```json
{
  "success": true,
  "data": {
    "proveedorId": "PRV-0021",
    "razonSocial": "PriceTravel Colombia S.A.S.",
    "estado": "activo",
    "motivo": "Renovación del convenio",
    "fechaCambioEstado": "2026-11-11T10:20:00-05:00"
  },
  "message": "Proveedor reactivado exitosamente"
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Desactivar o reactivar un proveedor

- **Método HTTP:** `PATCH`
- **Ruta:** `/api/v1/proveedores/{proveedorId}/estado`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "success": true,
  "data": {
    "proveedorId": "PRV-0021",
    "razonSocial": "PriceTravel Colombia S.A.S.",
    "estado": "inactivo",
    "motivo": "Fin del convenio comercial",
    "fechaCambioEstado": "2026-11-11T10:15:00-05:00"
  },
  "message": "Proveedor desactivado exitosamente"
}

````

- [x] Si el proveedor se reactiva, el backend retorna:

```json
{
  "success": true,
  "data": {
    "proveedorId": "PRV-0021",
    "razonSocial": "PriceTravel Colombia S.A.S.",
    "estado": "activo",
    "motivo": "Renovación del convenio",
    "fechaCambioEstado": "2026-11-11T10:20:00-05:00"
  },
  "message": "Proveedor reactivado exitosamente"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La administradora inició sesión con HU-002 y el proveedor PRV-0021 está activo.
- **Acción:** Ejecutar el endpoint PATCH /api/v1/proveedores/PRV-0021/estado con estado "inactivo" y un motivo.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.estado = "inactivo"
  - Campo data.proveedorId = "PRV-0021"
  - Campo message contiene el texto: "Proveedor desactivado exitosamente"

### ✅ Caso 2:

- **Precondición:** El proveedor PRV-0021 está inactivo.
- **Acción:** Ejecutar el endpoint PATCH /api/v1/proveedores/PRV-0021/estado con estado "activo" y un motivo.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo data.estado = "activo"
  - Campo message contiene el texto: "Proveedor reactivado exitosamente"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "proveedorId" (texto)
    - "razonSocial" (texto)
    - "estado" (texto)
    - "motivo" (texto)
    - "fechaCambioEstado" (fecha ISO 8601)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** Se envía el mismo estado que ya tiene el proveedor, o se omite el motivo.
- **Acción:** Ejecutar el endpoint con cada uno de esos casos.
- **Resultado esperado:**

  - Código HTTP 400 Bad Request
  - El estado del proveedor no cambia
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "El proveedor ya se encuentra en ese estado" o "El motivo es obligatorio", según el caso

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible cambiar el estado del proveedor"

## ✅ Definición de Hecho

# Historia: Desactivar o reactivar un proveedor

## 📦 Alcance Funcional

- [x] El endpoint cambia el estado del proveedor sin eliminarlo.
- [x] El estado del proveedor queda registrado para que el catálogo y las cotizaciones excluyan a los inactivos.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar el cambio de estado, el motivo obligatorio y el estado repetido.
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
