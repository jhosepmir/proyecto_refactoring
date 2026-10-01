# FASE 4 — Manejo de Errores: Especificaciones y Comparación

Fecha: 2026-09-22  
Proyecto: Películas y Series (Refactorizado)

---

## 1. OBJETIVO DE LA FASE

Reemplazar el manejo de errores deficiente (bare `except:`, ausencia de logging, `print()` debugging) por una jerarquía robusta de excepciones tipadas, un sistema centralizado de logging, y un mecanismo decorador que traduzca errores de dominio a mensajes amigables sin exponer trazas al usuario.

---

## 2. ESPECIFICACIONES TÉCNICAS

### 2.1 Jerarquía de Excepciones (`exceptions/`)

**Especificación:**
- Crear un paquete `exceptions/` con 6 archivos.
- Todas las excepciones deben heredar de `ApplicationError` (que hereda de `Exception`).
- `APIError` agrega atributo `status_code: int | None` para propagar códigos HTTP.
- Cada proveedor de API (`OMDBError`, `TVMazeError`) hereda de `APIError` para identificar el origen del fallo.
- `MovieNotFoundError` y `SeriesNotFoundError` representan errores de dominio (recurso no encontrado).
- `ConfigurationError` cubre fallos de configuración interna.
- `InputValidationError` cubre entradas de usuario inválidas (más adelante usada en Fase 5).

**Estructura:**
```
exceptions/
├── __init__.py          # Re-exporta con __all__
├── application_error.py # ApplicationError(Exception)
├── api_error.py         # APIError, InvalidResponseError, OMDBError, TVMazeError
├── not_found.py         # MovieNotFoundError, SeriesNotFoundError
├── configuration_error.py # ConfigurationError
└── validation_error.py  # InputValidationError
```

### 2.2 Cliente HTTP (`api/http_client.py`)

**Especificación:**
- Función `hacer_request(url, params)` que centraliza todos los GET.
- Traducir excepciones de `requests` a la jerarquía de la app:
  - `requests.Timeout` → `APIError("La API externa tardo demasiado en responder")`
  - `requests.ConnectionError` → `APIError("No se pudo conectar con la API externa")`
  - `requests.RequestException` genérico → `APIError("Error de comunicacion con la API externa")`
  - `requests.HTTPError` → `APIError` con `status_code` preservado
  - `ValueError` de `response.json()` → `InvalidResponseError`
- Levantar `ConfigurationError` si `CONFIG["timeout"]` falta.
- Máscarar `apikey` en logs con `%2A%2A%2A` mediante `_url_sin_secretos()`.
- Usar `logging.getLogger(__name__)` para diagnóstico (debug/verbose).

### 2.3 Servicios (`services/`)

**Especificación:**
- `movie_service.buscar_pelicula(titulo)`: lanza `MovieNotFoundError` si OMDb devuelve `None`.
- `series_service.obtener_detalles_serie(id)`: captura `TVMazeError` con `status_code == 404` y lanza `SeriesNotFoundError`.
- Los servicios **nunca imprimen nada**; solo transforman datos o lanzan excepciones.

### 2.4 Decorador de Manejo de Errores (`ui/menu.py`)

**Especificación:**
- Decorador `@manejar_errores` que envuelve cada flujo de menú.
- Captura específica (en orden de especificidad):
  - `MovieNotFoundError` → `display.mostrar_error_pelicula_no_encontrada()` + `logger.error()`
  - `SeriesNotFoundError` → `display.mostrar_error_serie_no_encontrada()` + `logger.error()`
  - `ConfigurationError` → `display.mostrar_error_configuracion()` + `logger.error()`
  - `InputValidationError` → `display.mostrar_mensaje(str(exc))` + `logger.warning()`
  - `APIError` → `display.mostrar_error_api()` + `logger.error()`
  - `ApplicationError` genérico → `display.mostrar_error_inesperado()` + `logger.error()`
- Los errores inesperados se propagan a `main()` como última protección.
- Logging con `exc_info=True` para trazas completas en el archivo, nunca en consola.

### 2.5 Logging Centralizado (`logging_config.py`)

