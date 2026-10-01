"""Tests del estado de usuario (services.library_service)."""
import json

import pytest

import services.library_service as library_service
from exceptions.validation_error import InputValidationError
from models.movie import Movie


@pytest.fixture(autouse=True)
def reset_library(tmp_path, monkeypatch):
    """Estado limpio y cwd aislado por test."""
    library_service.PELICULAS_FAVORITAS = []
    library_service.HISTORIAL_BUSQUEDAS = []
    monkeypatch.chdir(tmp_path)
    yield


def make_movie():
    return Movie.from_omdb({"Title": "Inception", "Year": "2010"})


def test_agregar_a_favoritas_dedup_por_titulo():
    assert library_service.agregar_a_favoritas(make_movie()) is True
    assert library_service.agregar_a_favoritas(make_movie()) is False
    assert len(library_service.PELICULAS_FAVORITAS) == 1


def test_eliminar_de_favoritas():
    library_service.agregar_a_favoritas(make_movie())
    assert library_service.eliminar_de_favoritas("Inception") is True
    assert library_service.eliminar_de_favoritas("Inception") is False
    assert len(library_service.PELICULAS_FAVORITAS) == 0


def test_historial():
    library_service.agregar_al_historial(make_movie())
    assert library_service.obtener_historial() == [{"titulo": "Inception", "fecha": "hoy"}]
    library_service.limpiar_historial()
    assert library_service.obtener_historial() == []


def test_obtener_favoritas_y_historial():
    library_service.agregar_a_favoritas(make_movie())
    assert [m.title for m in library_service.obtener_favoritas()] == ["Inception"]


def test_estadisticas():
    library_service.agregar_a_favoritas(make_movie())
    library_service.agregar_al_historial(make_movie())
    assert library_service.obtener_estadisticas() == {
        "total_favoritas": 1,
        "total_historial": 1,
    }


def test_exportar_serializa_dict_crudo():
    library_service.agregar_a_favoritas(make_movie())
    library_service.agregar_al_historial(make_movie())
    library_service.exportar_a_json("datos.json")
    with open("datos.json") as f:
        data = json.load(f)
    assert data["favoritas"] == [{"Title": "Inception", "Year": "2010"}]
    assert data["historial"] == [{"titulo": "Inception", "fecha": "hoy"}]
    assert data["estadisticas"] == {"total_favoritas": 1, "total_historial": 1}


def test_exportar_importar_roundtrip_idéntico():
    library_service.agregar_a_favoritas(make_movie())
    library_service.agregar_al_historial(make_movie())
    library_service.exportar_a_json("datos1.json")
    library_service.importar_de_json("datos1.json")
    library_service.exportar_a_json("datos2.json")
    with open("datos1.json") as f:
        primero = f.read()
    with open("datos2.json") as f:
        segundo = f.read()
    assert primero == segundo


def test_importar_sin_datos_previos():
    library_service.agregar_a_favoritas(make_movie())
    library_service.exportar_a_json("datos.json")
    library_service.PELICULAS_FAVORITAS = []
    library_service.importar_de_json("datos.json")
    assert [m.title for m in library_service.obtener_favoritas()] == ["Inception"]


def test_exportar_rechaza_nombre_con_ruta():
    with pytest.raises(InputValidationError):
        library_service.exportar_a_json("../fuera.json")


def test_exportar_rechaza_nombre_vacio():
    with pytest.raises(InputValidationError):
        library_service.exportar_a_json("")


def test_importar_rechaza_nombre_con_separador():
    with pytest.raises(InputValidationError):
        library_service.importar_de_json("dir/datos.json")


def test_agregar_dos_titulos_distintos_cubre_segunda_iteracion():
    """Agrega dos titulos distintos: recorre la lista en la segunda iteracion."""
    a = Movie.from_omdb({"Title": "Inception", "Year": "2010"})
    b = Movie.from_omdb({"Title": "Interstellar", "Year": "2014"})
    assert library_service.agregar_a_favoritas(a) is True
    assert library_service.agregar_a_favoritas(b) is True
    assert len(library_service.obtener_favoritas()) == 2


def test_eliminar_inexistente_devuelve_false_y_no_modifica():
    a = Movie.from_omdb({"Title": "Inception", "Year": "2010"})
    library_service.agregar_a_favoritas(a)
    assert library_service.eliminar_de_favoritas("Inexistente") is False
    assert len(library_service.obtener_favoritas()) == 1