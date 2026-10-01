"""Tests del acceso a TVMaze (api.tvmaze)."""
import pytest

import api.tvmaze as tvmaze
from exceptions.api_error import InvalidResponseError, TVMazeError


def test_buscar_series_y_url_exacta(fake_requests):
    data = tvmaze.buscar_series("Breaking Bad")
    assert data[0]["show"]["name"] == "Breaking Bad"
    assert fake_requests == ["http://api.tvmaze.com/search/shows?q=Breaking Bad"]


def test_buscar_series_usa_cache(fake_requests, monkeypatch):
    calls = []
    original = tvmaze.hacer_request
    monkeypatch.setattr(
        tvmaze,
        "hacer_request",
        lambda *args, **kwargs: (calls.append(args) or original(*args, **kwargs)),
    )
    tvmaze.buscar_series("Breaking Bad")
    tvmaze.buscar_series("Breaking Bad")
    assert len(calls) == 1


def test_buscar_series_respuesta_no_lista_es_invalid_response(monkeypatch):
    monkeypatch.setattr(tvmaze, "hacer_request", lambda *args, **kwargs: {})
    with pytest.raises(InvalidResponseError):
        tvmaze.buscar_series("Breaking Bad")


def test_obtener_detalles_serie(fake_requests):
    data = tvmaze.obtener_detalles_serie(169)
    assert data["id"] == 169
    assert fake_requests == ["http://api.tvmaze.com/shows/169"]


def test_obtener_detalles_serie_no_existe_es_tvmaze_error_404(fake_requests):
    with pytest.raises(TVMazeError) as excinfo:
        tvmaze.obtener_detalles_serie(404)
    assert excinfo.value.status_code == 404


def test_obtener_detalles_serie_respuesta_no_dict_es_invalid_response(monkeypatch):
    monkeypatch.setattr(tvmaze, "hacer_request", lambda *args, **kwargs: [])
    with pytest.raises(InvalidResponseError):
        tvmaze.obtener_detalles_serie(169)


def test_buscar_series_invalid_response_se_propaga(monkeypatch):
    def _boom(*a, **k):
        raise InvalidResponseError("boom")

    monkeypatch.setattr(tvmaze, "hacer_request", _boom)
    with pytest.raises(InvalidResponseError):
        tvmaze.buscar_series("Breaking Bad")