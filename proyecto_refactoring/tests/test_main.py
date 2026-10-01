"""Tests del punto de entrada (main.main): ultima linea de defensa."""
import pytest

import logging_config
import main
import ui.menu
from exceptions.not_found import MovieNotFoundError


def test_keyboard_interrupt_sale_cero(monkeypatch, capsys):
    monkeypatch.setattr(ui.menu, "menu_principal", lambda: (_ for _ in ()).throw(KeyboardInterrupt()))
    monkeypatch.setattr(logging_config, "configure_logging", lambda: None)
    with pytest.raises(SystemExit) as excinfo:
        main.main()
    assert excinfo.value.code == 0
    assert "Programa interrumpido" in capsys.readouterr().out


def test_application_error_registra_y_mensaje_amigable(monkeypatch, capsys):
    def explota():
        raise MovieNotFoundError("peli")

    monkeypatch.setattr(ui.menu, "menu_principal", explota)
    monkeypatch.setattr(logging_config, "configure_logging", lambda: None)
    with pytest.raises(SystemExit) as excinfo:
        main.main()
    assert excinfo.value.code == 1
    out = capsys.readouterr().out
    assert "Ocurrió un error inesperado" in out
    assert "peli" not in out


def test_error_inesperado_mensaje_generico_sin_traza(monkeypatch, capsys):
    def explota():
        raise RuntimeError("secreto interno")

    monkeypatch.setattr(ui.menu, "menu_principal", explota)
    monkeypatch.setattr(logging_config, "configure_logging", lambda: None)
    with pytest.raises(SystemExit) as excinfo:
        main.main()
    assert excinfo.value.code == 1
    out = capsys.readouterr().out
    assert "Ocurrió un error inesperado" in out
    assert "secreto interno" not in out
    assert "Traceback" not in out