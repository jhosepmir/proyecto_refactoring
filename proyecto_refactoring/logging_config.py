"""logging_config.py - Configuracion centralizada de logging.

Consola a nivel WARNING (la UI propia es el canal del usuario) y archivo
rotativo logs/app.log a nivel DEBUG con detalle completo para diagnostico.
La consola NO imprime trazas (traceback): las trazas quedan solo en el
archivo de log. Es idempotente: configurar dos veces no duplica handlers.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
LOG_MAX_BYTES = 1_000_000
LOG_BACKUP_COUNT = 2


class ConsoleFormatter(logging.Formatter):
    """Formatter de consola: emite el mensaje sin la traza (exc_info).

    Las trazas quedan solo en el archivo (usa el formatter estandar), para
    que el usuario nunca vea detalles internos por consola.
    """

    def format(self, record: logging.LogRecord) -> str:
        exc_info = record.exc_info
        exc_text = record.exc_text
        record.exc_info = None
        record.exc_text = None
        try:
            return super().format(record)
        finally:
            record.exc_info = exc_info
            record.exc_text = exc_text


def configure_logging() -> None:
    """Configura root: handler de archivo (DEBUG) y consola (WARNING)."""
    root = logging.getLogger()
    if root.handlers:
        return

    os.makedirs(LOG_DIR, exist_ok=True)
    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(ConsoleFormatter(LOG_FORMAT))

    root.setLevel(logging.DEBUG)
    root.addHandler(file_handler)
    root.addHandler(console_handler)