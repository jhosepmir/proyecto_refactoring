"""exceptions - Jerarquia de errores de la aplicacion.

ApplicationError
├── ConfigurationError
├── APIError
│   ├── InvalidResponseError
│   ├── OMDBError
│   └── TVMazeError
├── InputValidationError
├── MovieNotFoundError
└── SeriesNotFoundError
"""
from exceptions.api_error import APIError, InvalidResponseError, OMDBError, TVMazeError
from exceptions.application_error import ApplicationError
from exceptions.configuration_error import ConfigurationError
from exceptions.not_found import MovieNotFoundError, SeriesNotFoundError
from exceptions.validation_error import InputValidationError

__all__ = [
    "APIError",
    "ApplicationError",
    "ConfigurationError",
    "InputValidationError",
    "InvalidResponseError",
    "MovieNotFoundError",
    "OMDBError",
    "SeriesNotFoundError",
    "TVMazeError",
]