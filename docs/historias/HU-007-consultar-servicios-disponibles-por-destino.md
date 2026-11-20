## 📖 Historia de Usuario

Dado que soy cliente de One Click Caribe y estoy pensando en un viaje,
Para conocer qué servicios y tarifas hay disponibles en mi destino y en mis fechas antes de cotizar,
Que el sistema me muestre los servicios disponibles por destino y fechas, con su tarifa vigente y su disponibilidad.

## 🔁 Flujo Esperado

- El cliente realiza la consulta desde el portal web, que invoca el endpoint.
- El sistema consume el endpoint /api/v1/catalogo/servicios de `proveedores.api` con el método GET.
- La capa API valida los parámetros de consulta y delega el caso de uso a `ConsultarCatalogoService`.
- El servicio considera solo proveedores activos (RN-13) y la tarifa vigente al momento de la consulta (RN-18).
- Los servicios sin cupo en las fechas se marcan como no disponibles (RN-20).
- Se reciben o consultan los campos:
- destino / Ciudad de destino (parámetro de consulta)
- fechaInicio / Fecha de inicio del viaje
- fechaFin / Fecha de fin del viaje


## ✅ Criterios de Aceptación

### 1. 🔍 Estructura y lógica del servicio

- [x] Se expone un endpoint GET que recibe destino, fechaInicio y fechaFin como parámetros de consulta.
- [x] Se valida que fechaFin no sea anterior a fechaInicio.
- [x] Solo se incluyen servicios de proveedores activos (RN-13), con la tarifa vigente al momento de la consulta (RN-18).
- [x] Los servicios sin cupo se devuelven con disponible = false (RN-20).
- [x] El catálogo es público: no requiere token, porque no expone datos personales.
- [x] Los parámetros destino, fechaInicio y fechaFin son obligatorios; si falta uno o una fecha no tiene el formato AAAA-MM-DD, se responde 400 con los mensajes "El campo 'destino' es obligatorio" o "El campo 'fechaInicio' debe ser una fecha con formato AAAA-MM-DD", según el caso. Un destino vacío o con solo espacios también responde 400 con el mensaje "El campo 'destino' es obligatorio".
- [x] Si no hay servicios de proveedores activos para el destino, se responde 404 con el mensaje "No hay servicios disponibles para el destino".


### 2. 📆 Estructura de la información

- [x] Se responde con la siguiente estructura en JSON (fechaHoraConsulta corresponde a la fecha y hora de la consulta):

```json
{
  "success": true,
  "data": {
    "destino": "Cancún",
    "fechaInicio": "2026-12-10",
    "fechaFin": "2026-12-15",
    "servicios": [
      {
        "servicioId": "SRV-001",
        "tipoServicio": "tiquete_aereo",
        "proveedor": "Avianca S.A.",
        "tarifaNetaAdulto": 1980000,
        "tarifaNetaMenor": 1782000,
        "disponible": true
      },
      {
        "servicioId": "SRV-002",
        "tipoServicio": "hospedaje",
        "proveedor": "PriceTravel Colombia S.A.S.",
        "tarifaNetaAdulto": 1450000,
        "tarifaNetaMenor": 725000,
        "disponible": true
      },
      {
        "servicioId": "SRV-003",
        "tipoServicio": "traslado",
        "proveedor": "PriceTravel Colombia S.A.S.",
        "tarifaNetaAdulto": 210000,
        "tarifaNetaMenor": 105000,
        "disponible": true
      },
      {
        "servicioId": "SRV-004",
        "tipoServicio": "asistencia_medica",
        "proveedor": "Assist1 Colombia S.A.S.",
        "tarifaNetaAdulto": 180000,
        "tarifaNetaMenor": 180000,
        "disponible": true
      }
    ],
    "fechaHoraConsulta": "2026-11-11T10:15:00-05:00"
  },
  "message": "Servicios consultados exitosamente"
}
```

