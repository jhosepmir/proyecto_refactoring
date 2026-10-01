"""Test e2e del menu completo: simula una sesion scripted laxa.

No es una comparacion byte a byte (eso cubre el driver de baseline), pero
verifica que el flujo integrado ui -> services -> api -> UI funciona completo.
"""
import builtins
import os
import time

import config
import services.library_service as library_service
import ui.menu

INPUTS = [
    "1", "Inception", "s", "",                 # buscar + agregar favorita
    "1", "Inception", "s", "",                 # cache + ya favorita
    "1", "DoesNotExist", "",                   # no encontrada
    "2", "Tom Cruise", "1", "",                # actor, ver detalle
    "3", "Breaking Bad", "1", "",              # series, detalle
    "4", "",                                   # populares
    "5", "accion", "",                         # genero
    "6", "", "",                               # favoritos, volver
    "7", "s", "",                              # historial, limpiar
    "8", "",                                   # estadisticas
    "9", "test_export", "",                    # exportar
    "10", "test_export", "",                   # importar
    "11", "1", "",                             # config: toggle debug
    "99",                                      # opcion invalida
    "12",                                      # salir
]


def test_flujo_completo(fake_requests, monkeypatch, capsys, tmp_path):
    library_service.PELICULAS_FAVORITAS = []
    library_service.HISTORIAL_BUSQUEDAS = []
    monkeypatch.setattr(os, "system", lambda *args, **kwargs: None)
    monkeypatch.setattr(time, "sleep", lambda *args, **kwargs: None)
    monkeypatch.chdir(tmp_path)

    queue = iter(INPUTS)

    def fake_input(prompt=""):
        print(prompt, end="")
        try:
            value = next(queue)
        except StopIteration:
            value = "12"
        print(value)
        return value

    monkeypatch.setattr(builtins, "input", fake_input)

    ui.menu.menu_principal()
    out = capsys.readouterr().out

    assert "SISTEMA DE PELÍCULAS Y SERIES" in out
    assert "Título: Inception" in out
    assert "Rating IMDB: 8.8" in out
    assert "Ya está en favoritos" in out
    assert "No se encontró la película" in out
    assert "1. Mission: Impossible (1996)" in out
    assert "2. Top Gun (1986)" in out
    assert "1. Breaking Bad (Ended)" in out
    assert "Nombre: Breaking Bad" in out
    assert "Resumen:" in out
    assert "PELÍCULAS POPULARES" in out
    assert "1. The Shawshank Redemption (1994) - 9.3" in out
    assert "1. Die Hard (1988) - 8.2" in out
    assert "MIS FAVORITOS" in out
    assert "HISTORIAL DE BÚSQUEDAS" in out
    assert "Historial limpiado" in out
    assert "ESTADÍSTICAS" in out
    assert "Total favoritas: 1" in out
    assert "Exportado a test_export.json" in out
    assert "Importado desde test_export.json" in out
    assert "CONFIGURACIÓN" in out
    assert "3. Timeout: 30" in out
    assert "Debug ahora es: False" in out
    assert "Opción inválida" in out
    assert "¡Hasta luego!" in out
    assert config.CONFIG == {
        "debug": False,
        "verbose": True,
        "timeout": 30,
        "max_retries": 3,
        "api_key_omdb": "trilogy",
        "api_key_tmdb": "",
    }


def test_entrada_vacia_es_validada_sin_red(monkeypatch, capsys):
    """Titulo vacio no toca la red: la validacion corta antes de la API."""
    import api.omdb as omdb

    hits_before = len(omdb.CACHE_PELICULAS)

    queue = iter(["1", "", "12"])

    def fake_input(prompt=""):
        print(prompt, end="")
        try:
            value = next(queue)
        except StopIteration:
            value = "12"
        print(value)
        return value

    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(os, "system", lambda *args, **kwargs: None)

    ui.menu.menu_principal()
    out = capsys.readouterr().out

    assert "Título: Ingrese un valor válido." in out
    assert "Buscando película" not in out
    assert len(omdb.CACHE_PELICULAS) == hits_before