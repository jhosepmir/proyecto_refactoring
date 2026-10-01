# FASE 5 — Seguridad: Especificaciones y Comparación

Fecha: 2026-09-22  
Proyecto: Películas y Series (Refactorizado)  
Objetivo del proyecto: Refactorizar el proyecto "Películas y Series" (instrucciones_estudiantes.txt, FASE 5).

---

## PUNTOS OFICIALES DE LA FASE 5

Según `instrucciones_estudiantes.txt` (líneas 44-47), la Fase 5 exige:

```
FASE 5: SEGURIDAD
1. Mover contraseñas a variables de entorno
2. Eliminar datos hardcodeados sensibles
3. Agregar validación de entrada
```

A continuación, cada punto con su especificación y su cuadro comparativo ANTES vs DESPUÉS.

---

## PUNTO 1 — Mover contraseñas a variables de entorno

### Especificación

- Las claves de API (OMDb, TMDb) deben leerse con `os.getenv()` en tiempo de importación de `config.py`, nunca como literales en el código fuente.
- Se mantiene un fallback `"trilogy"` documentado como clave pública DEMO de OMDb (no sensible) para que el proyecto funcione sin red; cualquier despliegue real debe definir la variable `OMDB_API_KEY`.
- El módulo `constants.py` NO debe contener ninguna clave.
- La lectura debe ser sobreescribible en runtime y testeable con `monkeypatch.setenv` + `importlib.reload`.

### Cuadro comparativo

| Aspecto | ANTES | DESPUÉS |
|---|---|---|
| **Clave OMDb** | `api_movies.py:5` → `API_KEY_OMDB = "trilogy"` (literal fijo en código fuente) | `config.py:755` → `"api_key_omdb": os.getenv("OMDB_API_KEY", "trilogy")` |
| **Clave TMDb** | `api_movies.py:6` → `API_KEY_TMDB = ""` (literal en código fuente) | `config.py:756` → `"api_key_tmdb": os.getenv("TMDB_API_KEY", "")` |
| **Ubicación** | Variable global en la capa de datos (`api_movies.py`, junto a 10 globales más) | Diccionario `config.CONFIG` (configuración de ejecución centralizada) |
| **Cómo cambia la clave** | Editar el archivo .py y re-ejecutar | Variable de entorno: `OMDB_API_KEY=mi_clave python main.py` |
| **Documentación del fallback** | Sin explicación; parecía un secreto real | Comentario explícito en `config.py:747-749`: clave DEMO pública, no sensible |
| **`constants.py`** | Inexistente; las claves vivían en `api_movies.py` | `constants.py:20-21` declara: *"no hay claves hardcodeadas en este modulo"* |
| **Registro `api_config` legado** | Contenía la clave con el valor real | `config.py:479` → `'key': ''` (vacío, sin secreto) |
| **Uso en requests** | `buscar_pelicula()` construía la URL con el literal global | `api/omdb.py:43,68` → `config.CONFIG['api_key_omdb']` |
| **Tests** | 0 tests de gestión de claves | `tests/test_config.py`: 4 tests (fallback, TMDb vacía, lectura desde entorno con `importlib.reload`, sobreescritura runtime) |

### Puntos de verificación (tests)

| Test (`tests/test_config.py`) | Qué verifica |
|---|---|
| `test_conig_contiene_clave_omdb_desde_fallback` | Sin env var, usa `"trilogy"` |
| `test_conig_clave_tmdb_vacia_por_defecto` | TMDb vacía por defecto |
| `test_conig_clave_omdb_leida_desde_entorno` | `monkeypatch.setenv("OMDB_API_KEY", ...)` + `reload` lee el valor del entorno |
| `test_conig_clave_omdb_sobreescribible_en_runtime` | Se puede cambiar en runtime con `monkeypatch.setitem` |

---

## PUNTO 2 — Eliminar datos hardcodeados sensibles

### Especificación

- Ningún archivo del proyecto puede contener claves de API como literales.
- Los logs de diagnóstico deben enmascarar los parámetros sensibles de la URL antes de registrarlos (`apikey`, `key`, `api_key` → `***`, que se serializa como `%2A%2A%2A` en el log).
- El enmascarado debe hacerse en el punto único donde se construye/diagnostica el request (`api/http_client.py::_url_sin_secretos`).

### Cuadro comparativo

