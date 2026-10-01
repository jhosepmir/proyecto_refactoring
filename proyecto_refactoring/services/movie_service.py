"""services/movie_service.py - Logica de negocio de peliculas.

Transforma dicts crudos en modelos Movie; no imprime absolutamente nada
(la presentacion pertenece a la capa UI). "No encontrada" se expresa como
MovieNotFoundError para que la UI decida como mostrarlo.
"""
import constants
import api.omdb as omdb
from exceptions.not_found import MovieNotFoundError
from models.movie import Movie


def buscar_pelicula(titulo: str) -> Movie:
    """Busca una pelicula y la devuelve como Movie.

    Lanza MovieNotFoundError si OMDb respondio sin resultados.
    """
    data = omdb.buscar_pelicula(titulo)
    if data is None:
        raise MovieNotFoundError(f"No se encontro la pelicula '{titulo}'")
    return Movie.from_omdb(data)


def buscar_peliculas_por_actor(actor: str) -> list[Movie]:
    """Busca peliculas por actor y las devuelve como lista de Movie."""
    return [Movie.from_omdb(data) for data in omdb.buscar_peliculas_por_actor(actor)]


def obtener_peliculas_populares() -> list[Movie]:
    """Devuelve las peliculas populares del catalogo interno."""
    return [Movie.from_catalog(data) for data in constants.POPULAR_MOVIES]


def buscar_peliculas_por_genero(genero: str) -> list[Movie]:
    """Busca peliculas por genero del catalogo interno (sin API real)."""
    accion = [
        Movie.from_catalog(data)
        for data in constants.MOVIES_BY_GENRE[constants.GENRE_ACTION]
    ]
    comedia = [
        Movie.from_catalog(data)
        for data in constants.MOVIES_BY_GENRE[constants.GENRE_COMEDIA]
    ]

    if genero.lower() == constants.GENRE_ACTION:
        return accion
    if genero.lower() == constants.GENRE_COMEDIA:
        return comedia
    return accion + comedia