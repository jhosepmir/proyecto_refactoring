"""Tests del acceso a OMDb (api.omdb)."""
import logging

import pytest

import api.omdb as omdb
import config
from exceptions.api_error import InvalidResponseError, OMDBError


def test_buscar_pelicula_ok_y_url_exacta(fake_requests):
    data = omdb.buscar_pelicula("Inception")
    assert data["Title"] == "Inception"
    assert fake_requests == ["http://www.omdbapi.com/?t=Inception&apikey=trilogy"]


def test_buscar_pelicula_inexistente_devuelve_none(fake_requests):
    assert omdb.buscar_pelicula("DoesNotExist") is None


def test_buscar_pelicula_usa_cache(fake_requests, caplog):
    config.CONFIG["debug"] = True
    omdb.buscar_pelicula("Inception")
    omdb.buscar_pelicula("Inception")
    assert len(fake_requests) == 1
    with caplog.at_level(logging.DEBUG, logger="api.omdb"):
        omdb.buscar_pelicula("Inception")
    assert "Usando cache para Inception" in caplog.text


def test_buscar_pelicula_apikey_invalida_es_ombd_error(fake_requests, monkeypatch):
    monkeypatch.setitem(config.CONFIG, "api_key_omdb", "BADKEY")
    with pytest.raises(OMDBError, match="Clave de API invalida"):
        omdb.buscar_pelicula("Inception")


def test_buscar_pelicula_respuesta_no_dict_es_invalid_response(monkeypatch):
    monkeypatch.setattr(omdb, "hacer_request", lambda *args, **kwargs: [])
    with pytest.raises(InvalidResponseError):
        omdb.buscar_pelicula("Inception")


def test_buscar_pelicula_otro_error_omdb_se_propaga(monkeypatch):
    monkeypatch.setattr(
        omdb,
        "hacer_request",
        lambda *args, **kwargs: {"Response": "False", "Error": "Too many results."},
    )
    with pytest.raises(OMDBError):
        omdb.buscar_pelicula("Inception")


def test_buscar_peliculas_por_actor(fake_requests):
    data = omdb.buscar_peliculas_por_actor("Tom Cruise")
    assert [item["Title"] for item in data] == ["Mission: Impossible", "Top Gun"]
    assert fake_requests == ["http://www.omdbapi.com/?s=Tom Cruise&type=movie&apikey=trilogy"]


def test_buscar_peliculas_por_actor_apikey_invalida_es_ombd_error(fake_requests, monkeypatch):
    monkeypatch.setitem(config.CONFIG, "api_key_omdb", "BADKEY")
    with pytest.raises(OMDBError, match="Clave de API invalida"):
        omdb.buscar_peliculas_por_actor("Tom Cruise")


def test_buscar_pelicula_invalid_response_se_propaga_sin_reempaquetar(monkeypatch):
    monkeypatch.setattr(omdb, "hacer_request", lambda *a, **k: (_ for _ in ()).throw(InvalidResponseError("boom")))
    with pytest.raises(InvalidResponseError):
        omdb.buscar_pelicula("Inception")


def test_buscar_peliculas_por_actor_invalid_response_se_propaga(monkeypatch):
    monkeypatch.setattr(omdb, "hacer_request", lambda *a, **k: (_ for _ in ()).throw(InvalidResponseError("boom")))
    with pytest.raises(InvalidResponseError):
        omdb.buscar_peliculas_por_actor("Tom Cruise")


def test_buscar_pelicula_clave_invalida_directa(monkeypatch):
    monkeypatch.setattr(omdb, "hacer_request", lambda *a, **k: {"Response": "False", "Error": "Invalid API key!"})
    with pytest.raises(OMDBError):
        omdb.buscar_pelicula("Inception")


def test_buscar_peliculas_por_actor_respuesta_no_dict_es_invalid_response(monkeypatch):
    monkeypatch.setattr(omdb, "hacer_request", lambda *a, **k: [])
    with pytest.raises(InvalidResponseError):
        omdb.buscar_peliculas_por_actor("Tom Cruise")


def test_buscar_peliculas_por_actor_clave_invalida_directa(monkeypatch):
    monkeypatch.setattr(omdb, "hacer_request", lambda *a, **k: {"Response": "False", "Error": "Invalid API key!"})
    with pytest.raises(OMDBError):
        omdb.buscar_peliculas_por_actor("Tom Cruise")


def test_buscar_peliculas_por_actor_otro_error_devuelve_lista_vacia(monkeypatch):
    monkeypatch.setattr(omdb, "hacer_request", lambda *a, **k: {"Response": "False", "Error": "Too many results."})
    assert omdb.buscar_peliculas_por_actor("a") == []


def test_buscar_pelicula_cache_sin_debug_solo_retorna(fake_requests):
    # config debug ya es False por restore_runtime_config; cachea dos veces
    omdb.buscar_pelicula("Inception")
    segundo = omdb.buscar_pelicula("Inception")
    assert segundo["Title"] == "Inception"
    assert len(fake_requests) == 1