| Aspecto | ANTES | DESPUÉS |
|---|---|---|
| **Literales de clave en código** | `api_movies.py:5-6`: `API_KEY_OMDB = "trilogy"`, `API_KEY_TMDB = ""` | Ningún literal: solo `os.getenv()` en `config.py:755-756` |
| **Búsqueda global de claves** | Las claves aparecían en `api_movies.py` (definición) y en la construcción de URLs | `grep trilogy\|API_KEY\|getenv` solo encuentra: `config.py` (getenv), `constants.py` (comentario), tests y legacy `app.py` (ya lee de `config.CONFIG`) |
| **`app.py` (legado)** | Literal `API_KEY = "trilogy"` en el monolito | `app.py:12` → `API_KEY = config.CONFIG["api_key_omdb"]` (hereda del entorno) |
| **URL en logs** | Sin enmascarado (si había debug, la clave quedaba en texto plano) | `http_client.py:21-28` → `_url_sin_secretos()` con `PARAMETROS_SENSIBLES = {"apikey", "key", "api_key"}` |
| **Formato enmascarado** | No existía | `apikey=trilogy` → `apikey=%2A%2A%2A` (URL-encoded de `***`); el resto de parámetros se conserva (`t=Inception` visible) |
| **Test de enmascarado** | 0 tests | `test_http_client.py::test_hacer_request_enmascara_apikey_en_log`: verifica que `apikey=%2A%2A%2A` aparece y `apikey=trilogy` NO aparece en el log |
| **Punto único de enmascarado** | No aplicaba | Solo `api/http_client.py` (todos los requests pasan por ahí) |

### Puntos de verificación (tests)

| Test (`tests/test_http_client.py`) | Qué verifica |
|---|---|
| `test_hacer_request_enmascara_apikey_en_log` | `apikey=trilogy` no aparece en logs; `apikey=%2A%2A%2A` sí; parámetros no sensibles intactos |
| `test_hacer_request_consulta_url_fake` | La URL funcional sigue siendo correcta (el enmascarado es solo para logging) |

---

## PUNTO 3 — Agregar validación de entrada

### Especificación

Módulo `validation.py` con tres funciones, todas que lanzan `InputValidationError` (hereda de `ApplicationError`, Fase 4), capturada por el decorador `@manejar_errores` de `ui/menu.py`:

1. **`requiere_no_vacio(campo, valor)`** — recorta espacios; rechaza vacío, `None`, solo espacios y valores > 200 caracteres (`MAX_INPUT_LENGTH`).
2. **`valida_nombre_archivo(nombre)`** — regex `^[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*$`; rechaza path traversal (`../`, `a/b`, `a\b`, `/etc/passwd`), nombres ocultos (`.oculto`), espacios y caracteres especiales.
3. **`requiere_timeout(valor)`** — parsea entero positivo; rechaza `""`, `"abc"`, `"0"`, `"-5"`, `"3.5"`.

**Puntos de aplicación:**

- `ui/menu.py` (7 call sites): título, actor, serie, género, nombre de archivo (exportar/importar), timeout.
- `services/library_service.py` (2 call sites): `exportar_a_json()` e `importar_de_json()` validan el nombre ANTES de abrir el archivo (defensa en profundidad: aunque un llamador olvide validar, el servicio lo hace).

### Cuadro comparativo

| Aspecto | ANTES | DESPUÉS |
|---|---|---|
| **Entrada vacía** | Sin validación: título vacío → request a OMDb con `?t=` | `validation.requiere_no_vacio()` lanza `InputValidationError("Título: Ingrese un valor válido.")` en `ui/menu.py:73,92,113,144` |
| **Longitud de entrada** | Sin límite: entrada de miles de caracteres iba directo a la URL | Límite `MAX_INPUT_LENGTH = 200`; rechaza con `"Valor demasiado largo."` |
| **Timeout** | `main.py:272` (original): `CONFIG["timeout"] = int(input(...))` **crashea con `ValueError`** si el usuario escribe texto | `validation.requiere_timeout()` en `ui/menu.py:234`: `try/except ValueError` → `InputValidationError("Valor inválido para timeout. No se cambió.")`; rechaza `0`, negativos y decimales |
| **Nombres de archivo (export/import)** | Sin validación: el usuario podía escribir `../../etc/passwd` o `a\b` (path traversal) y el programa abría/escribía esa ruta | `valida_nombre_archivo()` con regex estricta; se aplica en `ui/menu.py:198,211` **y** en `library_service.py:83,100` (validación en dos capas) |
| **Manejo del error de validación** | `ValueError` sin capturar → crash; o `except:` desnudo que ocultaba el problema | `InputValidationError` → decorador `@manejar_errores` (`ui/menu.py:48-50`) → `logger.warning()` + mensaje amigable `display.mostrar_mensaje(str(exc))` |
| **Reutilización** | Lógica ad-hoc dispersa (`utils.py:44-56` con `print()` de reintentos) | Módulo único `validation.py` reutilizado por UI y servicios |
| **Tests** | 0 tests de validación de entrada | `tests/test_validation.py`: 16 tests (5 no-vacío, 4 archivo OK, 1 archivo vacío, 8 parametrizados de nombres peligrosos, 5 parametrizados de timeout) + 3 tests en `test_library_service.py` |

