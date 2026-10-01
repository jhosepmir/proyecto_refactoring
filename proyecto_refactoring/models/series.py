"""models/series.py - Modelo de datos de una serie (TVMaze).

Replica las expresiones .get() del codigo original para preservar la salida
por defecto exacta ('N/A' en detalle, '' en listados, recorte de resumen).
"""
from dataclasses import dataclass


@dataclass
class Series:
    """Serie lista para presentar en la UI."""

    id: int | None = None
    name: str | None = None
    language: str | None = None
    genres: list[str] | None = None
    rating: int | float | str | None = None
    status: str | None = None
    premiered: str | None = None
    ended: str | None = None
    runtime: int | None = None
    summary: str | None = "N/A"

    @classmethod
    def from_tvmaze(cls, data: dict) -> "Series":
        """Construye desde un dict de TVMaze.

        `data` puede ser el wrapper `{"show": ...}` devuelto por /search/shows
        o el show directo devuelto por /shows/{id}.
        """
        show = data.get("show", data)
        rating_obj = show.get("rating", {})
        if isinstance(rating_obj, dict):
            rating = rating_obj.get("average", "N/A")
        else:
            rating = rating_obj
        return cls(
            id=show.get("id"),
            name=show.get("name"),
            language=show.get("language"),
            genres=show.get("genres", []),
            rating=rating,
            status=show.get("status"),
            premiered=show.get("premiered"),
            ended=show.get("ended"),
            runtime=show.get("runtime"),
            summary=show.get("summary", "N/A"),
        )