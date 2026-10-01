"""Tests de la jerarquia de excepciones (exceptions package)."""
import pytest

from exceptions.api_error import APIError, InvalidResponseError, OMDBError, TVMazeError
from exceptions.application_error import ApplicationError
from exceptions.configuration_error import ConfigurationError
from exceptions.not_found import MovieNotFoundError, SeriesNotFoundError


def test_todas_cuelgan_de_application_error():
    assert issubclass(APIError, ApplicationError)
    assert issubclass(InvalidResponseError, APIError)
    assert issubclass(OMDBError, APIError)
    assert issubclass(TVMazeError, APIError)
    assert issubclass(ConfigurationError, ApplicationError)
    assert issubclass(MovieNotFoundError, ApplicationError)
    assert issubclass(SeriesNotFoundError, ApplicationError)
    assert issubclass(ApplicationError, Exception)


def test_apierror_guarda_mensaje_y_status_code():
    error = APIError("mensaje", status_code=404)
    assert str(error) == "mensaje"
    assert error.status_code == 404


def test_apierror_status_code_opcional():
    assert APIError("sin codigo").status_code is None


def test_se_pueden_capturar_como_application_error():
    with pytest.raises(ApplicationError):
        raise OMDBError("fallo omdb")


def test_not_found_llevan_mensaje():
    assert str(MovieNotFoundError("peli")) == "peli"
    assert str(SeriesNotFoundError("serie")) == "serie"