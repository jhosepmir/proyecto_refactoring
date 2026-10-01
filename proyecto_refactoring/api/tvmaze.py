"""api/tvmaze.py - Acceso a la API de TVMaze.

Devuelve dicts crudos o []/dict; la transformacion a modelos ocurre en la
capa de servicios. Los errores de transporte se traducen a TVMazeError
conservando el status_code para que los servicios distingan 404 (no existe).
"""
import logging

import constants
from api.http_client import hacer_request
from exceptions.api_error import APIError, InvalidResponseError, TVMazeError

logger = logging.getLogger(__name__)

CACHE_SERIES: dict[str, dict | list] = {}


def _consulta(url: str) -> dict | list:
    """Ejecuta el request y traduce errores de transporte a TVMazeError."""
    try:
        return hacer_request(url)
    except InvalidResponseError:
        raise
    except APIError as exc:
        raise TVMazeError(str(exc), status_code=exc.status_code) from exc


def buscar_series(nombre: str) -> list[dict]:
    """Busca series en TVMaze ([] si no hay resultados)."""
    global CACHE_SERIES

    cache_key = f"{constants.CACHE_KEY_PREFIX_SERIES}{nombre}"
    if cache_key in CACHE_SERIES:
        return CACHE_SERIES[cache_key]

    url = f"{constants.BASE_URL_TVMAZE}/search/shows?q={nombre}"
    data = _consulta(url)

    if not isinstance(data, list):
        raise InvalidResponseError("TVMaze devolvio un formato inesperado en la busqueda")

    CACHE_SERIES[cache_key] = data
    return data


def obtener_detalles_serie(id_serie: int | None) -> dict:
    """Obtiene el detalle de una serie por id."""
    url = f"{constants.BASE_URL_TVMAZE}/shows/{id_serie}"
    data = _consulta(url)

    if not isinstance(data, dict):
        raise InvalidResponseError("TVMaze devolvio un formato inesperado en el detalle")
    return data