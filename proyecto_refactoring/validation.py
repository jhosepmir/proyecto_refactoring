"""validation.py - Validacion de entradas de usuario (SEGURIDAD, FASE 5).

Rechaza entradas vacias, abusos de longitud y nombres de archivo con rutas
(traversal) o caracteres no seguros. Los errores se expresan como
InputValidationError para que la capa UI los muestre de forma amigable.
"""
import re

from exceptions.validation_error import InputValidationError

MAX_INPUT_LENGTH = 200
NOMBRE_ARCHIVO_VALIDO = re.compile(r"^[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*$")

MENSAJE_VACIO = "Ingrese un valor válido."
MENSAJE_LARGO = "Valor demasiado largo."
MENSAJE_ARCHIVO = "Nombre de archivo inválido."
MENSAJE_TIMEOUT = "Valor inválido para timeout. No se cambió."


def requiere_no_vacio(campo: str, valor: str) -> str:
    """Recorta espacios y exige un valor no vacio, con limite de longitud."""
    limpio = (valor or "").strip()
    if not limpio:
        raise InputValidationError(f"{campo}: {MENSAJE_VACIO}")
    if len(limpio) > MAX_INPUT_LENGTH:
        raise InputValidationError(f"{campo}: {MENSAJE_LARGO}")
    return limpio


def valida_nombre_archivo(nombre: str) -> str:
    """Exige un nombre de archivo simple (sin rutas ni traversal).

    Permite letras/digitos/guiones/puntos pero debe empezar y terminar en
    alfanumerico. Bloquea separadores de ruta (/, \\), '..', nombres de solo
    puntos, puntos iniciales/finales y caracteres de control.
    """
    limpio = requiere_no_vacio("Nombre del archivo", nombre)
    if not NOMBRE_ARCHIVO_VALIDO.fullmatch(limpio):
        raise InputValidationError(MENSAJE_ARCHIVO)
    return limpio


def requiere_timeout(valor: str) -> int:
    """Parsea un timeout entero positivo; rechaza 0, negativos y no numeros."""
    limpio = (valor or "").strip()
    try:
        timeout = int(limpio)
    except ValueError as exc:
        raise InputValidationError(MENSAJE_TIMEOUT) from exc
    if timeout <= 0:
        raise InputValidationError(MENSAJE_TIMEOUT)
    return timeout