### Puntos de verificación (tests)

| Test (`tests/test_validation.py`) | Qué verifica |
|---|---|
| `test_requiere_no_vacio_ok` | Recorta y devuelve `"  Inception  "` → `"Inception"` |
| `test_requiere_no_vacio_rechaza_vacio/_solo_espacios/_None` | 3 tests: vacío, `"   "`, `None` → `InputValidationError` |
| `test_requiere_no_vacio_rechaza_demasiado_largo` | 201 caracteres → rechazado |
| `test_valida_nombre_archivo_ok` | `"datos.json"`, `"mis-favoritas_2024"` aceptados |
| `test_valida_nombre_archivo_rechaza_peligrosos` (parametrizado, 8 casos) | `..`, `../secreto`, `a/b`, `a\b`, `/etc/passwd`, `.oculto`, `"con espacio.txt"`, `"caracter\|raro.txt"` → rechazados |
| `test_valida_nombre_archivo_rechaza_vacio` | Nombre vacío → rechazado |
| `test_requiere_timeout_ok` + `test_requiere_timeout_recorta_espacios` | `"30"` → `30`; `" 30 "` → `30` |
| `test_requiere_timeout_rechaza_invalidos` (parametrizado, 5 casos) | `""`, `"abc"`, `"0"`, `"-5"`, `"3.5"` → rechazados |
| `tests/test_library_service.py` (3 tests) | Export/import con nombre peligroso → `InputValidationError` desde el servicio |

---

## RESUMEN DE IMPACTO POR PUNTO

| Punto Fase 5 | Archivos creados | Archivos modificados | Tests nuevos | Estado |
|---|---|---|---|---|
| 1. Claves a variables de entorno | — | `config.py`, `constants.py`, `api/omdb.py`, `app.py` | 4 (`test_config.py`) | ✅ Completo |
| 2. Eliminar datos sensibles hardcodeados | — | `api/http_client.py` (enmascarado), `config.py:479` (`api_config` legado vacío) | 1 (`test_hacer_request_enmascara_apikey_en_log`) | ✅ Completo |
| 3. Validación de entrada | `validation.py` | `ui/menu.py` (7 sites), `services/library_service.py` (2 sites) | 19 (`test_validation.py` + `test_library_service.py`) | ✅ Completo |

---

## COMPROMISOS Y NOTAS

1. **Fallback `"trilogy"`**: sigue presente en `config.py:755` como default. Es la clave DEMO pública de OMDb (no es un secreto), documentado en `config.py:747-749` y en `README.md`. Los tests dependen de este fallback (`test_config.py:8`).
2. **`app.py` y `utils.py` (legados)**: siguen en el repo como referencia histórica; `app.py` ya no tiene claves propias (lee de `config.CONFIG`), pero no es el entry-point (`main.py` lo es).
3. **Validación de timeout en `config.py`**: el `CONFIG` se inicializa con los defaults de `network_config` (30); la validación de entradas del usuario se aplica solo en el menú (opción 11), no en la carga inicial (los defaults son internos, no del usuario).
4. **Interacción con Fase 4**: `InputValidationError` pertenece a la jerarquía de excepciones de la Fase 4; la validación se beneficia del decorador `@manejar_errores` y del logging centralizado sin duplicar lógica.

---

*Documento generado para la Fase 5 del proyecto de refactoring.*
