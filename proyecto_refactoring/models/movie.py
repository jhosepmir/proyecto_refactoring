"""models/movie.py - Modelo de datos de una pelicula.

Normaliza los dicts de OMDb y del catalogo interno (populares/genero) en un
objeto tipado para la capa UI.

`raw` conserva el dict OMDb ORIGINAL tal como llega de la API para que la
exportacion de favoritas a JSON reproduzca exactamente el formato previo.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Movie:
    """Pelicula lista para presentar en la UI."""

    title: str | None = None
    year: str | None = None
    imdb_rating: str | None = None
    genre: str | None = None
    director: str | None = None
    actors: str | None = None
    plot: str | None = None
    country: str | None = None
    awards: str | None = None
    rating: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_omdb(cls, data: dict[str, Any]) -> "Movie":
        """Construye desde un dict de OMDb (busqueda/detalle)."""
        return cls(
            title=data.get("Title", "N/A"),
            year=data.get("Year", "N/A"),
            imdb_rating=data.get("imdbRating", "N/A"),
            genre=data.get("Genre", "N/A"),
            director=data.get("Director", "N/A"),
            actors=data.get("Actors", "N/A"),
            plot=data.get("Plot", "N/A"),
            country=data.get("Country", "N/A"),
            awards=data.get("Awards", "N/A"),
            rating=None,
            raw=dict(data),
        )

    @classmethod
    def from_catalog(cls, data: dict[str, Any]) -> "Movie":
        """Construye desde el catalogo interno (populares / genero)."""
        return cls(
            title=data["titulo"],
            year=str(data["anio"]),
            rating=data["rating"],
            raw=dict(data),
        )