import logging
import sys

import logging_config
import ui.menu
from exceptions.application_error import ApplicationError

logger = logging.getLogger(__name__)


def main():
    """Punto de entrada: delega en el menu y gestiona errores de nivel superior.

    Ultima linea de defensa: los errores conocidos y desconocidos se registran
    en el log y el usuario recibe un mensaje generico (nunca trazas).
    """
    logging_config.configure_logging()
    try:
        ui.menu.menu_principal()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido")
        sys.exit(0)
    except ApplicationError as exc:
        logger.error("Error de aplicacion: %s", exc, exc_info=True)
        print("\nOcurrió un error inesperado. Revise el log para más detalles.")
        sys.exit(1)
    except Exception as exc:
        logger.exception("Error inesperado: %s", exc)
        print("\nOcurrió un error inesperado. Revise el log para más detalles.")
        sys.exit(1)


if __name__ == "__main__":
    main()