"""constants.py - Valores hardcodeados centralizados del proyecto.

Antes estos valores estaban dispersos y duplicados en api_movies.py, app.py,
main.py, utils.py, *_manager.py y los defaults de *_config.py. Aqui se declaran
una sola vez para reutilizarlos y evitar divergencias.

Este modulo NO tiene dependencias internas ni efectos secundarios.
"""

# ---------------------------------------------------------------------------
# Aplicacion
# ---------------------------------------------------------------------------
APP_NAME = "SISTEMA DE PELÍCULAS Y SERIES"
APP_SHORT_NAME = "SISTEMA DE PELÍCULAS"
APP_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# API / red
# ---------------------------------------------------------------------------
# Las claves de API se leen de variables de entorno (config.CONFIG
# "api_key_omdb"); no hay claves hardcodeadas en este modulo.
BASE_URL_OMDB = "http://www.omdbapi.com/"
BASE_URL_TMDB = "https://api.themoviedb.org/3/"
BASE_URL_TVMAZE = "http://api.tvmaze.com"

DEFAULT_TIMEOUT = 30  # segundos
MAX_RETRIES = 3

# Nombres de parametros de query usados al construir URLs
PARAM_TITLE = "t"
PARAM_SEARCH = "s"
PARAM_TYPE = "type"
PARAM_APIKEY = "apikey"
PARAM_TYPE_MOVIE = "movie"

# Claves de respuesta de OMDb / TVMaze
OMDB_RESPONSE_KEY = "Response"
OMDB_SUCCESS = "True"
OMDB_SEARCH_KEY = "Search"
OMDB_ERROR_KEY = "Error"
TVMAZE_SHOW_KEY = "show"

# ---------------------------------------------------------------------------
# UI / consola
# ---------------------------------------------------------------------------
SEPARATOR_CHAR = "="
SEPARATOR_WIDTH = 60  # main.py / utils.py
SEPARATOR_WIDTH_COMPACT = 50  # app.py
NOT_AVAILABLE = "N/A"
SUMMARY_MAX_LENGTH = 200  # recorte del resumen de series
DEFAULT_DELAY_SECONDS = 1  # "Simular carga"
PROMPT_CONTINUE = "\nPresione Enter para continuar..."
CLEAR_CMD_WINDOWS = "cls"
CLEAR_CMD_POSIX = "clear"

# Etiquetas de campo para mostrar peliculas/series
MOVIE_FIELDS = (
    ("Título", "Title"),
    ("Año", "Year"),
    ("Rating IMDB", "imdbRating"),
    ("Género", "Genre"),
    ("Director", "Director"),
    ("Actores", "Actors"),
    ("Trama", "Plot"),
    ("País", "Country"),
    ("Premios", "Awards"),
)

SERIES_FIELDS = (
    ("Nombre", "name"),
    ("Idioma", "language"),
    ("Géneros", "genres"),
    ("Rating", "rating.average"),
    ("Estado", "status"),
    ("Estreno", "premiered"),
    ("Final", "ended"),
    ("Episodios", "runtime"),
    ("Resumen", "summary"),
)

# Opciones del menu principal (numero, texto)
MENU_OPTIONS = (
    (1, "Buscar película por título"),
    (2, "Buscar por actor"),
    (3, "Buscar series"),
    (4, "Ver películas populares"),
    (5, "Buscar por género"),
    (6, "Ver favoritos"),
    (7, "Ver historial"),
    (8, "Ver estadísticas"),
    (9, "Exportar datos"),
    (10, "Importar datos"),
    (11, "Configuración"),
    (12, "Salir"),
)

# ---------------------------------------------------------------------------
# Directorios y almacenamiento
# ---------------------------------------------------------------------------
DATA_DIR = "data"
RESULTS_DIR = "results"
EXPORT_DIR = "exports"
CACHE_DIR = "cache"
BACKUP_DIR = "backups"

CACHE_INDEX_FILE = "cache_index.json"
AUDIT_FILE = "audit_log.json"
FAVORITES_FILE = "favorites.json"
HISTORY_FILE = "history.json"
CONFIG_FILE = "config.json"

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
CACHE_EXPIRY_SECONDS = 3600  # 1 hora
CACHE_EXPIRY_HOURS = 24
CACHE_KEY_PREFIX_SERIES = "series_"
CACHE_KEY_SEPARATOR = "_"

# ---------------------------------------------------------------------------
# Backups / exportacion
# ---------------------------------------------------------------------------
MAX_BACKUPS = 10
JSON_EXTENSION = ".json"
JSON_INDENT = 4
BACKUP_SUFFIX = "_backup_"

# ---------------------------------------------------------------------------
# Formatos de fecha/hora
# ---------------------------------------------------------------------------
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
HISTORY_DATE_PLACEHOLDER = "hoy"  # fecha hardcodeada del historial original

# ---------------------------------------------------------------------------
# Dominio: peliculas/series hardcodeadas
# ---------------------------------------------------------------------------
GENRE_ACTION = "accion"
GENRE_COMEDIA = "comedia"

POPULAR_MOVIES = (
    {"titulo": "The Shawshank Redemption", "anio": 1994, "rating": 9.3},
    {"titulo": "The Godfather", "anio": 1972, "rating": 9.2},
    {"titulo": "The Dark Knight", "anio": 2008, "rating": 9.0},
    {"titulo": "Pulp Fiction", "anio": 1994, "rating": 8.9},
    {"titulo": "Forrest Gump", "anio": 1994, "rating": 8.8},
)

MOVIES_BY_GENRE = {
    GENRE_ACTION: (
        {"titulo": "Die Hard", "anio": 1988, "rating": 8.2},
        {"titulo": "Mad Max Fury Road", "anio": 2015, "rating": 8.1},
    ),
    GENRE_COMEDIA: (
        {"titulo": "Superbad", "anio": 2007, "rating": 7.6},
        {"titulo": "The Hangover", "anio": 2009, "rating": 7.7},
    ),
}

AVAILABLE_GENRES = (GENRE_ACTION, GENRE_COMEDIA)
