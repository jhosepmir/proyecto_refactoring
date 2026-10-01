import requests
import json
import sys
import os
import time
import random

import constants
import config

# Variables globales
API_KEY = config.CONFIG["api_key_omdb"]
OMDB_BASE_URL = constants.BASE_URL_OMDB
TVMAZE_BASE_URL = constants.BASE_URL_TVMAZE
CACHE = {}
USUARIO_ACTUAL = None
PELICULAS_FAVORITAS = []
HISTORIAL = []

# Funciones de utilidad (mezcladas con lógica de negocio)
def print_sep():
    print(constants.SEPARATOR_CHAR * constants.SEPARATOR_WIDTH_COMPACT)

def print_header(text):
    print_sep()
    print(text.upper())
    print_sep()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def delay(seconds):
    time.sleep(seconds)

# Funciones de API (sin manejo de errores, sin logging, sin validación)
def buscar_pelicula_omdb(titulo):
    global CACHE
    if titulo in CACHE:
        print("Usando cache...")
        return CACHE[titulo]
    
    url = f"{OMDB_BASE_URL}?t={titulo}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if data.get(constants.OMDB_RESPONSE_KEY) == constants.OMDB_SUCCESS:
        CACHE[titulo] = data
        return data
    else:
        return None

def buscar_series_tvmaze(nombre):
    global CACHE
    cache_key = f"{constants.CACHE_KEY_PREFIX_SERIES}{nombre}"
    if cache_key in CACHE:
        print("Usando cache de series...")
        return CACHE[cache_key]
    
    url = f"{TVMAZE_BASE_URL}/search/shows?q={nombre}"
    response = requests.get(url)
    data = response.json()
    
    CACHE[cache_key] = data
    return data

def obtener_detalles_serie_tvmaze(id_serie):
    url = f"{TVMAZE_BASE_URL}/shows/{id_serie}"
    response = requests.get(url)
    return response.json()

def buscar_peliculas_por_actor(nombre_actor):
    url = f"{OMDB_BASE_URL}?s={nombre_actor}&type=movie&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if data.get(constants.OMDB_RESPONSE_KEY) == constants.OMDB_SUCCESS:
        return data.get(constants.OMDB_SEARCH_KEY, [])
    return []

def obtener_peliculas_populares():
    # Simular películas populares con datos hardcodeados
    return [dict(pelicula) for pelicula in constants.POPULAR_MOVIES]

# Funciones de presentación (mezcladas con lógica)
def mostrar_pelicula(pelicula):
    print_sep()
    if pelicula is None:
        print("No se encontró la película")
        return
    
    print(f"Título: {pelicula.get('Title', 'N/A')}")
    print(f"Año: {pelicula.get('Year', 'N/A')}")
    print(f"Rating: {pelicula.get('imdbRating', 'N/A')}")
    print(f"Género: {pelicula.get('Genre', 'N/A')}")
    print(f"Director: {pelicula.get('Director', 'N/A')}")
    print(f"Trama: {pelicula.get('Plot', 'N/A')}")
    print_sep()

def mostrar_serie(serie):
    print_sep()
    show = serie.get("show", serie)
    print(f"Nombre: {show.get('name', 'N/A')}")
    print(f"Idioma: {show.get('language', 'N/A')}")
    print(f"Géneros: {show.get('genres', [])}")
    print(f"Rating: {show.get('rating', {}).get('average', 'N/A')}")
    print(f"Estado: {show.get('status', 'N/A')}")
    print_sep()

def mostrar_lista_peliculas(peliculas):
    i = 0
    while i < len(peliculas):
        print(f"{i + 1}. {peliculas[i].get('titulo', peliculas[i].get('Title', 'Sin título'))}")
        i += 1

# Funciones de menú
def menu_principal():
    while True:
        clear_screen()
        print_header("SISTEMA DE PELÍCULAS")
        print("1. Buscar película por título")
        print("2. Buscar por actor")
        print("3. Buscar series")
        print("4. Ver películas populares")
        print("5. Ver favoritos")
        print("6. Ver historial")
        print("7. Salir")
        
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
            funcion_ver_favoritos()
        elif opcion == "6":
            funcion_ver_historial()
        elif opcion == "7":
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida")
            delay(1)

def funcion_buscar_pelicula():
    titulo = input("Ingrese el título de la película: ")
    print("Buscando...")
    delay(1)  # Simular carga
    
    pelicula = buscar_pelicula_omdb(titulo)
    mostrar_pelicula(pelicula)
    
    if pelicula:
        HISTORIAL.append(pelicula.get("Title"))
        opcion = input("\n¿Agregar a favoritos? (s/n): ")
        if opcion.lower() == "s":
            PELICULAS_FAVORITAS.append(pelicula)
            print("Agregada a favoritos!")
    
    input("\nPresione Enter para continuar...")

def funcion_buscar_actor():
    actor = input("Ingrese el nombre del actor: ")
    print("Buscando películas del actor...")
    
    peliculas = buscar_peliculas_por_actor(actor)
    
    if len(peliculas) > 0:
        i = 0
        while i < len(peliculas):
            print(f"{i + 1}. {peliculas[i].get('Title', '')} ({peliculas[i].get('Year', '')})")
            i += 1
        
        opcion = input("\nSeleccione una película para ver detalles (0 para volver): ")
        if opcion.isdigit() and int(opcion) > 0:
            indice = int(opcion) - 1
            if indice < len(peliculas):
                detalles = buscar_pelicula_omdb(peliculas[indice].get("Title"))
                mostrar_pelicula(detalles)
    else:
        print("No se encontraron películas para ese actor")
    
    input("\nPresione Enter para continuar...")

def funcion_buscar_series():
    nombre = input("Ingrese el nombre de la serie: ")
    print("Buscando series...")
    
    series = buscar_series_tvmaze(nombre)
    
    if len(series) > 0:
        i = 0
        while i < len(series):
            show = series[i].get("show", {})
            print(f"{i + 1}. {show.get('name', '')} ({show.get('status', '')})")
            i += 1
        
        opcion = input("\nSeleccione una serie para ver detalles (0 para volver): ")
        if opcion.isdigit() and int(opcion) > 0:
            indice = int(opcion) - 1
            if indice < len(series):
                id_serie = series[indice].get("show", {}).get("id")
                detalles = obtener_detalles_serie_tvmaze(id_serie)
                mostrar_serie(detalles)
    else:
        print("No se encontraron series")
    
    input("\nPresione Enter para continuar...")

def funcion_peliculas_populares():
    print_header("PELÍCULAS POPULARES")
    peliculas = obtener_peliculas_populares()
    mostrar_lista_peliculas(peliculas)
    input("\nPresione Enter para continuar...")

def funcion_ver_favoritos():
    print_header("MIS FAVORITOS")
    if len(PELICULAS_FAVORITAS) > 0:
        i = 0
        while i < len(PELICULAS_FAVORITAS):
            print(f"{i + 1}. {PELICULAS_FAVORITAS[i].get('Title', '')}")
            i += 1
    else:
        print("No tienes películas favoritas")
    input("\nPresione Enter para continuar...")

def funcion_ver_historial():
    print_header("HISTORIAL DE BÚSQUEDAS")
    if len(HISTORIAL) > 0:
        i = 0
        while i < len(HISTORIAL):
            print(f"{i + 1}. {HISTORIAL[i]}")
            i += 1
    else:
        print("No hay historial")
    input("\nPresione Enter para continuar...")

# Programa principal
if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido")
        sys.exit(0)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)
