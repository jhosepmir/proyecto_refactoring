"""ui/menu.py - Interaccion con el usuario: prompts y navegacion.

Solo maneja input/validacion/orquestacion y delega toda salida en ui/display.
Los flujos exponen las excepciones de la app (ApplicationError) y un decorador
las traduce aqui a mensajes amigables + registro en log; la UI nunca muestra
borradores de excepciones ni trazas al usuario.
"""
import functools
import logging
import os
import time

import config
import constants
import services.library_service as library_service
import services.movie_service as movie_service
import services.series_service as series_service
import ui.display as display
import validation
from exceptions.api_error import APIError
from exceptions.application_error import ApplicationError
from exceptions.configuration_error import ConfigurationError
from exceptions.not_found import MovieNotFoundError, SeriesNotFoundError
from exceptions.validation_error import InputValidationError

logger = logging.getLogger(__name__)


def manejar_errores(funcion):
    """Envuelve un flujo del menu: traduce ApplicationError a la UI + log.

    Solo gestiona errores conocidos de la app; los inesperados se propagan a
    main() (ultima proteccion).
    """
    @functools.wraps(funcion)
    def envoltura(*args, **kwargs):
        try:
            return funcion(*args, **kwargs)
        except MovieNotFoundError as exc:
            logger.error("Pelicula no encontrada: %s", exc, exc_info=True)
            display.mostrar_error_pelicula_no_encontrada()
        except SeriesNotFoundError as exc:
            logger.error("Serie no encontrada: %s", exc, exc_info=True)
            display.mostrar_error_serie_no_encontrada()
        except ConfigurationError as exc:
            logger.error("Error de configuracion: %s", exc, exc_info=True)
            display.mostrar_error_configuracion()
        except InputValidationError as exc:
            logger.warning("Entrada invalida: %s", exc)
            display.mostrar_mensaje(str(exc))
        except APIError as exc:
            logger.error("Error de API: %s", exc, exc_info=True)
            display.mostrar_error_api()
        except ApplicationError as exc:
            logger.error("Error de aplicacion: %s", exc, exc_info=True)
            display.mostrar_error_inesperado()
    return envoltura


def clear_screen() -> None:
    """Limpia la pantalla."""
    os.system(constants.CLEAR_CMD_WINDOWS if os.name == "nt" else constants.CLEAR_CMD_POSIX)


def delay(seconds: float = constants.DEFAULT_DELAY_SECONDS) -> None:
    """Pausa breve para simular carga."""
    time.sleep(seconds)


@manejar_errores
def funcion_buscar_pelicula() -> None:
    """Flujo de busqueda de pelicula por titulo."""
    titulo = validation.requiere_no_vacio("Título", input("Ingrese el título de la película: "))
    display.mostrar_buscando()
    delay()

    pelicula = movie_service.buscar_pelicula(titulo)
    display.mostrar_pelicula(pelicula)

    library_service.agregar_al_historial(pelicula)
    opcion = input("\n¿Agregar a favoritos? (s/n): ")
    if opcion.lower() == "s":
        if library_service.agregar_a_favoritas(pelicula):
            display.mostrar_pelicula_agregada()
        else:
            display.mostrar_pelicula_ya_en_favoritas()


@manejar_errores
def funcion_buscar_actor() -> None:
    """Flujo de busqueda por actor."""
    actor = validation.requiere_no_vacio("Actor", input("Ingrese el nombre del actor: "))
    display.mostrar_buscando_actor()

    peliculas = movie_service.buscar_peliculas_por_actor(actor)

    if len(peliculas) > 0:
        display.mostrar_lista_peliculas(peliculas)

        opcion = input("\nSeleccione una película para ver detalles (0 para volver): ")
        if opcion.isdigit():
            indice = int(opcion) - 1
            if indice >= 0 and indice < len(peliculas):
                detalles = movie_service.buscar_pelicula(peliculas[indice].title)
                display.mostrar_pelicula(detalles)
    else:
        display.mostrar_sin_peliculas_actor()


@manejar_errores
def funcion_buscar_series() -> None:
    """Flujo de busqueda de series."""
    nombre = validation.requiere_no_vacio("Serie", input("Ingrese el nombre de la serie: "))
    display.mostrar_buscando_series()

    series = series_service.buscar_series(nombre)

    if len(series) > 0:
        display.mostrar_lista_series(series)

        opcion = input("\nSeleccione una serie para ver detalles (0 para volver): ")
        if opcion.isdigit():
            indice = int(opcion) - 1
            if indice >= 0 and indice < len(series):
                id_serie = series[indice].id
                detalles = series_service.obtener_detalles_serie(id_serie)
                display.mostrar_serie(detalles)
    else:
        display.mostrar_sin_series()