**Especificación:**
- Función `configure_logging()` idempotente (no duplica handlers si se llama dos veces).
- **Archivo** (`logs/app.log`): nivel `DEBUG`, formato con timestamp, level, logger name, message. Handler `RotatingFileHandler` (1 MB max, 2 backups).
- **Consola**: nivel `WARNING` solo; el usuario no ve trazas, solo mensajes amigables de la UI. Usa `ConsoleFormatter` que omite `exc_info` (las trazas quedan solo en el archivo).
- Crea el directorio `logs/` si no existe con `os.makedirs(..., exist_ok=True)`.

### 2.6 Punto de Entrada (`main.py`)

**Especificación:**
- Última línea de defensa: captura `KeyboardInterrupt`, `ApplicationError`, y `Exception` genérico.
- Para `ApplicationError`: log con `exc_info=True` + mensaje genérico `"Ocurrió un error inesperado. Revise el log para más detalles."`
- Para `Exception` genérico: `logger.exception()` (auto-log de traceback) + mismo mensaje genérico.
- **Nunca** muestra trazas al usuario.

---

## 3. COMPARACIÓN ANTES vs DESPUÉS

### 3.1 Excepciones

| Aspecto | ANTES (Código Original) | DESPUÉS (Refactorizado) |
|---|---|---|
| **Jerarquía** | Sin excepciones custom; solo `Exception` implícito | Jerarquía completa: `ApplicationError` con subclases por dominio |
| **Bare `except:`** | 27 ocurrencias en `main.py`, `app.py`, `utils.py` | **0 ocurrencias**; todas las excepciones son específicas |
| **`except:` desnudo** | Tapaba `KeyError`, `TypeError`, `ValueError` sin distinguir | Cada excepción capturada con tipo concreto o `.get("X", "N/A")` |
| **`except Exception`** | 1 ocurrencia en `main.py:332-334` sin logging | 1 ocurrencia en `main.py` como última protección con `logger.exception()` |
| **Identificación de origen** | No se distinguía si el error era de OMDb, TVMaze o red | `OMDBError`, `TVMazeError`, `APIError` con `status_code` |
| **Not found** | `if Response == "True"` / listas vacías sin error explícito | `MovieNotFoundError`, `SeriesNotFoundError` con mensaje descriptivo |

### 3.2 Manejo de Errores en `hacer_request`

| Aspecto | ANTES (`api_movies.py`) | DESPUÉS (`api/http_client.py`) |
|---|---|---|
| **`requests.get()`** | Sin `try/except`; `timeout` pasado pero sin catch | `try/except` para `Timeout`, `ConnectionError`, `RequestException` |
| **`response.raise_for_status()`** | No se llamaba | Llamado con `try/except` → `APIError` con `status_code` |
| **`response.json()`** | Sin `try/except`; crash con `ValueError` | `try/except ValueError` → `InvalidResponseError` |
| **Log de URL** | Sin mascaramiento | `_url_sin_secretos()` enmascara `apikey` como `%2A%2A%2A` |
| **Configuración ausente** | No validaba si `timeout` existía | Lanza `ConfigurationError` si `timeout` falta en `CONFIG` |

### 3.3 Logging

| Aspecto | ANTES | DESPUÉS |
|---|---|---|
| **Módulo `logging`** | No usado; solo `print()` | Centralizado en `logging_config.py` |
| **Consola** | `print()` crudos para todo (errores, resultados, depuración) | Solo `WARNING`+; mensajes amigables vía `display` |
| **Archivo** | No existía | `logs/app.log` con `RotatingFileHandler` (DEBUG) |
| **Idempotencia** | N/A | `configure_logging()` verifica `if root.handlers: return` |
| **Trazas al usuario** | `print()` de errores + bare `except` mostraba traceback | `print()` solo mensajes amigables; trazas van al log |
| **`print()` debugging** | Múltiples `print()` en `api_movies.py`, `main.py`, `utils.py` | Eliminados; reemplazados por `logger.debug()`/`logger.error()` |

### 3.4 Flujo de Ejecución

