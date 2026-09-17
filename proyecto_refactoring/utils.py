import os
import sys
import time
import random
from datetime import datetime

import constants

# Variables globales
RESULTS_DIR = constants.RESULTS_DIR
EXPORT_DIR = constants.EXPORT_DIR

def init_dirs():
    """Inicializa directorios"""
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

def clear_screen():
    """Limpia pantalla"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_separator(char=constants.SEPARATOR_CHAR, length=constants.SEPARATOR_WIDTH):
    """Imprime separador"""
    print(char * length)

def print_header(text):
    """Imprime header"""
    print_separator()
    print(text.upper().center(constants.SEPARATOR_WIDTH))
    print_separator()

def print_subheader(text):
    """Imprime subheader"""
    print_separator("-", 40)
    print(text.center(40))
    print_separator("-", 40)

def delay(seconds):
    """Delay innecesario"""
    time.sleep(seconds)

def get_user_input(prompt, input_type=str):
    """Obtiene input del usuario"""
    while True:
        try:
            user_input = input(prompt)
            if input_type == int:
                return int(user_input)
            elif input_type == float:
                return float(user_input)
            else:
                return user_input
        except ValueError:
            print("Entrada inválida. Intente de nuevo.")

def format_movie_display(movie):
    """Formatea película para mostrar"""
    lines = []
    lines.append(constants.SEPARATOR_CHAR * constants.SEPARATOR_WIDTH_COMPACT)
    
    if movie is None:
        lines.append("No se encontró la película")
        lines.append(constants.SEPARATOR_CHAR * constants.SEPARATOR_WIDTH_COMPACT)
        return "\n".join(lines)
    
    try:
        lines.append(f"Título: {movie['Title']}")
    except:
        lines.append("Título: N/A")
    
    try:
        lines.append(f"Año: {movie['Year']}")
    except:
        lines.append("Año: N/A")
    
    try:
        lines.append(f"Rating IMDB: {movie['imdbRating']}")
    except:
        lines.append("Rating: N/A")
    
    try:
        lines.append(f"Género: {movie['Genre']}")
    except:
        lines.append("Género: N/A")
    
    try:
        lines.append(f"Director: {movie['Director']}")
    except:
        lines.append("Director: N/A")
    
    try:
        lines.append(f"Actores: {movie['Actors']}")
    except:
        lines.append("Actores: N/A")
    
    try:
        lines.append(f"Trama: {movie['Plot']}")
    except:
        lines.append("Trama: N/A")
    
    try:
        lines.append(f"Idioma: {movie['Language']}")
    except:
        lines.append("Idioma: N/A")
    
    try:
        lines.append(f"País: {movie['Country']}")
    except:
        lines.append("País: N/A")
    
    try:
        lines.append(f"Premios: {movie['Awards']}")
    except:
        lines.append("Premios: N/A")
    
    try:
        lines.append(f"Poster: {movie['Poster']}")
    except:
        lines.append("Poster: N/A")
    
    lines.append(constants.SEPARATOR_CHAR * constants.SEPARATOR_WIDTH_COMPACT)
    
    return "\n".join(lines)

def format_series_display(series):
    """Formatea serie para mostrar"""
    lines = []
    lines.append(constants.SEPARATOR_CHAR * constants.SEPARATOR_WIDTH_COMPACT)
    
    show = series.get("show", series)
    
    lines.append(f"Nombre: {show.get('name', 'N/A')}")
    lines.append(f"Idioma: {show.get('language', 'N/A')}")
    lines.append(f"Géneros: {show.get('genres', [])}")
    lines.append(f"Rating: {show.get('rating', {}).get('average', 'N/A')}")
    lines.append(f"Estado: {show.get('status', 'N/A')}")
    lines.append(f"Estreno: {show.get('premiered', 'N/A')}")
    lines.append(f"Final: {show.get('ended', 'N/A')}")
    lines.append(f"Episodios: {show.get('runtime', 'N/A')}")
    
    summary = str(show.get("summary", "N/A"))
    if len(summary) > constants.SUMMARY_MAX_LENGTH:
        summary = f"{summary[:constants.SUMMARY_MAX_LENGTH]}..."
    lines.append(f"Resumen: {summary}")
    
    lines.append(constants.SEPARATOR_CHAR * constants.SEPARATOR_WIDTH_COMPACT)
    
    return "\n".join(lines)

def format_list_display(items, item_type="pelicula"):
    """Formatea lista para mostrar"""
    lines = []
    
    if len(items) == 0:
        lines.append(f"No se encontraron {item_type}s")
        return "\n".join(lines)
    
    i = 0
    while i < len(items):
        if "titulo" in items[i]:
            lines.append(f"{i + 1}. {items[i]['titulo']} ({items[i].get('anio', '')})")
        elif "Title" in items[i]:
            lines.append(f"{i + 1}. {items[i]['Title']} ({items[i].get('Year', 'N/A')})")
        elif "name" in items[i]:
            lines.append(f"{i + 1}. {items[i]['name']}")
        else:
            lines.append(f"{i + 1}. Elemento desconocido")
        i += 1
    
    return "\n".join(lines)

def save_results(results, filename):
    """Guarda resultados a archivo"""
    filepath = os.path.join(RESULTS_DIR, filename)
    with open(filepath, 'w') as f:
        if isinstance(results, list):
            for item in results:
                f.write(f"{item}\n")
        else:
            f.write(str(results))
    return filepath

def export_to_json(data, filename):
    """Exporta datos a JSON"""
    import json
    
    filepath = os.path.join(EXPORT_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    return filepath

def export_to_csv(data, filename):
    """Exporta datos a CSV"""
    import csv
    
    filepath = os.path.join(EXPORT_DIR, filename)
    with open(filepath, 'w', newline='') as f:
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict):
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
    return filepath

def create_menu(options):
    """Crea menú dinámico"""
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print("0. Salir")

def handle_menu_choice(choice, handlers):
    """Maneja selección de menú"""
    if choice in handlers:
        handlers[choice]()
        return True
    elif choice == 0:
        return False
    else:
        print("Opción inválida")
        return True

def generate_random_id():
    """Genera ID aleatorio"""
    return str(random.randint(1000, 9999))

def get_timestamp():
    """Obtiene timestamp actual"""
    return datetime.now().strftime(constants.DATETIME_FORMAT)

def validate_email(email):
    """Valida email (de forma simple)"""
    return "@" in email and "." in email

def validate_date(date_str):
    """Valida formato de fecha"""
    try:
        datetime.strptime(date_str, constants.DATE_FORMAT)
        return True
    except:
        return False

def format_date(date_obj):
    """Formatea fecha"""
    if isinstance(date_obj, datetime):
        return date_obj.strftime(constants.DATETIME_FORMAT)
    return str(date_obj)

def truncate_text(text, max_length=100):
    """Trunca texto"""
    if len(text) > max_length:
        return f"{text[:max_length]}..."
    return text

def remove_duplicates(items):
    """Elimina duplicados (de forma ineficiente)"""
    unique_items = []
    for item in items:
        if item not in unique_items:
            unique_items.append(item)
    return unique_items

def sort_items(items, key, reverse=False):
    """Ordena elementos"""
    try:
        return sorted(items, key=lambda x: x.get(key, ""), reverse=reverse)
    except:
        return items

def filter_items(items, key, value):
    """Filtra elementos"""
    filtered = []
    for item in items:
        if item.get(key) == value:
            filtered.append(item)
    return filtered

# Inicializar directorios
init_dirs()
