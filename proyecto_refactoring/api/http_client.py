"""api/http_client.py - Cliente HTTP compartido por OMDb y TVMaze.

Centraliza el GET y el logging de diagnostico para evitar duplicar el request
entre api/omdb.py y api/tvmaze.py. Solo obtiene datos; los errores de red,
HTTP y JSON se convierten aqui en excepciones de la jerarquia de la app.
"""
import logging
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

import config
from exceptions.api_error import APIError, InvalidResponseError
from exceptions.configuration_error import ConfigurationError

logger = logging.getLogger(__name__)

PARAMETROS_SENSIBLES = {"apikey", "key", "api_key"}


def _url_sin_secretos(url: str) -> str:
    """Devuelve la URL con los valores de parametros sensibles enmascarados."""
    partes = urlsplit(url)
    query = [
        (nombre, "***" if nombre.lower() in PARAMETROS_SENSIBLES else valor)
        for nombre, valor in parse_qsl(partes.query, keep_blank_values=True)
    ]
    return urlunsplit((partes.scheme, partes.netloc, partes.path, urlencode(query), ""))


def hacer_request(url: str, params: dict | None = None) -> dict | list:
    """Ejecuta un GET y devuelve el JSON crudo, traduciendo errores a APIError."""
    try:
        timeout = config.CONFIG["timeout"]
    except KeyError as exc:
        raise ConfigurationError("Configuracion de timeout ausente") from exc

    if config.CONFIG["debug"]:
        logger.debug("Haciendo request a %s", _url_sin_secretos(url))

    try:
        response = requests.get(url, params=params, timeout=timeout)
    except requests.Timeout as exc:
        raise APIError("La API externa tardo demasiado en responder") from exc
    except requests.ConnectionError as exc:
        raise APIError("No se pudo conectar con la API externa") from exc
    except requests.RequestException as exc:
        raise APIError("Error de comunicacion con la API externa") from exc

    if config.CONFIG["verbose"]:
        logger.debug("Status code: %s", response.status_code)

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise APIError(
            f"La API respondio con estado {response.status_code}",
            status_code=response.status_code,
        ) from exc

    try:
        return response.json()
    except ValueError as exc:
        raise InvalidResponseError("La respuesta de la API no es JSON valido") from exc