"""services/library_service.py - Estado de usuario.

Favoritas, historial, estadisticas y exportacion/importacion a JSON.
A diferencia del modulo previo, NO imprime: devuelve datos y la UI se encarga
de la presentacion.
"""
import json

import constants
import models.movie as movie_module
import validation
from models.movie import Movie

USUARIO_LOGUEADO = None
PELICULAS_FAVORITAS: list[Movie] = []
HISTORIAL_BUSQUEDAS: list[dict] = []


def agregar_a_favoritas(pelicula: Movie) -> bool:
    """Agrega a favoritas sin duplicados (por titulo). Devuelve si se agrego."""
    global PELICULAS_FAVORITAS

    for pelicula_existente in PELICULAS_FAVORITAS:
        if pelicula_existente.title == pelicula.title:
            return False

    PELICULAS_FAVORITAS.append(pelicula)
    return True


def eliminar_de_favoritas(titulo: str) -> bool:
    """Elimina una favorita por titulo. Devuelve si se elimino alguna."""
    global PELICULAS_FAVORITAS

    for i in range(len(PELICULAS_FAVORITAS)):
        if PELICULAS_FAVORITAS[i].title == titulo:
            PELICULAS_FAVORITAS.pop(i)
            return True
    return False


def agregar_al_historial(pelicula: Movie) -> None:
    """Agrega una pelicula al historial (sin limite)."""
    global HISTORIAL_BUSQUEDAS
    HISTORIAL_BUSQUEDAS.append(
        {
            "titulo": pelicula.raw.get("Title", ""),
            "fecha": constants.HISTORY_DATE_PLACEHOLDER,
        }
    )


def limpiar_historial() -> None:
    """Limpia el historial."""
    global HISTORIAL_BUSQUEDAS
    HISTORIAL_BUSQUEDAS = []


def obtener_favoritas() -> list[Movie]:
    """Devuelve la lista de favoritas."""
    return PELICULAS_FAVORITAS


def obtener_historial() -> list[dict]:
    """Devuelve el historial de busquedas."""
    return HISTORIAL_BUSQUEDAS


def obtener_estadisticas() -> dict[str, int]:
    """Devuelve estadisticas de favoritas e historial."""
    return {
        "total_favoritas": len(PELICULAS_FAVORITAS),
        "total_historial": len(HISTORIAL_BUSQUEDAS),
    }


def exportar_a_json(nombre_archivo: str) -> str:
    """Exporta favoritas/historial/estadisticas a JSON.

    Favoritas se serializan desde su dict OMDb crudo (`raw`) para conservar
    el formato exacto de exportacion previo.
    """
    nombre_archivo = validation.valida_nombre_archivo(nombre_archivo)
    data = {
        "favoritas": [pelicula.raw for pelicula in PELICULAS_FAVORITAS],
        "historial": HISTORIAL_BUSQUEDAS,
        "estadisticas": obtener_estadisticas(),
    }

    with open(nombre_archivo, "w") as f:
        json.dump(data, f)

    return nombre_archivo


def importar_de_json(nombre_archivo: str) -> None:
    """Importa favoritas/historial desde un JSON previamente exportado."""
    global PELICULAS_FAVORITAS, HISTORIAL_BUSQUEDAS

    nombre_archivo = validation.valida_nombre_archivo(nombre_archivo)
    with open(nombre_archivo, "r") as f:
        data = json.load(f)

    PELICULAS_FAVORITAS = [movie_module.Movie.from_omdb(item) for item in data.get("favoritas", [])]
    HISTORIAL_BUSQUEDAS = data.get("historial", [])