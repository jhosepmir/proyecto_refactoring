"""Tests de configuracion en runtime (config.CONFIG) - SEGURIDAD FASE 5."""
import importlib

import pytest

import config


@pytest.fixture
def recargar_config(monkeypatch):
    """Recarga config.py con un entorno concreto y restaura el modulo al final.

    config.CONFIG se construye al importar, asi que la unica forma de probar
    la lectura de variables de entorno es recargar el modulo. Se conservan y
    restauran CONFIG y manager para que el resto de la suite siga viendo el
    mismo modulo que antes del test.
    """
    previos = (config.CONFIG, config.manager)

    def _recargar(**entorno):
        for clave, valor in entorno.items():
            if valor is None:
                monkeypatch.delenv(clave, raising=False)
            else:
                monkeypatch.setenv(clave, valor)
        importlib.reload(config)

    yield _recargar
    config.CONFIG, config.manager = previos


def test_conig_contiene_clave_omdb_desde_fallback(recargar_config):
    recargar_config(OMDB_API_KEY=None, TMDB_API_KEY=None)
    assert config.CONFIG["api_key_omdb"] == "trilogy"


def test_conig_clave_tmdb_vacia_por_defecto(recargar_config):
    recargar_config(TMDB_API_KEY=None)
    assert config.CONFIG["api_key_tmdb"] == ""


def test_conig_clave_omdb_leida_desde_entorno(recargar_config):
    recargar_config(OMDB_API_KEY="clave-desde-ambiente", TMDB_API_KEY=None)
    assert config.CONFIG["api_key_omdb"] == "clave-desde-ambiente"


def test_conig_clave_omdb_sobreescribible_en_runtime(monkeypatch):
    monkeypatch.setitem(config.CONFIG, "api_key_omdb", "otra-clave")
    assert config.CONFIG["api_key_omdb"] == "otra-clave"


def test_config_get_y_secciones():
    assert config.get("network_config", "timeout") == 30
    assert config.get("network_config", "no_existe", "fallback") == "fallback"
    assert "network_config" in config.sections()
    assert config.section("network_config") is not None
    assert config.get_all("network_config")["timeout"] == 30


def test_config_validate_y_resumen_sin_errores():
    assert config.validate("network_config") == []
    assert config.summary("network_config")["timeout"] == 30
    assert config.get_all("network_config") == config.summary("network_config")