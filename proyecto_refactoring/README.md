# Proyecto de Refactoring — Películas y Series (Refactorizado)

Proyecto educativo refactorizado: cliente de APIs OMDb + TVMaze con manejo de errores, seguridad y tests.

## Estructura

```
.
├── api/                  # Clientes HTTP (http_client, omdb, tvmaze) + cache
├── models/               # Dataclasses Movie, Series
├── services/             # Lógica de negocio (movie_service, series_service, library_service)
├── ui/                   # UI por capas (menu, display)
├── exceptions/           # Jerarquía: ApplicationError -> APIError/OMDBError/TVMazeError/...
├── tests/                # Pytest (unit + integración + e2e)
├── validation.py         # Validación de entrada (longitud, nombres de archivo, timeout)
├── logging_config.py     # Logging centralizado (consola WARNING + logs/app.log DEBUG rotativo)
├── config.py             # Configuración + variables de entorno (OMDB_API_KEY)
├── constants.py          # Constantes centralizadas (sin secretos)
├── main.py               # Entrada con última protección (sin trazas al usuario)
└── .opencode/skills/     # 3 skills (refactoring, api-integration, testing)
```

## Mejoras realizadas

**FASE 4 — Manejo de errores**
- Jerarquía `exceptions/` (ApplicationError, APIError/InvalidResponseError/OMDBError/TVMazeError, MovieNotFoundError/SeriesNotFoundError, ConfigurationError).
- `api/http_client`: enmascara `apikey` en logs (`%2A%2A%2A`), traduce `Timeout`/`ConnectionError`/`HTTPError`/`ValueError` JSON a errores tipados.
- `services`: `buscar_pelicula` lanza `MovieNotFoundError`; `obtener_detalles_serie` mapea 404 a `SeriesNotFoundError`.
- `ui/menu`: decorator `@manejar_errores`; `main.py`: última protección sin trazas; `logging_config` idempotente.

**FASE 5 — Seguridad**
- Claves vía `os.getenv("OMDB_API_KEY", "trilogy")` en `config.CONFIG` (fallback demo público documentado); eliminadas de `constants.py` y del `api_config` legado.
- Validación en `validation.py` y `ui/menu`/`services/library_service` (no vacío, longitud 200, nombres de archivo `^[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*$` contra traversal, timeout entero positivo).

**FASE 6 — Testing**
- `tests/` con pytest: `conftest` (`fake_requests` nunca red, `clear_api_caches`, `restore_runtime_config`, `silenciar_logging`).
- Unitarios por servicio (movie/series/library) + integración APIs (omdb/tvmaze/http_client) + validación + menú scripted (decorador, submenús config/favoritas/historial) + logging + config.
- Coverage **95%** (`coverage run --branch -m pytest`).

## APIs

- **OMDb** `http://www.omdbapi.com/` — `OMDB_API_KEY` env (default demo `trilogy`)
- **TVMaze** `http://api.tvmaze.com` — sin key

## Cómo ejecutar

```bash
pip install -r requirements.txt
python main.py
# opcional: OMDB_API_KEY=mi_clave python main.py
```

## Tests y coverage

```bash
pytest -q
coverage run --branch -m pytest -q
coverage report        # 95%
# e2e baseline (sin red): python run_e2e.py final.txt
```

## Skills (3)

- `refactoring` — eliminar malas prácticas, SOLID, type hints
- `api-integration` — clientes, cache, reintentos, logging, timeouts
- `testing` — pytest, mocks, fixtures, parametrización, coverage

Ver `.opencode/skills/*/instrucciones.md` y `.opencode/skills/*/skill.json`.
