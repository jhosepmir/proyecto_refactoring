"""Tests de integracion del menu: cubren ramas del decorador y submenus (FASE 6).

Cada test corre una sesion scripted aislada (ui.menu -> services -> api)
y verifica mensajes observables de display o el comportamiento sin red."""
import builtins
import os
import time

import pytest

import config
import services.library_service as library_service
import ui.menu
from exceptions.api_error import APIError
from exceptions.application_error import ApplicationError
from exceptions.configuration_error import ConfigurationError
from models.movie import Movie


def _run_session(monkeypatch, capsys, inputs):
    """Ejecuta menu_principal con la cola inputs scripted."""
    monkeypatch.setattr(os, "system", lambda *a, **k: None)
    monkeypatch.setattr(time, "sleep", lambda *a, **k: None)
    q = iter(inputs)

    def fake_input(prompt=""):
        print(prompt, end="")
        try:
            v = next(q)
        except StopIteration:
            v = "12"
        print(v)
        return v

    monkeypatch.setattr(builtins, "input", fake_input)
    ui.menu.menu_principal()
    return capsys.readouterr().out


def test_serie_404_decorador(fake_requests, monkeypatch, capsys, tmp_path):
    library_service.PELICULAS_FAVORITAS = []
    library_service.HISTORIAL_BUSQUEDAS = []
    monkeypatch.chdir(tmp_path)
    # Busca "404" -> una serie con id 404, seleccionarla detona TVMaze 404
    out = _run_session(monkeypatch, capsys, ["3", "404", "1", "", "12"])
    assert "No se encontró la serie" in out


def test_actor_sin_resultados_y_volver(fake_requests, monkeypatch, capsys, tmp_path):
    library_service.PELICULAS_FAVORITAS = []
    library_service.HISTORIAL_BUSQUEDAS = []
    monkeypatch.chdir(tmp_path)
    out = _run_session(monkeypatch, capsys, ["2", "EmptyActor", "", "12"])
    assert "No se encontraron películas para ese actor" in out


def test_series_sin_resultados(fake_requests, monkeypatch, capsys, tmp_path):
    library_service.PELICULAS_FAVORITAS = []
    library_service.HISTORIAL_BUSQUEDAS = []
    monkeypatch.chdir(tmp_path)
    out = _run_session(monkeypatch, capsys, ["3", "Ghost", "", "12"])
    assert "No se encontraron series" in out


def test_opciones_volver_0_y_n(fake_requests, monkeypatch, capsys, tmp_path):
    library_service.PELICULAS_FAVORITAS = []
    library_service.HISTORIAL_BUSQUEDAS = []
    monkeypatch.chdir(tmp_path)
    # Actor: volver, Series: volver, Pelicula: no agregar, Historial n: no limpia
    out = _run_session(
        monkeypatch,
        capsys,
        [
            "2", "Tom Cruise", "0", "",  # actor 0 = volver
            "3", "Breaking Bad", "0", "",  # series 0 = volver
            "1", "Inception", "n", "",  # no agregar a favoritos
            "7", "n", "",  # historial n
            "12",
        ],
    )
    # Deben estar los encabezados de los flujos sin error
    assert "Buscando películas del actor" in out
    assert "Buscando series" in out


def test_favoritas_vacia_y_con_eliminar(fake_requests, monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    library_service.PELICULAS_FAVORITAS = []
    library_service.HISTORIAL_BUSQUEDAS = []
    # Vacia
    out = _run_session(monkeypatch, capsys, ["6", "", "12"])
    assert "No tienes películas favoritas" in out

    library_service.PELICULAS_FAVORITAS = []
    library_service.HISTORIAL_BUSQUEDAS = []
    # Agrega luego elimina
    out = _run_session(
        monkeypatch,
        capsys,
        ["1", "Inception", "s", "", "6", "1", "", "6", "9", "", "12"],
    )
    assert "¡Agregada a favoritos!" in out
    assert "Eliminada de favoritos" in out
    # Segunda eliminacion con fuera de rango no falla; sigue 9 fuera de rango -> silencioso


def test_historial_sin_datos(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    library_service.PELICULAS_FAVORITAS = []
    library_service.HISTORIAL_BUSQUEDAS = []
    out = _run_session(monkeypatch, capsys, ["7", "", "12"])
    assert "No hay historial" in out


def test_config_submenus(monkeypatch, capsys, tmp_path):
    library_service.PELICULAS_FAVORITAS = []
    library_service.HISTORIAL_BUSQUEDAS = []
    monkeypatch.chdir(tmp_path)
    out = _run_session(
        monkeypatch,
        capsys,
        [
            "11", "2", "",  # verbose toggle
            "11", "3", "40", "",  # timeout valido
            "11", "3", "abc", "",  # timeout invalido -> mensaje de validacion
            "12",
        ],
    )
    assert "Verbose ahora es:" in out
    assert "Valor inválido para timeout. No se cambió." in out
    assert config.CONFIG["timeout"] == 40


def test_decorador_ramas_de_error(monkeypatch, capsys, tmp_path):
    import api.omdb as omdb  # noqa: F401
    import services.movie_service as movie_service

    monkeypatch.chdir(tmp_path)
    library_service.PELICULAS_FAVORITAS = []
    library_service.HISTORIAL_BUSQUEDAS = []

    # APIError
    monkeypatch.setattr(movie_service, "buscar_pelicula", lambda titulo: (_ for _ in ()).throw(APIError("caida")))
    out = _run_session(monkeypatch, capsys, ["1", "Inception", "", "12"])
    assert "Error al consultar la API. Intente nuevamente más tarde." in out

    # ConfigurationError
    monkeypatch.setattr(library_service, "obtener_favoritas", lambda: (_ for _ in ()).throw(ConfigurationError("cfg mala")))
    out = _run_session(monkeypatch, capsys, ["6", "", "12"])
    assert "Error de configuración de la aplicación." in out

    # ApplicationError generico
    monkeypatch.setattr(library_service, "obtener_favoritas", lambda: [])
    monkeypatch.setattr(movie_service, "obtener_peliculas_populares", lambda: (_ for _ in ()).throw(ApplicationError("boom")))
    out = _run_session(monkeypatch, capsys, ["4", "", "12"])
    assert "Ocurrió un error inesperado. Revise el log para más detalles." in out

    # Export OSError
    monkeypatch.setattr(library_service, "obtener_favoritas", lambda: [])
    monkeypatch.setattr(library_service, "exportar_a_json", lambda nombre: (_ for _ in ()).throw(OSError("disco lleno")))
    out = _run_session(monkeypatch, capsys, ["9", "archivo", "", "12"])
    assert "Error al exportar archivo" in out

    # Import OSError
    monkeypatch.setattr(library_service, "importar_de_json", lambda nombre: (_ for _ in ()).throw(FileNotFoundError("no existe")))
    out = _run_session(monkeypatch, capsys, ["10", "archivo", "", "12"])
    assert "Error al importar archivo" in out

    # Import ValueError (JSON invalido)
    monkeypatch.setattr(library_service, "importar_de_json", lambda nombre: (_ for _ in ()).throw(ValueError("json malo")))
    out = _run_session(monkeypatch, capsys, ["10", "archivo", "", "12"])
    assert "Error al importar archivo" in out
