"""services/series_service.py - Logica de negocio de series.

Transforma dicts crudos de TVMaze en modelos Series; no imprime nada.
Un 404 de TVMaze se interpreta como SeriesNotFoundError (dominio).
"""
import api.tvmaze as tvmaze
from exceptions.api_error import TVMazeError
from exceptions.not_found import SeriesNotFoundError
from models.series import Series


def buscar_series(nombre: str) -> list[Series]:
    """Busca series en TVMaze y las devuelve como lista de Series."""
    return [Series.from_tvmaze(data) for data in tvmaze.buscar_series(nombre)]


def obtener_detalles_serie(id_serie: int | None) -> Series:
    """Obtiene el detalle de una serie como Series.

    Lanza SeriesNotFoundError si TVMaze responde 404.
    """
    try:
        return Series.from_tvmaze(tvmaze.obtener_detalles_serie(id_serie))
    except TVMazeError as exc:
        if exc.status_code == 404:
            raise SeriesNotFoundError(f"No se encontro la serie con id {id_serie}") from exc
        raise