@manejar_errores
def funcion_peliculas_populares() -> None:
    """Flujo de peliculas populares."""
    display.print_header("PELÍCULAS POPULARES")
    peliculas = movie_service.obtener_peliculas_populares()
    display.mostrar_lista_peliculas(peliculas)


@manejar_errores
def funcion_buscar_por_genero() -> None:
    """Flujo de busqueda por genero."""
    display.mostrar_generos_disponibles()
    genero = validation.requiere_no_vacio("Género", input("Ingrese el género: "))
    display.mostrar_buscando()

    peliculas = movie_service.buscar_peliculas_por_genero(genero)
    display.mostrar_lista_peliculas(peliculas)


@manejar_errores
def funcion_ver_favoritos() -> None:
    """Flujo de favoritas."""
    display.print_header("MIS FAVORITOS")
    favoritas = library_service.obtener_favoritas()

    if len(favoritas) > 0:
        display.mostrar_favoritas(favoritas)

        opcion = input("\n¿Desea eliminar alguna? (número o Enter para volver): ")
        if opcion.isdigit():
            indice = int(opcion) - 1
            if indice >= 0 and indice < len(favoritas):
                if library_service.eliminar_de_favoritas(favoritas[indice].title):
                    display.mostrar_favorita_eliminada()
    else:
        display.mostrar_sin_favoritas()


@manejar_errores
def funcion_ver_historial() -> None:
    """Flujo de historial."""
    display.print_header("HISTORIAL DE BÚSQUEDAS")
    historial = library_service.obtener_historial()

    if len(historial) > 0:
        display.mostrar_historial(historial)

        opcion = input("\n¿Limpiar historial? (s/n): ")
        if opcion.lower() == "s":
            library_service.limpiar_historial()
            display.mostrar_historial_limpiado()
    else:
        display.mostrar_sin_historial()


@manejar_errores
def funcion_estadisticas() -> None:
    """Flujo de estadisticas."""
    display.print_header("ESTADÍSTICAS")
    stats = library_service.obtener_estadisticas()
    display.mostrar_estadisticas(stats)


@manejar_errores
def funcion_exportar() -> None:
    """Flujo de exportacion a JSON."""
    nombre = validation.valida_nombre_archivo(input("Nombre del archivo (sin extensión): "))
    try:
        archivo = library_service.exportar_a_json(f"{nombre}.json")
    except OSError as exc:
        logger.error("Error al exportar %s.json: %s", nombre, exc, exc_info=True)
        display.mostrar_error_exportacion()
    else:
        display.mostrar_exportado(archivo)


@manejar_errores
def funcion_importar() -> None:
    """Flujo de importacion desde JSON."""
    nombre = validation.valida_nombre_archivo(input("Nombre del archivo (sin extensión): "))
    try:
        library_service.importar_de_json(f"{nombre}.json")
        display.mostrar_importado(f"{nombre}.json")
    except (OSError, ValueError) as exc:
        logger.error("Error al importar %s.json: %s", nombre, exc, exc_info=True)
        display.mostrar_error_importacion()


@manejar_errores
def funcion_configuracion() -> None:
    """Flujo de configuracion de depuracion."""
    display.print_header("CONFIGURACIÓN")
    display.mostrar_configuracion(config.CONFIG)

    opcion = input("\nSeleccione opción a cambiar (0 para volver): ")
    if opcion == "1":
        config.CONFIG["debug"] = not config.CONFIG["debug"]
        display.mostrar_debug_ahora(config.CONFIG["debug"])
    elif opcion == "2":
        config.CONFIG["verbose"] = not config.CONFIG["verbose"]
        display.mostrar_verbose_ahora(config.CONFIG["verbose"])
    elif opcion == "3":
        config.CONFIG["timeout"] = validation.requiere_timeout(input("Nuevo timeout: "))


def menu_principal() -> None:
    """Menu principal de la aplicacion."""
    while True:
        clear_screen()
        display.print_header(constants.APP_NAME)
        for numero, etiqueta in constants.MENU_OPTIONS:
            print(f"{numero}. {etiqueta}")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            funcion_buscar_pelicula()
        elif opcion == "2":
            funcion_buscar_actor()
        elif opcion == "3":
            funcion_buscar_series()
        elif opcion == "4":
            funcion_peliculas_populares()
        elif opcion == "5":
            funcion_buscar_por_genero()
        elif opcion == "6":
            funcion_ver_favoritos()
        elif opcion == "7":
            funcion_ver_historial()
        elif opcion == "8":
            funcion_estadisticas()
        elif opcion == "9":
            funcion_exportar()
        elif opcion == "10":
            funcion_importar()
        elif opcion == "11":
            funcion_configuracion()
        elif opcion == "12":
            display.mostrar_despedida()
            break
        else:
            display.mostrar_opcion_invalida()
            delay()
            continue

        input(constants.PROMPT_CONTINUE)