| Aspecto | ANTES | DESPUÉS |
|---|---|---|
| **Entry point** | `main.py` con lógica mezclada + `app.py` duplicado | `main.py` solo entrada; `ui/menu.py` orquesta |
| **Decorator** | Sin decorador; cada función manejaba errores inconsistentemente | `@manejar_errores` en cada flujo de menú |
| **Capa de presentación** | `print()` mezclado con lógica en `main.py`, `app.py`, `utils.py` | `ui/display.py` es el único módulo con `print()` |
| **Capa de servicios** | `api_movies.py` mezclaba API, lógica, y presentación | Servicios no imprimen; solo lanzan excepciones o devuelven modelos |
| **Separación de errores** | Un `except:` genérico para todo | Cada tipo de error capturado, logueado y traducido a mensaje UI |

### 3.5 Códigos y Archivos Específicos

| Archivo/Feature | ANTES | DESPUÉS |
|---|---|---|
| `main.py:37-77` | 9 bare `except:` tapando `KeyError` en `try: print(pelicula["X"])` | `display.mostrar_pelicula()` usa `Movie` con atributos seguros (no `dict` directo) |
| `main.py:253` | `except: print("Error al importar archivo")` sin tipo ni variable `e` | `funcion_importar()` captura `(OSError, ValueError)` con `logger.error(..., exc_info=True)` |
| `main.py:272` | `int(input())` sin `try/except ValueError` (crash con texto) | `validation.requiere_timeout()` lanza `InputValidationError` |
| `utils.py:68-118` | 11 `try: ... except:` desnudos en `format_movie_display` | Eliminado; `display.py` usa modelo `Movie`/`Series` con atributos |
| `utils.py:239` | `except: return False` en `validate_date()` | Eliminado; `validate_date` en `validation.py` con `try/except ValueError` y `raise InputValidationError` |
| `utils.py:266` | `except: return items` en `sort_items()` | Eliminado; la lógica de sorting se simplificó |
| `api_movies.py:29` | `requests.get` sin `try/except` | `hacer_request()` con manejo completo de excepciones |
| `api_movies.py:34` | `response.json()` sin `try/except` | `hacer_request()` con `try/except ValueError` |

---

## 4. ARCHIVOS CREADOS, MODIFICADOS Y ELIMINADOS

### 4.1 Archivos Nuevos (Fase 4)

| Archivo | Descripción |
|---|---|
| `exceptions/__init__.py` | Paquete de excepciones; re-exporta con `__all__` |
| `exceptions/application_error.py` | Clase base `ApplicationError(Exception)` |
| `exceptions/api_error.py` | `APIError`, `InvalidResponseError`, `OMDBError`, `TVMazeError` |
| `exceptions/not_found.py` | `MovieNotFoundError`, `SeriesNotFoundError` |
| `exceptions/configuration_error.py` | `ConfigurationError` |
| `exceptions/validation_error.py` | `InputValidationError` |
| `api/http_client.py` | Cliente HTTP compartido con manejo de excepciones y masking |
| `logging_config.py` | Configuración centralizada de logging (archivo + consola) |
| `tests/test_exceptions.py` | Tests de la jerarquía de excepciones |
| `tests/test_http_client.py` | Tests del cliente HTTP (11 tests) |
| `tests/test_logging_config.py` | Tests del configurador de logging |

### 4.2 Archivos Modificados (Fase 4)

| Archivo | Cambio Principal |
|---|---|
| `api/omdb.py` | Usa `hacer_request()`, lanza `OMDBError`, elimina lógica de error cruda |
| `api/tvmaze.py` | Usa `hacer_request()`, lanza `TVMazeError` |
| `services/movie_service.py` | Lanza `MovieNotFoundError` en lugar de devolver `None` implícito |
| `services/series_service.py` | Convierte `TVMazeError` 404 en `SeriesNotFoundError` |
| `ui/menu.py` | `@manejar_errores` en todos los flujos; logging en lugar de `print()` |
| `main.py` | Reestructurado con `try/except` de última protección; logging |
| `validation.py` | Lanza `InputValidationError` en lugar de imprimir o retornar `False` |
| `ui/display.py` | Añade métodos `mostrar_error_*` para todos los tipos de error |

### 4.3 Archivos Eliminados por la Refactorización (Indirectamente)

