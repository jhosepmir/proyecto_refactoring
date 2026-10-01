"""exceptions/not_found.py - Errores de dominio: recursos inexistentes.

Los servicios traducen respuestas validas "vacias" en estos errores para que la
UI pueda mostrar un mensaje amigable sin conocer detalles de cada API.
"""
from exceptions.application_error import ApplicationError


class MovieNotFoundError(ApplicationError):
    """No se encontro la pelicula buscada."""


class SeriesNotFoundError(ApplicationError):
    """No se encontro la serie buscada."""