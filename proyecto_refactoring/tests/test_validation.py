"""Tests de validation.py (SEGURIDAD - entrada de usuario)."""
import pytest

import validation
from exceptions.validation_error import InputValidationError


def test_requiere_no_vacio_ok():
    assert validation.requiere_no_vacio("Título", "  Inception  ") == "Inception"


def test_requiere_no_vacio_rechaza_vacio():
    with pytest.raises(InputValidationError):
        validation.requiere_no_vacio("Título", "")


def test_requiere_no_vacio_rechaza_solo_espacios():
    with pytest.raises(InputValidationError):
        validation.requiere_no_vacio("Título", "   ")


def test_requiere_no_vacio_rechaza_none():
    with pytest.raises(InputValidationError):
        validation.requiere_no_vacio("Título", None)


def test_requiere_no_vacio_rechaza_demasiado_largo():
    with pytest.raises(InputValidationError):
        validation.requiere_no_vacio("Título", "x" * 201)


def test_valida_nombre_archivo_ok():
    assert validation.valida_nombre_archivo("datos.json") == "datos.json"
    assert validation.valida_nombre_archivo("mis-favoritas_2024") == "mis-favoritas_2024"


@pytest.mark.parametrize(
    "nombre_invalido",
    [
        "..",
        "../secreto",
        "a/b",
        "a\\b",
        "/etc/passwd",
        ".oculto",
        "con espacio.txt",
        "caracter|raro.txt",
    ],
)
def test_valida_nombre_archivo_rechaza_peligrosos(nombre_invalido):
    with pytest.raises(InputValidationError):
        validation.valida_nombre_archivo(nombre_invalido)


def test_valida_nombre_archivo_rechaza_vacio():
    with pytest.raises(InputValidationError):
        validation.valida_nombre_archivo("")


def test_requiere_timeout_ok():
    assert validation.requiere_timeout("30") == 30


@pytest.mark.parametrize("timeout_invalido", ["", "abc", "0", "-5", "3.5"])
def test_requiere_timeout_rechaza_invalidos(timeout_invalido):
    with pytest.raises(InputValidationError):
        validation.requiere_timeout(timeout_invalido)


def test_requiere_timeout_recorta_espacios():
    assert validation.requiere_timeout(" 30 ") == 30