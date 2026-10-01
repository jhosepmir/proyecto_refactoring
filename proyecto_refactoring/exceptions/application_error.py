"""exceptions/application_error.py - Excepcion base de la aplicacion.

Todas las excepciones propias cuelgan de ApplicationError para que la UI y
main.py puedan distinguir errores conocidos de errores inesperados.
"""


class ApplicationError(Exception):
    """Error base identificable por la capa de presentacion."""