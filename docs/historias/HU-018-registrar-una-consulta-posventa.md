## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y necesito apoyo personalizado sobre mi viaje ya comprado: una duda, el check-in o un servicio adicional,
Para recibir atención de un asesor sin perder el seguimiento de mi caso,
Que el sistema me permita registrar una consulta vinculada a mi orden.

## 🔁 Flujo Esperado

- El cliente diligencia el formulario del portal web, que envía la solicitud en JSON al endpoint.
- El sistema consume el endpoint /api/v1/posventa/consultas de `posventa.api` con el método POST.
- La capa API valida el formato del JSON y delega el caso de uso a `RegistrarConsultaService`.
- El servicio verifica que la orden exista y vincula la consulta a ella (RN-83).
- El dominio valida la categoría: una consulta no modifica la venta (RN-81).
- La consulta queda abierta y sin fecha de vencimiento (RN-85).
- Se reciben o consultan los campos:
- ventaId / Identificador de la orden
- categoria / `equipaje`, `documentos`, `itinerario`, `check_in`, `servicios_adicionales` u `otro`
- descripcion / Detalle de la consulta


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [ ] Se expone un endpoint POST que recibe en el cuerpo JSON ventaId, categoria y descripcion.
- [ ] La consulta queda vinculada a una orden existente (RN-83).
- [ ] Solo se aceptan las categorías permitidas; una consulta no modifica la venta (RN-81).
- [ ] La consulta se crea en estado `abierta`, sin fecha de vencimiento (RN-85).
- [ ] El endpoint exige el token de acceso en el encabezado `Authorization: Bearer`; sin token, o con el token vencido, responde 401.
- [ ] El cliente solo accede a sus propios recursos; si el recurso pertenece a otro cliente, responde 403.
- [ ] Los errores de formato del JSON (campos faltantes o tipos inválidos) se responden con código 400 y la estructura success, data y message.


### 2. 📆 Estructura de la información

- [ ] Se responde con la siguiente estructura en JSON:

```json
{
  "message": "Consulta registrada exitosamente",
  "data": {
    "consultaId": "CON-00021",
    "ventaId": "VEN-00010",
    "categoria": "equipaje",
    "descripcion": "¿Cuántas maletas puedo llevar en el vuelo?",
    "estado": "abierta",
    "fechaRegistro": "2026-11-06T08:45:00-05:00"
  },
  "success": true
}
```

- [ ] Si la orden no existe, el backend retorna:

```json
{
  "message": "La orden de venta no existe",
  "data": null,
  "success": false
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
  "message": "Consulta registrada exitosamente",
  "data": {
    "consultaId": "CON-00021",
    "ventaId": "VEN-00010",
    "categoria": "equipaje",
    "descripcion": "¿Cuántas maletas puedo llevar en el vuelo?",
    "estado": "abierta",
    "fechaRegistro": "2026-11-06T08:45:00-05:00"
  },
  "success": true
}

````

- [ ] Si la orden no existe, el backend retorna:

```json
{
  "message": "La orden de venta no existe",
  "data": null,
  "success": false
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** La orden VEN-00010 existe.
- **Acción:** Ejecutar el endpoint POST /api/v1/posventa/consultas con categoría equipaje y una descripción.
- **Resultado esperado:**

  - Código HTTP 201 Created
  - Campo success = true
  - Campo data.estado = "abierta"
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

  - "consultaId" (texto)
  - "ventaId" (texto)
  - "categoria" (texto)
  - "descripcion" (texto)
  - "estado" (texto)
  - "fechaRegistro" (fecha ISO 8601)
  - "message" (texto)
  - "success" (booleano)

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

- [ ] El endpoint registra la consulta posventa vinculada a la orden.
- [ ] Las categorías que implican cambios de la venta se rechazan.
- [ ] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [ ] Se ejecutaron pruebas unitarias para validar la vinculación con la orden y la categoría.
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
