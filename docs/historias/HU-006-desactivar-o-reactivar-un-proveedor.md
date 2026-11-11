## 📖 Historia de Usuario

Dado que soy administradora de One Click Caribe y la agencia deja de trabajar con un proveedor, o retoma la relación con él,
Para que sus servicios dejen de ofrecerse en el portal, o vuelvan a ofrecerse, sin perder su historial,
Que el sistema me permita cambiar el estado del proveedor entre activo e inactivo, indicando el motivo.

## 🔁 Flujo Esperado

- La administradora diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/proveedores/{proveedorId}/estado de `proveedores.api` con el método PATCH.
- La capa API valida el formato del JSON y delega el caso de uso a `CambiarEstadoProveedorService`.
- El dominio valida que el nuevo estado sea distinto del actual y que el motivo esté informado.
- El proveedor no se elimina: cambia de estado y conserva su historial.
- Un proveedor inactivo deja de aparecer en el catálogo y en las cotizaciones nuevas (RN-13); las cotizaciones ya emitidas conservan su precio (RN-34).
- Se reciben o consultan los campos:
- proveedorId / Identificador del proveedor (parámetro de ruta)
- estado / `activo` o `inactivo`
- motivo / Motivo del cambio de estado


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint PATCH que recibe en el cuerpo JSON los campos estado y motivo.
- [ ] El proveedor nunca se elimina; solo cambia entre `activo` e `inactivo`.
- [ ] El nuevo estado debe ser distinto del actual y el motivo es obligatorio.
- [ ] Un proveedor inactivo no se ofrece en el catálogo ni en cotizaciones nuevas (RN-13).
- [ ] El endpoint exige un token con rol `administradora`; un token de otro rol responde 403 y la ausencia de token, 401.
- [ ] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Proveedor desactivado exitosamente",
  "data": {
    "proveedorId": "PRV-0021",
    "razonSocial": "PriceTravel Colombia S.A.S.",
    "estado": "inactivo",
    "motivo": "Fin del convenio comercial",
    "fechaCambioEstado": "2026-11-05T10:15:00-05:00"
  },
  "success": true
}
```

- [ ] Si el proveedor se reactiva, el backend retorna:

```json
{
  "message": "Proveedor reactivado exitosamente",
  "data": {
    "proveedorId": "PRV-0021",
    "razonSocial": "PriceTravel Colombia S.A.S.",
    "estado": "activo",
    "motivo": "Renovación del convenio",
    "fechaCambioEstado": "2026-11-20T09:00:00-05:00"
  },
  "success": true
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
  "message": "Proveedor desactivado exitosamente",
  "data": {
    "proveedorId": "PRV-0021",
    "razonSocial": "PriceTravel Colombia S.A.S.",
    "estado": "inactivo",
    "motivo": "Fin del convenio comercial",
    "fechaCambioEstado": "2026-11-05T10:15:00-05:00"
  },
  "success": true
}

````

- [ ] Si el proveedor se reactiva, el backend retorna:

```json
{
  "message": "Proveedor reactivado exitosamente",
  "data": {
    "proveedorId": "PRV-0021",
    "razonSocial": "PriceTravel Colombia S.A.S.",
    "estado": "activo",
    "motivo": "Renovación del convenio",
    "fechaCambioEstado": "2026-11-20T09:00:00-05:00"
  },
  "success": true
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** El proveedor PRV-0021 está activo.
- **Acción:** Ejecutar el endpoint PATCH /api/v1/proveedores/PRV-0021/estado con estado "inactivo" y un motivo.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.estado = "inactivo"
  - El proveedor deja de aparecer en GET /api/v1/catalogo/servicios
  - Campo message contiene el texto: "Proveedor desactivado exitosamente"

### ✅ Caso 2:

- **Precondición:** El proveedor PRV-0021 está inactivo.
- **Acción:** Ejecutar el endpoint con estado "activo" y un motivo.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo data.estado = "activo"
  - Campo message contiene el texto: "Proveedor reactivado exitosamente"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "proveedorId" (texto)
  - "razonSocial" (texto)
  - "estado" (texto)
  - "motivo" (texto)
  - "fechaCambioEstado" (fecha ISO 8601)
  - "message" (texto)
  - "success" (booleano)

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

- [ ] El endpoint cambia el estado del proveedor sin eliminarlo.
- [ ] Los proveedores inactivos dejan de ofrecerse en el catálogo.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar el cambio de estado, el motivo obligatorio y el filtro del catálogo.
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
