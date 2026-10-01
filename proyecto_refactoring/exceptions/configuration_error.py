"""exceptions/configuration_error.py - Fallos de configuracion interna."""
from exceptions.application_error import ApplicationError


class ConfigurationError(ApplicationError):
    """Falta o es invalida una clave de configuracion interna."""