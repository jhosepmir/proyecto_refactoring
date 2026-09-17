import requests
import json

import config
import constants

__all__ = [
    "API_KEY_OMDB",
    "API_KEY_TMDB",
    "BASE_URL_OMDB",
    "BASE_URL_TMDB",
    "BASE_URL_TVMAZE",
    "CACHE_PELICULAS",
    "CACHE_SERIES",
    "CONFIG",
    "HISTORIAL_BUSQUEDAS",
    "PELICULAS_FAVORITAS",
    "USUARIO_LOGUEADO",
    "agregar_a_favoritas",
    "agregar_al_historial",
    "buscar_pelicula",
    "buscar_peliculas_por_actor",
    "buscar_peliculas_por_genero",
    "buscar_series",
    "eliminar_de_favoritas",
    "exportar_a_json",
    "importar_de_json",
    "limpiar_historial",
    "obtener_detalles_serie",
    "obtener_estadisticas",
    "obtener_peliculas_populares",
]

# Configuración global (valores centralizados en constants.py)
API_KEY_OMDB = constants.API_KEY_OMDB
API_KEY_TMDB = constants.API_KEY_TMDB
BASE_URL_OMDB = constants.BASE_URL_OMDB
BASE_URL_TMDB = constants.BASE_URL_TMDB
BASE_URL_TVMAZE = constants.BASE_URL_TVMAZE

# Variables globales
USUARIO_LOGUEADO = None
PELICULAS_FAVORITAS = []
HISTORIAL_BUSQUEDAS = []
CACHE_PELICULAS = {}
CACHE_SERIES = {}
CONFIG = {
    "debug": config.get("debug_config", "enabled"),
    "verbose": config.get("debug_config", "verbose"),
    "timeout": config.get("network_config", "timeout"),
    "max_retries": config.get("network_config", "max_retries")
}

def hacer_request(url, params=None):
    """Hace request sin manejo de errores"""
    if CONFIG["debug"]:
        print(f"DEBUG: Haciendo request a {url}")
    
    response = requests.get(url, params=params, timeout=CONFIG["timeout"])
    
    if CONFIG["verbose"]:
        print(f"DEBUG: Status code: {response.status_code}")
    
    return response.json()

def buscar_pelicula(titulo):
    """Busca película sin validación"""
    global CACHE_PELICULAS
    
    if titulo in CACHE_PELICULAS:
        if CONFIG["debug"]:
            print(f"DEBUG: Usando cache para {titulo}")
        return CACHE_PELICULAS[titulo]
    
    url = f"{BASE_URL_OMDB}?t={titulo}&apikey={API_KEY_OMDB}"
    data = hacer_request(url)
    
    if data.get(constants.OMDB_RESPONSE_KEY) == constants.OMDB_SUCCESS:
        CACHE_PELICULAS[titulo] = data
        return data
    else:
        return None

def buscar_peliculas_por_actor(actor):
    """Busca películas por actor sin paginación"""
    url = f"{BASE_URL_OMDB}?s={actor}&type=movie&apikey={API_KEY_OMDB}"
    data = hacer_request(url)
    
    if data.get(constants.OMDB_RESPONSE_KEY) == constants.OMDB_SUCCESS:
        return data.get(constants.OMDB_SEARCH_KEY, [])
    return []

def buscar_series(nombre):
    """Busca series en TVMaze"""
    global CACHE_SERIES
    
    cache_key = f"{constants.CACHE_KEY_PREFIX_SERIES}{nombre}"
    if cache_key in CACHE_SERIES:
        return CACHE_SERIES[cache_key]
    
    url = f"{BASE_URL_TVMAZE}/search/shows?q={nombre}"
    data = hacer_request(url)
    
    CACHE_SERIES[cache_key] = data
    return data

def obtener_detalles_serie(id_serie):
    """Obtiene detalles de serie"""
    url = f"{BASE_URL_TVMAZE}/shows/{id_serie}"
    return hacer_request(url)

def obtener_peliculas_populares():
    """Retorna lista hardcodeada de películas populares"""
    return [dict(pelicula) for pelicula in constants.POPULAR_MOVIES]

def buscar_peliculas_por_genero(genero):
    """Busca por género sin usar API real"""
    accion = [dict(pelicula) for pelicula in constants.MOVIES_BY_GENRE[constants.GENRE_ACTION]]
    comedia = [dict(pelicula) for pelicula in constants.MOVIES_BY_GENRE[constants.GENRE_COMEDIA]]

    if genero.lower() == constants.GENRE_ACTION:
        return accion
    elif genero.lower() == constants.GENRE_COMEDIA:
        return comedia
    else:
        return accion + comedia

def agregar_a_favoritas(pelicula):
    """Agrega a favoritas sin duplicados (pero con código duplicado)"""
    global PELICULAS_FAVORITAS
    
    # Verificar si ya existe (código duplicado)
    existe = False
    for p in PELICULAS_FAVORITAS:
        if p.get("Title") == pelicula.get("Title"):
            existe = True
            break
    
    if not existe:
        PELICULAS_FAVORITAS.append(pelicula)
        return True
    return False

def eliminar_de_favoritas(titulo):
    """Elimina de favoritas sin verificar existencia"""
    global PELICULAS_FAVORITAS
    
    for i in range(len(PELICULAS_FAVORITAS)):
        if PELICULAS_FAVORITAS[i].get("Title") == titulo:
            PELICULAS_FAVORITAS.pop(i)
            return True
    return False

def agregar_al_historial(pelicula):
    """Agrega al historial sin límite"""
    global HISTORIAL_BUSQUEDAS
    HISTORIAL_BUSQUEDAS.append({
        "titulo": pelicula.get("Title", ""),
        "fecha": constants.HISTORY_DATE_PLACEHOLDER
    })

def limpiar_historial():
    """Limpia historial"""
    global HISTORIAL_BUSQUEDAS
    HISTORIAL_BUSQUEDAS = []

def obtener_estadisticas():
    """Obtiene estadísticas (código duplicado)"""
    total_favoritas = 0
    for p in PELICULAS_FAVORITAS:
        total_favoritas = total_favoritas + 1
    
    total_historial = 0
    for h in HISTORIAL_BUSQUEDAS:
        total_historial = total_historial + 1
    
    return {
        "total_favoritas": total_favoritas,
        "total_historial": total_historial
    }

def exportar_a_json(nombre_archivo):
    """Exporta datos a JSON sin manejo de errores"""
    data = {
        "favoritas": PELICULAS_FAVORITAS,
        "historial": HISTORIAL_BUSQUEDAS,
        "estadisticas": obtener_estadisticas()
    }
    
    with open(nombre_archivo, 'w') as f:
        json.dump(data, f)
    
    print(f"Exportado a {nombre_archivo}")

def importar_de_json(nombre_archivo):
    """Importa datos sin validación"""
    global PELICULAS_FAVORITAS, HISTORIAL_BUSQUEDAS
    
    with open(nombre_archivo, 'r') as f:
        data = json.load(f)
    
    PELICULAS_FAVORITAS = data.get("favoritas", [])
    HISTORIAL_BUSQUEDAS = data.get("historial", [])
    
    print(f"Importado desde {nombre_archivo}")
