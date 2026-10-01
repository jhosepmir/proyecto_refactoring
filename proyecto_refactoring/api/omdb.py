"""api/omdb.py - Acceso a la API de OMDb.

Devuelve dicts crudos o None/[]; la transformacion a modelos ocurre en la
capa de servicios. "Movie not found" es una respuesta valida (None); cualquier
otro error de OMDb (p.ej. clave invalida) se propaga como OMDBError.
"""
import logging

import config
import constants
from api.http_client import hacer_request
from exceptions.api_error import APIError, InvalidResponseError, OMDBError

logger = logging.getLogger(__name__)

CACHE_PELICULAS: dict[str, dict] = {}

MENSAJE_CLAVE_INVALIDA = "Invalid API key"
MENSAJE_SIN_RESULTADO = "Movie not found"


def _consulta(url: str) -> dict | list:
    """Ejecuta el request y traduce errores de transporte a OMDBError."""
    try:
        return hacer_request(url)
    except InvalidResponseError:
        raise
    except APIError as exc:
        raise OMDBError(str(exc), status_code=exc.status_code) from exc


def buscar_pelicula(titulo: str) -> dict | None:
    """Busca una pelicula por titulo en OMDb (None si no existe)."""
    global CACHE_PELICULAS

    if titulo in CACHE_PELICULAS:
        if config.CONFIG["debug"]:
            logger.debug("Usando cache para %s", titulo)
        return CACHE_PELICULAS[titulo]

    url = (
        f"{constants.BASE_URL_OMDB}?{constants.PARAM_TITLE}={titulo}"
        f"&{constants.PARAM_APIKEY}={config.CONFIG['api_key_omdb']}"
    )
    data = _consulta(url)

    if not isinstance(data, dict):
        raise InvalidResponseError("OMDb devolvio un formato inesperado")

    if data.get(constants.OMDB_RESPONSE_KEY) == constants.OMDB_SUCCESS:
        CACHE_PELICULAS[titulo] = data
        return data

    error = data.get(constants.OMDB_ERROR_KEY, "")
    if MENSAJE_CLAVE_INVALIDA in error:
        raise OMDBError(f"Clave de API invalida: {error}")
    if MENSAJE_SIN_RESULTADO in error or not error:
        return None

    raise OMDBError(f"OMDb respondio con error: {error}")


def buscar_peliculas_por_actor(actor: str) -> list[dict]:
    """Busca peliculas por actor (sin paginacion; [] si no hay resultados)."""
    url = (
        f"{constants.BASE_URL_OMDB}?{constants.PARAM_SEARCH}={actor}"
        f"&{constants.PARAM_TYPE}={constants.PARAM_TYPE_MOVIE}"
        f"&{constants.PARAM_APIKEY}={config.CONFIG['api_key_omdb']}"
    )
    data = _consulta(url)

    if not isinstance(data, dict):
        raise InvalidResponseError("OMDb devolvio un formato inesperado")

    if data.get(constants.OMDB_RESPONSE_KEY) == constants.OMDB_SUCCESS:
        return data.get(constants.OMDB_SEARCH_KEY, [])

    error = data.get(constants.OMDB_ERROR_KEY, "")
    if MENSAJE_CLAVE_INVALIDA in error:
        raise OMDBError(f"Clave de API invalida: {error}")
    return []