"""Tests de logging_config (FASE 6 - cobertura del wiring de logging)."""
import logging
import os
import sys

import logging_config


def test_configure_logging_crea_handlers_y_archivo(tmp_path, monkeypatch):
    root = logging.getLogger()
    saved_handlers = list(root.handlers)
    saved_level = root.level
    # Limpia el root (quita el NullHandler del autouse silenciar_logging)
    root.handlers.clear()
    monkeypatch.setattr(logging_config, "LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setattr(logging_config, "LOG_FILE", str(tmp_path / "logs" / "app.log"))
    try:
        logging_config.configure_logging()
        assert len(root.handlers) == 2
        assert os.path.isfile(str(tmp_path / "logs" / "app.log"))
        assert any(isinstance(h, logging.FileHandler) or type(h).__name__ == "RotatingFileHandler" for h in root.handlers)
        assert any(isinstance(h, logging.StreamHandler) for h in root.handlers)
        # Idempotente: segunda llamada no duplica
        logging_config.configure_logging()
        assert len(root.handlers) == 2
        assert root.level == logging.DEBUG
    finally:
        # Restaura root a su estado (silenciar_logging re-pondra NullHandler en el proximo test)
        for h in list(root.handlers):
            root.removeHandler(h)
            try:
                h.close()
            except Exception:
                pass
        for h in saved_handlers:
            root.addHandler(h)
        root.setLevel(saved_level)


def _registro_con_excepcion():
    """Crea un registro ERROR con traza adjunta."""
    try:
        raise RuntimeError("fallo interno")
    except RuntimeError:
        return logging.LogRecord(
            name="test.trazas",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="Error controlado: %s",
            args=("detalle",),
            exc_info=sys.exc_info(),
        )


def test_console_formatter_omite_trazas():
    registro = _registro_con_excepcion()
    salida_consola = logging_config.ConsoleFormatter(logging_config.LOG_FORMAT).format(registro)
    assert "Error controlado: detalle" in salida_consola
    assert "Traceback" not in salida_consola
    assert "RuntimeError" not in salida_consola
    # El formatter estandar (archivo) si conserva la traza
    salida_archivo = logging.Formatter(logging_config.LOG_FORMAT).format(registro)
    assert "Traceback" in salida_archivo
    assert "RuntimeError: fallo interno" in salida_archivo


def test_configure_logging_consola_sin_trazas(tmp_path, monkeypatch, capsys):
    root = logging.getLogger()
    saved_handlers = list(root.handlers)
    saved_level = root.level
    root.handlers.clear()
    monkeypatch.setattr(logging_config, "LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setattr(logging_config, "LOG_FILE", str(tmp_path / "logs" / "app.log"))
    try:
        logging_config.configure_logging()
        try:
            raise RuntimeError("fallo interno")
        except RuntimeError:
            logging.getLogger("test.consola").error("Error controlado: %s", "detalle", exc_info=True)
        capturado = capsys.readouterr()
        assert "Error controlado: detalle" in capturado.err
        assert "Traceback" not in capturado.err
        contenido_archivo = (tmp_path / "logs" / "app.log").read_text(encoding="utf-8")
        assert "Traceback" in contenido_archivo
        assert "RuntimeError: fallo interno" in contenido_archivo
    finally:
        for h in list(root.handlers):
            root.removeHandler(h)
            try:
                h.close()
            except Exception:
                pass
        for h in saved_handlers:
            root.addHandler(h)
        root.setLevel(saved_level)
