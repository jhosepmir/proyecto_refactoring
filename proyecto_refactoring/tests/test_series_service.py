"""Tests del servicio de series (services.series_service)."""
import pytest

import services.series_service as series_service
from exceptions.api_error import TVMazeError
from exceptions.not_found import SeriesNotFoundError


def test_buscar_series(fake_requests):
    series = series_service.buscar_series("Breaking Bad")
    assert len(series) == 1
    assert series[0].name == "Breaking Bad"
    assert series[0].status == "Ended"


def test_obtener_detalles_serie(fake_requests):
    serie = series_service.obtener_detalles_serie(169)
    assert serie.id == 169
    assert serie.rating == 9.5
    assert serie.genres == ["Crime", "Drama", "Thriller"]
    assert serie.summary.startswith("A school chemistry teacher.")


def test_obtener_detalles_serie_no_existe_lanza_series_not_found(fake_requests):
    with pytest.raises(SeriesNotFoundError):
        series_service.obtener_detalles_serie(404)


def test_obtener_detalles_serie_error_no_404_se_propaga(monkeypatch):
    """Un error distinto de 404 (p.ej. 500) se propaga como TVMazeError."""
    import api.tvmaze as tvmaze

    def _boom(id_serie):
        raise TVMazeError("La API tardo demasiado", status_code=500)

    monkeypatch.setattr(tvmaze, "obtener_detalles_serie", _boom)
    with pytest.raises(TVMazeError) as excinfo:
        series_service.obtener_detalles_serie(99)
    assert excinfo.value.status_code == 500


def test_buscar_series_sin_resultados_devuelve_lista_vacia(monkeypatch):
    import api.tvmaze as tvmaze

    monkeypatch.setattr(tvmaze, "buscar_series", lambda nombre: [])
    assert series_service.buscar_series("Ghost") == []