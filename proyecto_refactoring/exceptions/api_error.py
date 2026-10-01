"""exceptions/api_error.py - Errores de la capa de acceso a APIs.

APIError es la base; el atributo status_code permite a los servicios traducir
codigos HTTP (p.ej. 404) en errores de dominio sin perder informacion.
InvalidResponseError señala respuestas con formato inesperado.
OMDBError/TVMazeError identifican de que proveedor proviene el fallo.
"""
from exceptions.application_error import ApplicationError


class APIError(ApplicationError):
    """Error al comunicarse con una API externa."""

    def __init__(self, mensaje: str, status_code: int | None = None):
        super().__init__(mensaje)
        self.status_code = status_code


class InvalidResponseError(APIError):
    """La API respondio un formato que no se esperaba."""


class OMDBError(APIError):
    """Error originado por la API de OMDb."""


class TVMazeError(APIError):
    """Error originado por la API de TVMaze."""