"""Fixtures compartidos: respuestas fake de APIs, reset de estado global."""
import logging

import pytest


class FakeResponse:
    """Minimo objeto respuesta con .json(), .status_code y .raise_for_status()."""

    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"HTTP {self.status_code}")


MOVIE_DETAILS = {
    "Response": "True",
    "Title": "Inception",
    "Year": "2010",
    "imdbRating": "8.8",
    "Genre": "Sci-Fi, Thriller",
    "Director": "Christopher Nolan",
    "Actors": "Leonardo DiCaprio, Joseph Gordon-Levitt",
    "Plot": "A thief who steals corporate secrets.",
    "Country": "USA, UK",
    "Awards": "4 Oscars",
}

SEARCH_RESULTS = [
    {"Title": "Mission: Impossible", "Year": "1996"},
    {"Title": "Top Gun", "Year": "1986"},
]

SHOW_SEARCH = {"id": 169, "name": "Breaking Bad", "status": "Ended"}

SHOW_DETAIL = {
    "id": 169,
    "name": "Breaking Bad",
    "language": "English",
    "genres": ["Crime", "Drama", "Thriller"],
    "rating": {"average": 9.5},
    "status": "Ended",
    "premiered": "2008-01-20",
    "ended": "2013-09-29",
    "runtime": 47,
    "summary": "A school chemistry teacher. " * 15,
}


@pytest.fixture
def fake_requests(monkeypatch):
    """Parchea requests.get con respuestas fake (nunca red real).

    Devuelve la lista de URLs consultadas.
    """
    import requests

    calls = []

    def get(url, params=None, timeout=None):
        calls.append(url)
        if "omdbapi.com" in url:
            if "apikey=BADKEY" in url:
                return FakeResponse({"Response": "False", "Error": "Invalid API key!"})
            if "DoesNotExist" in url:
                return FakeResponse({"Response": "False", "Error": "Movie not found!"})
            if "s=EmptyActor" in url:
                return FakeResponse({"Response": "False", "Error": "Movie not found!"})
            if "t=" in url and "s=" not in url:
                return FakeResponse(MOVIE_DETAILS)
            if "s=" in url:
                return FakeResponse({"Response": "True", "Search": SEARCH_RESULTS})
            return FakeResponse({"Response": "False"})
        if "tvmaze.com" in url:
            if "/search/shows" in url:
                if "q=Ghost" in url:
                    return FakeResponse([])
                if "q=404" in url:
                    return FakeResponse([{"show": {"id": 404, "name": "Fantasmas", "status": "Ended"}}])
                return FakeResponse([{"show": SHOW_SEARCH}])
            if "/shows/404" in url:
                return FakeResponse({}, status_code=404)
            if "/shows/" in url:
                return FakeResponse(SHOW_DETAIL)
            return FakeResponse({})
        return FakeResponse({})

    monkeypatch.setattr(requests, "get", get)
    return calls


@pytest.fixture(autouse=True)
def bloquear_red_real(monkeypatch):
    """Cualquier llamada HTTP que no pase por fake_requests es un error.

    Impide que la suite dependa de Internet ni consuma cuota de una API real:
    un test que olvide la fixture falla de inmediato con un mensaje claro en
    vez de recibir una respuesta ajena o un timeout de red.
    """
    import requests

    def get_prohibido(url, *args, **kwargs):
        raise AssertionError(
            f"Llamada HTTP real bloqueada ({url}). Usa la fixture fake_requests."
        )

    def request_prohibido(self, method, url, *args, **kwargs):
        raise AssertionError(
            f"Llamada HTTP real bloqueada ({method} {url}). Usa la fixture fake_requests."
        )

    monkeypatch.setattr(requests, "get", get_prohibido)
    monkeypatch.setattr(requests.Session, "request", request_prohibido)


@pytest.fixture(autouse=True)
def restore_runtime_config():
    """Restaura CONFIG de runtime entre tests (el menu lo muta).

    Ademas fija las claves de API a valores de prueba: su valor real depende de
    OMDB_API_KEY en la maquina que ejecuta la suite, y la suite debe dar el
    mismo resultado en todas.
    """
    import config

    originales = dict(config.CONFIG)
    config.CONFIG["api_key_omdb"] = "trilogy"
    config.CONFIG["api_key_tmdb"] = ""
    yield
    config.CONFIG.clear()
    config.CONFIG.update(originales)


@pytest.fixture(autouse=True)
def clear_api_caches():
    """Limpia las caches de la capa api entre tests."""
    import api.omdb as omdb
    import api.tvmaze as tvmaze

    omdb.CACHE_PELICULAS.clear()
    tvmaze.CACHE_SERIES.clear()
    yield


@pytest.fixture(autouse=True)
def silenciar_logging():
    """Evita que el logging WARNING+ de los tests ruya en stderr.

    Se instala un NullHandler en el root para que no se use el lastResort.
    caplog sigue capturando sin problemas (añade su propio handler).
    """
    root = logging.getLogger()
    root.addHandler(logging.NullHandler())
    yield