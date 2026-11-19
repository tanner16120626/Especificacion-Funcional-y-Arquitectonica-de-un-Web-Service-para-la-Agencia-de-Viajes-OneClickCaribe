# Especificación Funcional y Arquitectónica de un Web Service para la Agencia de Viajes One Click Caribe

Proyecto académico de la asignatura **Web Services** (Unidades Tecnológicas de Santander, docente Edward Villamizar).
Autor: **Tanner José Cedeño Miranda**.

## Enlaces

- Repositorio: https://github.com/tanner16120626/Especificacion-Funcional-y-Arquitectonica-de-un-Web-Service-para-la-Agencia-de-Viajes-OneClickCaribe
- Tablero GitHub Projects ("Columnas"): https://github.com/users/tanner16120626/projects/1

## Propósito

Centralizar la información operativa de One Click Caribe, automatizar el cálculo de cotizaciones y pagos, y estandarizar la comunicación entre los componentes del sistema mediante Web Services.

## Organización del backlog

| Elemento | Representación en GitHub |
|---|---|
| Épica (módulo MOD-01 a MOD-08) | Etiqueta `MOD-XX` |
| Historia de usuario (19 historias, HU-001 a HU-019) | Issue `HU-XXX Título` con la plantilla del docente |
| Trazabilidad FUN / PRO / RN | Campo `Trazabilidad` del Project |
| Prioridad | Campo `Prioridad` (Alta, Media, Baja) |
| Planificación | Campos `Corte` y `Sprint` |

## Estados del tablero

| Columna | Significado |
|---|---|
| To do | Historia refinada, pendiente de implementación |
| In progress | Historia en implementación en su rama propia (feature/HU-XXX), con pruebas locales en Swagger |
| Gestión Integración | Rama de la historia integrada a development mediante pull request |
| Testing | development integrada a testing; en la rama testing se valida que la implementación sea fiel a la historia |
| Done | Historia validada en testing, con sus casillas cumplidas y las evidencias de las pruebas en el issue |

Si la validación en testing no es fiel a la historia, la tarjeta vuelve a To do y el proceso se repite.

## Ramas

- `development`: rama de integración. Cada historia se implementa en una rama propia creada desde development (`feature/HU-XXX-descripcion`) y se integra mediante pull request.
- `testing`: rama de validación. development se integra a testing mediante pull request y desde ahí se validan las historias.
- `main` y `staging` no se utilizan en el tercer corte.

## Ejecución local

1. `python -m venv venv` y activar el entorno (`venv\Scripts\activate` en Windows).
2. `pip install -r requirements.txt`
3. Copiar `.env.example` como `.env`.
4. `uvicorn main:app --reload --host 127.0.0.1 --port 8000`
5. Abrir la documentación en `http://localhost:8000/docs`.

## Convenciones de los servicios

- Toda respuesta JSON contiene `success`, `data` y `message`.
- Rutas con prefijo `/api/v1`.
- Nombres de campos en camelCase y fechas en ISO 8601.

## Estructura del repositorio

- `main.py`: punto de entrada de la API (FastAPI).
- `api/`: routers con los endpoints, uno por módulo.
- `service/`: lógica de los casos de uso.
- `domain/`: esquemas de datos y reglas de negocio.
- `repository/`: repositorio en memoria y datos iniciales.
- `requirements.txt` y `.env.example`: dependencias y variables de entorno.
- `.github/ISSUE_TEMPLATE/historia-de-usuario.md`: plantilla del docente para crear historias desde *New issue*.
- `docs/plantilla/`: copia literal de la plantilla del docente.
- `docs/historias/`: especificación de las 19 historias del refinamiento final, un archivo por historia con el formato `HU-XXX-descripcion-corta.md` (por ejemplo, `HU-001-registrarme-en-el-portal.md`).
- `docs/refinamiento/Refinamiento_Final.md`: documento de refinamiento final del backlog (alcance, actores, historias, endpoints, reglas de negocio y criterios transversales).
- `docs/inventario/Inventario_APIs_OneClickCaribe.xlsx`: inventario de APIs del Web Service, alineado con las 19 historias.
