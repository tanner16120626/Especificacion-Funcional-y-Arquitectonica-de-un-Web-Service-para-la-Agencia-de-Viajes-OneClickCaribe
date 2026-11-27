## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y necesito apoyo personalizado sobre mi viaje ya comprado: una duda, el check-in o un servicio adicional,
Para recibir atención de un asesor sin perder el seguimiento de mi caso,
Que el sistema me permita registrar una consulta vinculada a mi orden.

## 🔁 Flujo Esperado

- El cliente diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/posventa/consultas de `posventa.api` con el método POST.
- La capa API valida el token de acceso del cliente y el formato del JSON, y delega el caso de uso a `RegistrarConsultaService`.
- El servicio verifica que la orden exista y que pertenezca al cliente del token, y vincula la consulta a ella (RN-83).
- El dominio valida la categoría: una consulta no modifica la venta (RN-81).
- La consulta queda abierta y sin fecha de vencimiento (RN-85), a la espera de la respuesta del asesor (HU-019).
- Se reciben o consultan los campos:
- ventaId / Identificador de la orden
- categoria / `equipaje`, `documentos`, `itinerario`, `check_in`, `servicios_adicionales` u `otro`
- descripcion / Detalle de la consulta


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint POST que recibe en el cuerpo JSON ventaId, categoria y descripcion.
- [x] La consulta queda vinculada a una orden existente (RN-83); si la orden no existe, responde 404 con el mensaje "La orden de venta no existe".
- [x] Solo se aceptan las categorías permitidas: `equipaje`, `documentos`, `itinerario`, `check_in`, `servicios_adicionales` u `otro`; cualquier otra responde 400 con el mensaje "La categoría de la consulta no es válida". Una consulta no modifica la venta (RN-81).
- [x] La descripción es obligatoria; si llega vacía, responde 400 con el mensaje "La descripción es obligatoria".
- [x] La consulta se crea en estado `abierta`, sin fecha de vencimiento (RN-85), y queda disponible para que el asesor la responda con HU-019.
- [x] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`. Sin token o con un token alterado responde 401 con "Token de acceso inválido o ausente"; con el token vencido responde 401 con "La sesión expiró. Inicie sesión nuevamente".
- [x] El cliente solo registra consultas sobre sus propias órdenes; si la orden pertenece a otro cliente, o la cuenta no tiene rol cliente, responde 403 con el mensaje "No tiene permisos para realizar esta acción".
- [x] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message; por ejemplo, "El identificador de la orden es obligatorio", "La categoría es obligatoria" o "El campo 'descripcion' debe ser un texto".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (consulta nueva de la orden VEN-00010; CON-00023 es el primer identificador libre después de las consultas precargadas CON-00019, CON-00021 y CON-00022, y fechaRegistro corresponde a la fecha y hora en que se registra la consulta):

```json
{
  "success": true,
  "data": {
    "consultaId": "CON-00023",
    "ventaId": "VEN-00010",
    "categoria": "equipaje",
    "descripcion": "¿Puedo llevar una maleta adicional de 23 kg en el vuelo de regreso?",
    "estado": "abierta",
    "fechaRegistro": "2026-11-11T10:50:00-05:00"
  },
  "message": "Consulta registrada exitosamente"
}
```

- [x] Si la orden no existe, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "La orden de venta no existe"
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Registrar una consulta posventa

- **Método HTTP:** `POST`
- **Ruta:** `/api/v1/posventa/consultas`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "success": true,
  "data": {
    "consultaId": "CON-00023",
    "ventaId": "VEN-00010",
    "categoria": "equipaje",
    "descripcion": "¿Puedo llevar una maleta adicional de 23 kg en el vuelo de regreso?",
    "estado": "abierta",
    "fechaRegistro": "2026-11-11T10:50:00-05:00"
  },
  "message": "Consulta registrada exitosamente"
}

````

- [x] Si la categoría no está permitida (por ejemplo "cambio_fecha"), el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "La categoría de la consulta no es válida"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La cliente CLI-00188 (registrada con HU-001) inició sesión con HU-002 y su orden precargada VEN-00010 existe.
- **Acción:** Ejecutar el endpoint POST /api/v1/posventa/consultas con su token, ventaId VEN-00010, categoría equipaje y una descripción.
- **Resultado esperado:**

  - Código HTTP 201 Created
  - Campo success = true
  - Campo data.consultaId = "CON-00023" y data.estado = "abierta"
  - Campo message contiene el texto: "Consulta registrada exitosamente"

### ✅ Caso 2:

- **Precondición:** La orden VEN-09999 no existe.
- **Acción:** Ejecutar el endpoint POST /api/v1/posventa/consultas con ventaId VEN-09999.
- **Resultado esperado:**

  - Código HTTP 404 Not Found
  - No se crea la consulta
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La orden de venta no existe"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "consultaId" (texto)
    - "ventaId" (texto)
    - "categoria" (texto)
    - "descripcion" (texto)
    - "estado" (texto)
    - "fechaRegistro" (fecha ISO 8601)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** El cliente envía la categoría "cambio_fecha", o una descripción vacía.
- **Acción:** Ejecutar el endpoint con cada uno de esos datos inválidos.
- **Resultado esperado:**

  - Código HTTP 400 Bad Request
  - No se crea la consulta
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La categoría de la consulta no es válida" o "La descripción es obligatoria", según el caso

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible registrar la consulta"

## ✅ Definición de Hecho

# Historia: Registrar una consulta posventa

## 📦 Alcance Funcional

- [x] El endpoint registra la consulta posventa vinculada a la orden.
- [x] Las categorías que implican cambios de la venta se rechazan.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar la vinculación con la orden y la categoría.
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