| Archivo | Razón |
|---|---|
| `api_movies.py` (original) | Reemplazado por la arquitectura `api/` + `services/` + `models/` |
| `utils.py` (original) | Reemplazado por `ui/display.py` + `validation.py` + `logging_config.py` |
| `app.py` (original) | Monolito duplicado; eliminado en fases anteriores |

---

## 5. CUBRIMIENTO DE TESTS (FASE 4)

### 5.1 Tests de Excepciones (`test_exceptions.py`)

| Test | Verifica |
|---|---|
| `test_todas_cuelgan_de_application_error` | Herencia correcta de la jerarquía |
| `test_apierror_guarda_mensaje_y_status_code` | `APIError` con `status_code` |
| `test_apierror_status_code_opcional` | `status_code` es `None` por defecto |
| `test_se_pueden_capturar_como_application_error` | Polimorfismo: `OMDBError` es `ApplicationError` |
| `test_not_found_llevan_mensaje` | `MovieNotFoundError` y `SeriesNotFoundError` con mensaje |

### 5.2 Tests del Cliente HTTP (`test_http_client.py`)

| Test | Verifica |
|---|---|
| `test_hacer_request_consulta_url_fake` | Request básico retorna dict |
| `test_hacer_request_registra_debug_y_verbose` | Logs cuando `debug=True, verbose=True` |
| `test_hacer_request_no_registra_debug_desactivado` | No logs cuando están `False` |
| `test_hacer_request_enmascara_apikey_en_log` | `apikey=trilogy` → `apikey=%2A%2A%2A` |
| `test_hacer_request_timeout_es_error_de_api` | `Timeout` → `APIError` |
| `test_hacer_request_connection_error_es_error_de_api` | `ConnectionError` → `APIError` |
| `test_hacer_request_http_error_conserva_status_code` | `HTTPError` → `APIError` con `status_code` |
| `test_hacer_request_json_invalido_es_invalid_response` | `ValueError` de JSON → `InvalidResponseError` |
| `test_hacer_request_sin_timeout_configurado_es_configuration_error` | Falta `timeout` → `ConfigurationError` |
| `test_hacer_request_request_exception_generica_es_api_error` | `RequestException` genérico → `APIError` |

### 5.3 Tests de Logging (`test_logging_config.py`)

| Test | Verifica |
|---|---|
| `test_configure_logging_crea_handlers_y_archivo` | Handlers de archivo y consola creados; idempotencia |

**Coverage Fase 4:** Los tests de la Fase 4 contribuyen al coverage total del proyecto (95%).

---

## 6. BENEFICIOS ALCANZADOS

1. **Seguridad operacional**: El usuario nunca ve trazas de excepciones; siempre recibe un mensaje amigable.
2. **Diagnóstico mejorado**: El archivo `logs/app.log` contiene trazas completas con timestamps para desarrollo y producción.
3. **Mantenibilidad**: Cada tipo de error se maneja de forma específica; agregar un nuevo tipo de error no requiere modificar múltiples `except:`.
4. **Seguridad**: El `apikey` queda enmascarado en los logs, evitando exposición de credenciales.
5. **Testabilidad**: La jerarquía de excepciones y el `http_client` son testeables de forma aislada con mocks.
6. **Consistencia**: Todos los flujos de menú usan el mismo decorador `@manejar_errores`, eliminando inconsistencias en el manejo de errores.
7. **Eliminación de `print()` debugging**: Todo el debug se hace a través de `logging` con niveles configurables.

---

## 7. COMPROMISOS Y LIMITACIONES

1. **`utils.py` heredado**: El archivo `utils.py` original (con bare `except:` y `print()`) sigue existiendo en el proyecto como referencia histórica. No se importa desde ningún módulo refactorizado.
2. **`CACHE_PELICULAS` / `CACHE_SERIES`**: Los cachés en `api/omdb.py` y `api/tvmaze.py` aún usan variables globales (`global CACHE_PELICULAS`, `global CACHE_SERIES`). Esto fue identificado en el ANALISIS_PLAN como pendiente para una fase futura (eliminación de globales).
3. **`ConfigurationError` en `http_client`**: La dependencia circular con `config` se resuelve importando `config` dentro de la función o al nivel de módulo; puede causar importación circular si no se maneja con cuidado en testeos avanzados.

---

*Documento generado para la Fase 4 del proyecto de refactoring.*
