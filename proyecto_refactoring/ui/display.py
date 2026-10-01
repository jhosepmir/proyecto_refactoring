"""ui/display.py - Presentacion: TODAS las salidas por consola.

Es el unico modulo con prints de resultados/mensajes/errores. La capa de
servicios no imprime nada y el menu delega aqui cualquier salida hacia el
usuario, incluidos los mensajes amigables de las excepciones de la app.
"""
import constants
from models.movie import Movie
from models.series import Series


def print_separator() -> None:
    """Imprime un separador."""
    print(constants.SEPARATOR_CHAR * constants.SEPARATOR_WIDTH)


def print_header(text: str) -> None:
    """Imprime un header centrado."""
    print_separator()
    print(text.upper().center(constants.SEPARATOR_WIDTH))
    print_separator()


def mostrar_mensaje(texto: str) -> None:
    """Imprime un mensaje simple."""
    print(texto)


def mostrar_pelicula(pelicula: Movie) -> None:
    """Muestra los detalles de una pelicula."""
    print_separator()
    print(f"Título: {pelicula.title}")
    print(f"Año: {pelicula.year}")
    print(f"Rating IMDB: {pelicula.imdb_rating}")
    print(f"Género: {pelicula.genre}")
    print(f"Director: {pelicula.director}")
    print(f"Actores: {pelicula.actors}")
    print(f"Trama: {pelicula.plot}")
    print(f"País: {pelicula.country}")
    print(f"Premios: {pelicula.awards}")
    print_separator()


def mostrar_serie(serie: Series) -> None:
    """Muestra los detalles de una serie."""
    print_separator()
    print(f"Nombre: {serie.name if serie.name is not None else 'N/A'}")
    print(f"Idioma: {serie.language if serie.language is not None else 'N/A'}")
    print(f"Géneros: {serie.genres}")
    print(f"Rating: {serie.rating}")
    print(f"Estado: {serie.status if serie.status is not None else 'N/A'}")
    print(f"Estreno: {serie.premiered if serie.premiered is not None else 'N/A'}")
    print(f"Final: {serie.ended if serie.ended is not None else 'N/A'}")
    print(f"Episodios: {serie.runtime if serie.runtime is not None else 'N/A'}")
    print(f"Resumen: {serie.summary[: constants.SUMMARY_MAX_LENGTH]}...")
    print_separator()


def mostrar_lista_peliculas(peliculas: list[Movie]) -> None:
    """Muestra una lista numerada de peliculas."""
    i = 0
    while i < len(peliculas):
        pelicula = peliculas[i]
        if pelicula.rating is not None:
            print(f"{i + 1}. {pelicula.title} ({pelicula.year}) - {pelicula.rating}")
        elif pelicula.title is not None:
            print(f"{i + 1}. {pelicula.title} ({pelicula.year})")
        else:
            print(f"{i + 1}. Película desconocida")
        i += 1


def mostrar_lista_series(series: list[Series]) -> None:
    """Muestra una lista numerada de series (nombre y estado)."""
    i = 0
    while i < len(series):
        nombre = series[i].name if series[i].name is not None else ""
        estado = series[i].status if series[i].status is not None else ""
        print(f"{i + 1}. {nombre} ({estado})")
        i += 1


def mostrar_favoritas(favoritas: list[Movie]) -> None:
    """Muestra la lista numerada de favoritas."""
    i = 0
    while i < len(favoritas):
        print(f"{i + 1}. {favoritas[i].title}")
        i += 1


def mostrar_historial(historial: list[dict]) -> None:
    """Muestra la lista numerada del historial."""
    i = 0
    while i < len(historial):
        print(f"{i + 1}. {historial[i]['titulo']}")
        i += 1


def mostrar_estadisticas(stats: dict[str, int]) -> None:
    """Muestra las estadisticas."""
    print(f"Total favoritas: {stats['total_favoritas']}")
    print(f"Total historial: {stats['total_historial']}")


def mostrar_configuracion(config: dict) -> None:
    """Muestra la configuracion de depuracion."""
    print(f"1. Debug: {config['debug']}")
    print(f"2. Verbose: {config['verbose']}")
    print(f"3. Timeout: {config['timeout']}")


def mostrar_generos_disponibles() -> None:
    """Muestra los generos disponibles."""
    print("Géneros disponibles: acción, comedia")


def mostrar_buscando() -> None:
    """Muestra el mensaje de busqueda de peliculas."""
    print("Buscando...")


def mostrar_buscando_actor() -> None:
    """Muestra el mensaje de busqueda por actor."""
    print("Buscando películas del actor...")


def mostrar_buscando_series() -> None:
    """Muestra el mensaje de busqueda de series."""
    print("Buscando series...")


def mostrar_pelicula_agregada() -> None:
    """Confirma la adicion de una favorita."""
    print("¡Agregada a favoritos!")


def mostrar_pelicula_ya_en_favoritas() -> None:
    """Informa que la pelicula ya era favorita."""
    print("Ya está en favoritos")


def mostrar_favorita_eliminada() -> None:
    """Confirma la eliminacion de una favorita."""
    print("Eliminada de favoritos")


def mostrar_historial_limpiado() -> None:
    """Confirma el borrado del historial."""
    print("Historial limpiado")


def mostrar_exportado(nombre_archivo: str) -> None:
    """Confirma la exportacion a JSON."""
    print(f"Exportado a {nombre_archivo}")


def mostrar_importado(nombre_archivo: str) -> None:
    """Confirma la importacion desde JSON."""
    print(f"Importado desde {nombre_archivo}")


def mostrar_error_importacion() -> None:
    """Informa de un error al importar."""
    print("Error al importar archivo")


def mostrar_error_exportacion() -> None:
    """Informa de un error al exportar."""
    print("Error al exportar archivo")


def mostrar_error_pelicula_no_encontrada() -> None:
    """Informa que la pelicula no existe."""
    print("No se encontró la película")


def mostrar_error_serie_no_encontrada() -> None:
    """Informa que la serie no existe."""
    print("No se encontró la serie")


def mostrar_error_api() -> None:
    """Informa de un fallo al consultar una API externa."""
    print("Error al consultar la API. Intente nuevamente más tarde.")


def mostrar_error_configuracion() -> None:
    """Informa de un fallo de configuracion interna."""
    print("Error de configuración de la aplicación.")


def mostrar_error_inesperado() -> None:
    """Informa de un error no anticipado (registrado en el log)."""
    print("Ocurrió un error inesperado. Revise el log para más detalles.")


def mostrar_sin_peliculas_actor() -> None:
    """Informa que no hay peliculas para el actor."""
    print("No se encontraron películas para ese actor")


def mostrar_sin_series() -> None:
    """Informa que no hay series."""
    print("No se encontraron series")


def mostrar_sin_favoritas() -> None:
    """Informa que no hay favoritas."""
    print("No tienes películas favoritas")


def mostrar_sin_historial() -> None:
    """Informa que no hay historial."""
    print("No hay historial")


def mostrar_opcion_invalida() -> None:
    """Informa de una opcion no valida."""
    print("Opción inválida")


def mostrar_despedida() -> None:
    """Mensaje de despedida al salir."""
    print("¡Hasta luego!")


def mostrar_debug_ahora(valor: bool) -> None:
    """Muestra el nuevo valor de debug."""
    print(f"Debug ahora es: {valor}")


def mostrar_verbose_ahora(valor: bool) -> None:
    """Muestra el nuevo valor de verbose."""
    print(f"Verbose ahora es: {valor}")