- [x] Si no hay servicios para el destino, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "No hay servicios disponibles para el destino"
}
```

## 🔧 Notas Técnicas

## 🚀 Endpoint – Consultar servicios disponibles por destino

- **Método HTTP:** `GET`
- **Ruta:** `/api/v1/catalogo/servicios`

## 📤 Ejemplo de Respuesta JSON

````json

```json
{
  "success": true,
  "data": {
    "destino": "Cancún",
    "fechaInicio": "2026-12-10",
    "fechaFin": "2026-12-15",
    "servicios": [
      {
        "servicioId": "SRV-001",
        "tipoServicio": "tiquete_aereo",
        "proveedor": "Avianca S.A.",
        "tarifaNetaAdulto": 1980000,
        "tarifaNetaMenor": 1782000,
        "disponible": true
      },
      {
        "servicioId": "SRV-002",
        "tipoServicio": "hospedaje",
        "proveedor": "PriceTravel Colombia S.A.S.",
        "tarifaNetaAdulto": 1450000,
        "tarifaNetaMenor": 725000,
        "disponible": true
      },
      {
        "servicioId": "SRV-003",
        "tipoServicio": "traslado",
        "proveedor": "PriceTravel Colombia S.A.S.",
        "tarifaNetaAdulto": 210000,
        "tarifaNetaMenor": 105000,
        "disponible": true
      },
      {
        "servicioId": "SRV-004",
        "tipoServicio": "asistencia_medica",
        "proveedor": "Assist1 Colombia S.A.S.",
        "tarifaNetaAdulto": 180000,
        "tarifaNetaMenor": 180000,
        "disponible": true
      }
    ],
    "fechaHoraConsulta": "2026-11-11T10:15:00-05:00"
  },
  "message": "Servicios consultados exitosamente"
}

````

- [x] Si no hay servicios para el destino, el backend retorna:

```json
{
  "success": false,
  "data": null,
  "message": "No hay servicios disponibles para el destino"
}
```

## 🧪 Requisitos de Pruebas

## 🔍 Casos de Prueba Funcional

### ✅ Caso 1: 

- **Precondición:** El catálogo contiene servicios de proveedores activos para Cancún (SRV-001 a SRV-004).
- **Acción:** Ejecutar el endpoint GET /api/v1/catalogo/servicios?destino=Cancún&fechaInicio=2026-12-10&fechaFin=2026-12-15.
- **Resultado esperado:**

  - Código HTTP 200 OK
  - Campo success = true
  - Campo data.servicios contiene los servicios con su tarifa vigente
  - Campo message contiene el texto: "Servicios consultados exitosamente"

### ✅ Caso 2:

- **Precondición:** El catálogo no tiene servicios para el destino Tokio.
- **Acción:** Ejecutar el endpoint GET /api/v1/catalogo/servicios?destino=Tokio&fechaInicio=2026-12-10&fechaFin=2026-12-15.
- **Resultado esperado:**

  - Código HTTP 404 Not Found
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No hay servicios disponibles para el destino"

### ✅ Caso 3: 

- **Precondición:** Ejecución exitosa del endpoint.
- **Resultado esperado:** La respuesta JSON debe contener exactamente los campos:

  - "success" (booleano)
  - "data" (objeto), con los campos:
    - "destino" (texto)
    - "fechaInicio" (fecha ISO 8601)
    - "fechaFin" (fecha ISO 8601)
    - "servicios" (lista de objetos), cada uno con los campos:
      - "servicioId" (texto)
      - "tipoServicio" (texto)
      - "proveedor" (texto)
      - "tarifaNetaAdulto" (número)
      - "tarifaNetaMenor" (número)
      - "disponible" (booleano)
    - "fechaHoraConsulta" (fecha ISO 8601)
  - "message" (texto)

### ❌ Caso 4: 

- **Precondición:** El cliente envía fechaFin anterior a fechaInicio.
- **Acción:** Ejecutar el endpoint con fechaInicio=2026-12-15 y fechaFin=2026-12-10.
- **Resultado esperado:**

  - Código HTTP 400 Bad Request
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "La fecha de fin no puede ser anterior a la fecha de inicio"

### ❌ Caso 5: 

- **Precondición:** El repositorio de datos no está disponible o ocurre un error inesperado.
- **Acción:** Ejecutar el endpoint bajo condiciones simuladas de fallo del repositorio.
- **Resultado esperado:**
  - Código HTTP 500 Internal Server Error
  - Campo success = false y campo data = null
  - Campo message contiene el texto: "No fue posible consultar los servicios"

## ✅ Definición de Hecho

# Historia: Consultar servicios disponibles por destino

## 📦 Alcance Funcional

- [x] El endpoint devuelve los servicios activos del destino con su tarifa vigente.
- [x] Los servicios sin cupo se identifican como no disponibles.
- [x] La respuesta JSON cumple con el contrato definido.

## 🧪 Pruebas Completadas

- [x] Se ejecutaron pruebas funcionales en Swagger para validar el filtro de proveedores activos, las fechas y la disponibilidad.
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
