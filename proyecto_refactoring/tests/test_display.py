"""Tests de la capa de presentacion (ui.display) con capsys."""
import constants
import ui.display as display
from models.movie import Movie
from models.series import Series


def test_print_separator(capsys):
    display.print_separator()
    assert capsys.readouterr().out == constants.SEPARATOR_CHAR * constants.SEPARATOR_WIDTH + "\n"


def test_print_header_centra_en_mayusculas(capsys):
    display.print_header("Título de Prueba")
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 3
    assert lines[0] == constants.SEPARATOR_CHAR * constants.SEPARATOR_WIDTH
    assert lines[1] == "TÍTULO DE PRUEBA".center(constants.SEPARATOR_WIDTH)


def test_mostrar_pelicula(capsys):
    movie = Movie.from_omdb(
        {"Title": "Inception", "Year": "2010", "imdbRating": "8.8", "Genre": "Sci-Fi"}
    )
    display.mostrar_pelicula(movie)
    out = capsys.readouterr().out
    assert "Título: Inception" in out
    assert "Año: 2010" in out
    assert "Rating IMDB: 8.8" in out
    assert "Género: Sci-Fi" in out
    assert "Director: N/A" in out
    assert "Premios: N/A" in out


def test_mostrar_serie_recorta_resumen_a_200(capsys):
    serie = Series.from_tvmaze(
        {
            "id": 169,
            "name": "Breaking Bad",
            "language": "English",
            "genres": ["Drama"],
            "rating": {"average": 9.5},
            "status": "Ended",
            "premiered": "2008-01-20",
            "ended": "2013-09-29",
            "runtime": 47,
            "summary": "x" * 300,
        }
    )
    display.mostrar_serie(serie)
    out = capsys.readouterr().out
    assert "Nombre: Breaking Bad" in out
    assert "Idioma: English" in out
    assert "Géneros: ['Drama']" in out
    assert "Rating: 9.5" in out
    assert "Estado: Ended" in out
    assert "Episodios: 47" in out
    assert f"Resumen: {'x' * constants.SUMMARY_MAX_LENGTH}..." in out


def test_mostrar_serie_campos_ausentes_n_na(capsys):
    display.mostrar_serie(Series.from_tvmaze({}))
    out = capsys.readouterr().out
    assert "Nombre: N/A" in out
    assert "Idioma: N/A" in out
    assert "Resumen: N/A..." in out


def test_mostrar_lista_peliculas_catalogo_y_omdb(capsys):
    catalogo = Movie.from_catalog({"titulo": "Die Hard", "anio": 1988, "rating": 8.2})
    omdb_movie = Movie.from_omdb({"Title": "Mission: Impossible", "Year": "1996"})
    display.mostrar_lista_peliculas([catalogo, omdb_movie])
    out = capsys.readouterr().out
    assert "1. Die Hard (1988) - 8.2" in out
    assert "2. Mission: Impossible (1996)" in out


def test_mostrar_lista_series_con_defaults_vacios(capsys):
    display.mostrar_lista_series(
        [
            Series.from_tvmaze({"show": {"name": "Breaking Bad", "status": "Ended"}}),
            Series.from_tvmaze({}),
        ]
    )
    out = capsys.readouterr().out
    assert "1. Breaking Bad (Ended)" in out
    assert "2.  ()" in out


def test_mostrar_favoritas_historial_estadisticas_config(capsys):
    display.mostrar_favoritas([Movie.from_omdb({"Title": "Inception"})])
    assert "1. Inception" in capsys.readouterr().out

    display.mostrar_historial([{"titulo": "Inception", "fecha": "hoy"}])
    assert "1. Inception" in capsys.readouterr().out

    display.mostrar_estadisticas({"total_favoritas": 1, "total_historial": 2})
    out = capsys.readouterr().out
    assert "Total favoritas: 1" in out
    assert "Total historial: 2" in out

    display.mostrar_configuracion({"debug": True, "verbose": False, "timeout": 30, "max_retries": 3})
    out = capsys.readouterr().out
    assert "1. Debug: True" in out
    assert "2. Verbose: False" in out
    assert "3. Timeout: 30" in out


def test_mensajes_de_confirmacion_y_error(capsys):
    display.mostrar_despedida()
    display.mostrar_opcion_invalida()
    display.mostrar_pelicula_agregada()
    display.mostrar_pelicula_ya_en_favoritas()
    display.mostrar_favorita_eliminada()
    display.mostrar_historial_limpiado()
    display.mostrar_exportado("a.json")
    display.mostrar_importado("a.json")
    display.mostrar_error_importacion()
    display.mostrar_error_exportacion()
    display.mostrar_error_pelicula_no_encontrada()
    display.mostrar_error_serie_no_encontrada()
    display.mostrar_error_api()
    display.mostrar_error_configuracion()
    display.mostrar_error_inesperado()
    display.mostrar_sin_peliculas_actor()
    display.mostrar_sin_series()
    display.mostrar_sin_favoritas()
    display.mostrar_sin_historial()
    display.mostrar_buscando()
    display.mostrar_buscando_actor()
    display.mostrar_buscando_series()
    display.mostrar_generos_disponibles()
    display.mostrar_debug_ahora(False)
    display.mostrar_verbose_ahora(True)
    out = capsys.readouterr().out
    assert "¡Hasta luego!" in out
    assert "Opción inválida" in out
    assert "¡Agregada a favoritos!" in out
    assert "Ya está en favoritos" in out
    assert "Eliminada de favoritos" in out
    assert "Historial limpiado" in out
    assert "Exportado a a.json" in out
    assert "Importado desde a.json" in out
    assert "Error al importar archivo" in out
    assert "Error al exportar archivo" in out
    assert "No se encontró la película" in out
    assert "No se encontró la serie" in out
    assert "Error al consultar la API. Intente nuevamente más tarde." in out
    assert "Error de configuración de la aplicación." in out
    assert "Ocurrió un error inesperado. Revise el log para más detalles." in out
    assert "No se encontraron películas para ese actor" in out
    assert "No se encontraron series" in out
    assert "No tienes películas favoritas" in out
    assert "No hay historial" in out
    assert "Buscando..." in out
    assert "Buscando películas del actor..." in out
    assert "Géneros disponibles: acción, comedia" in out
    assert "Debug ahora es: False" in out
    assert "Verbose ahora es: True" in out