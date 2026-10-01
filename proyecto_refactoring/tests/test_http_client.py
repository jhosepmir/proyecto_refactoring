"""Tests del cliente HTTP compartido (api.http_client)."""
import logging

import pytest
import requests

import config
from api.http_client import hacer_request
from exceptions.api_error import APIError, InvalidResponseError
from exceptions.configuration_error import ConfigurationError


def test_hacer_request_consulta_url_fake(fake_requests):
    result = hacer_request("http://dominio.test/ruta")
    assert fake_requests == ["http://dominio.test/ruta"]
    assert isinstance(result, dict)


def test_hacer_request_registra_debug_y_verbose(fake_requests, caplog):
    config.CONFIG["debug"] = True
    config.CONFIG["verbose"] = True
    with caplog.at_level(logging.DEBUG):
        hacer_request("http://dominio.test/ruta")
    assert "Haciendo request a http://dominio.test/ruta" in caplog.text
    assert "Status code: 200" in caplog.text


def test_hacer_request_no_registra_debug_desactivado(fake_requests, caplog):
    config.CONFIG["debug"] = False
    config.CONFIG["verbose"] = False
    with caplog.at_level(logging.DEBUG):
        hacer_request("http://dominio.test/ruta")
    assert "Haciendo request" not in caplog.text
    assert "Status code" not in caplog.text


def test_hacer_request_enmascara_apikey_en_log(fake_requests, caplog):
    config.CONFIG["debug"] = True
    with caplog.at_level(logging.DEBUG):
        hacer_request("http://dominio.test/ruta?t=Inception&apikey=trilogy")
    assert "apikey=%2A%2A%2A" in caplog.text
    assert "apikey=trilogy" not in caplog.text
    assert "t=Inception" in caplog.text


def test_hacer_request_timeout_es_error_de_api(monkeypatch):
    def get_timed_out(url, params=None, timeout=None):
        raise requests.Timeout("timeout")

    monkeypatch.setattr(requests, "get", get_timed_out)
    with pytest.raises(APIError):
        hacer_request("http://dominio.test/ruta")


def test_hacer_request_connection_error_es_error_de_api(monkeypatch):
    def get_refused(url, params=None, timeout=None):
        raise requests.ConnectionError("conexion rehusada")

    monkeypatch.setattr(requests, "get", get_refused)
    with pytest.raises(APIError):
        hacer_request("http://dominio.test/ruta")


def test_hacer_request_http_error_conserva_status_code(monkeypatch):
    class RespuestaHttpError:
        status_code = 500

        def raise_for_status(self):
            raise requests.HTTPError("boom")

        def json(self):
            return {}

    monkeypatch.setattr(requests, "get", lambda *a, **k: RespuestaHttpError())
    with pytest.raises(APIError) as excinfo:
        hacer_request("http://dominio.test/ruta")
    assert excinfo.value.status_code == 500


def test_hacer_request_json_invalido_es_invalid_response(monkeypatch):
    class RespuestaJsonInvalido:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            raise ValueError("no es JSON")

    monkeypatch.setattr(requests, "get", lambda *a, **k: RespuestaJsonInvalido())
    with pytest.raises(InvalidResponseError):
        hacer_request("http://dominio.test/ruta")


def test_hacer_request_sin_timeout_configurado_es_configuration_error(monkeypatch):
    del config.CONFIG["timeout"]
    with pytest.raises(ConfigurationError):
        hacer_request("http://dominio.test/ruta")


def test_hacer_request_request_exception_generica_es_api_error(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: (_ for _ in ()).throw(requests.RequestException("fallo generico")))
    with pytest.raises(APIError) as excinfo:
        hacer_request("http://dominio.test/ruta")
    assert "Error de comunicacion con la API externa" in str(excinfo.value)