"""Tests del servicio de peliculas (services.movie_service)."""
import pytest

import services.movie_service as movie_service
from exceptions.not_found import MovieNotFoundError


def test_buscar_pelicula_ok(fake_requests):
    movie = movie_service.buscar_pelicula("Inception")
    assert movie.title == "Inception"
    assert movie.year == "2010"
    assert movie.rating is None


def test_buscar_pelicula_inexistente_lanza_movie_not_found(fake_requests):
    with pytest.raises(MovieNotFoundError):
        movie_service.buscar_pelicula("DoesNotExist")


def test_buscar_peliculas_por_actor(fake_requests):
    movies = movie_service.buscar_peliculas_por_actor("Tom Cruise")
    assert [m.title for m in movies] == ["Mission: Impossible", "Top Gun"]


def test_obtener_peliculas_populares():
    movies = movie_service.obtener_peliculas_populares()
    assert len(movies) == 5
    assert movies[0].title == "The Shawshank Redemption"
    assert movies[0].year == "1994"
    assert movies[0].rating == 9.3


def test_buscar_peliculas_por_genero():
    assert [m.title for m in movie_service.buscar_peliculas_por_genero("accion")] == [
        "Die Hard",
        "Mad Max Fury Road",
    ]
    assert [m.title for m in movie_service.buscar_peliculas_por_genero("comedia")] == [
        "Superbad",
        "The Hangover",
    ]
    assert len(movie_service.buscar_peliculas_por_genero("otro")) == 4