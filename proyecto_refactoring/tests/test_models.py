"""Tests de los modelos Movie y Series."""
from models.movie import Movie
from models.series import Series


def test_movie_from_omdb_maps_fields():
    movie = Movie.from_omdb(
        {
            "Response": "True",
            "Title": "Inception",
            "Year": "2010",
            "imdbRating": "8.8",
            "Genre": "Sci-Fi",
            "Director": "Christopher Nolan",
            "Actors": "Leonardo DiCaprio",
            "Plot": "Dreams",
            "Country": "USA",
            "Awards": "4 Oscars",
        }
    )
    assert movie.title == "Inception"
    assert movie.year == "2010"
    assert movie.imdb_rating == "8.8"
    assert movie.genre == "Sci-Fi"
    assert movie.director == "Christopher Nolan"
    assert movie.actors == "Leonardo DiCaprio"
    assert movie.plot == "Dreams"
    assert movie.country == "USA"
    assert movie.awards == "4 Oscars"
    assert movie.rating is None
    assert movie.raw["Title"] == "Inception"


def test_movie_from_omdb_missing_keys_default_na():
    movie = Movie.from_omdb({"Response": "True"})
    assert movie.title == "N/A"
    assert movie.year == "N/A"
    assert movie.imdb_rating == "N/A"
    assert movie.awards == "N/A"


def test_movie_from_omdb_conserva_dict_crudo():
    movie = Movie.from_omdb({"Title": "Inception", "Year": "2010"})
    assert movie.raw == {"Title": "Inception", "Year": "2010"}


def test_movie_from_catalog():
    movie = Movie.from_catalog({"titulo": "The Godfather", "anio": 1972, "rating": 9.2})
    assert movie.title == "The Godfather"
    assert movie.year == "1972"
    assert movie.rating == 9.2


def test_series_from_tvmaze_wrapper():
    series = Series.from_tvmaze(
        {
            "show": {
                "id": 169,
                "name": "Breaking Bad",
                "rating": {"average": 9.5},
                "genres": ["Drama", "Crime"],
            }
        }
    )
    assert series.id == 169
    assert series.name == "Breaking Bad"
    assert series.rating == 9.5
    assert series.genres == ["Drama", "Crime"]


def test_series_from_tvmaze_directo():
    series = Series.from_tvmaze({"name": "Severance", "status": "Running"})
    assert series.name == "Severance"
    assert series.status == "Running"


def test_series_missing_defaults():
    series = Series.from_tvmaze({})
    assert series.name is None
    assert series.genres == []
    assert series.rating == "N/A"
    assert series.summary == "N/A"


def test_series_rating_average_ausente():
    series = Series.from_tvmaze({"rating": {}})
    assert series.rating == "N/A"


def test_series_resumen_preserva_none():
    series = Series.from_tvmaze({"rating": {"average": None}})
    assert series.rating is None


def test_series_rating_no_dict_se_preserva():
    """models/series.py:36 — cuando rating no es dict se preserva tal cual."""
    series = Series.from_tvmaze({"name": "Severance", "rating": 8.0})
    assert series.rating == 8.0