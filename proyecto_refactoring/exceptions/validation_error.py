"""exceptions/validation_error.py - Entradas de usuario invalidas."""
from exceptions.application_error import ApplicationError


class InputValidationError(ApplicationError):
    """Una entrada del usuario no cumple las reglas de validacion."""