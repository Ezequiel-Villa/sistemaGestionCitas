import asyncio
from datetime import datetime, timedelta
from typing import Optional

import httpx

from services import WorldTimeService


class DummyResponse:
    def __init__(self, status_code: int = 200, data: Optional[object] = None):
        self.status_code = status_code
        self._data = data or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://test.local")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("error", request=request, response=response)

    def json(self):
        return self._data


class DummyAsyncClient:
    def __init__(self, response: DummyResponse | Exception):
        self._response = response

    async def __aenter__(self):
        if isinstance(self._response, Exception):
            raise self._response
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url: str):
        return self._response


def test_get_current_time_success(monkeypatch):
    response_data = {
        "timezone": "America/Mexico_City",
        "datetime": "2025-01-01T12:00:00+00:00",
    }

    def fake_async_client(*args, **kwargs):
        return DummyAsyncClient(DummyResponse(200, response_data))

    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client)

    result = asyncio.run(WorldTimeService.get_current_time("America/Mexico_City"))
    assert result == response_data


def test_get_current_time_error(monkeypatch):
    def fake_async_client(*args, **kwargs):
        return DummyAsyncClient(httpx.ConnectError("boom"))

    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client)

    result = asyncio.run(WorldTimeService.get_current_time("America/Mexico_City"))
    assert result is None


def test_get_holiday_name():
    fecha = datetime(2025, 12, 25, 9, 0, 0)
    assert WorldTimeService._get_holiday_name(fecha) == "Navidad"


def test_validate_appointment_date_api_indisponible(monkeypatch):
    async def fake_get_current_time(timezone: str):
        return None

    monkeypatch.setattr(WorldTimeService, "get_current_time", fake_get_current_time)

    result = asyncio.run(
        WorldTimeService.validate_appointment_date("2025-01-01T10:00:00", "America/Tijuana")
    )
    assert result["valida"] is True
    assert "No se pudo validar" in result["mensaje"]


def test_validate_appointment_date_pasado(monkeypatch):
    reference = datetime(2025, 1, 5, 12, 0, 0)
    past_date = (reference - timedelta(days=1)).isoformat()

    async def fake_get_current_time(timezone: str):
        return {"datetime": reference.isoformat()}

    monkeypatch.setattr(WorldTimeService, "get_current_time", fake_get_current_time)

    result = asyncio.run(
        WorldTimeService.validate_appointment_date(past_date, "America/Tijuana")
    )
    assert result["valida"] is False
    assert "en el pasado" in result["mensaje"]


def test_get_timezones_error(monkeypatch):
    def fake_async_client(*args, **kwargs):
        response = DummyResponse(500, {})
        return DummyAsyncClient(response)

    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client)

    result = asyncio.run(WorldTimeService.get_timezones())
    assert result is None


def test_get_timezones_success(monkeypatch):
    def fake_async_client(*args, **kwargs):
        response = DummyResponse(200, ["America/Tijuana", "Europe/Madrid"])
        return DummyAsyncClient(response)

    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client)

    result = asyncio.run(WorldTimeService.get_timezones())
    assert result == ["America/Tijuana", "Europe/Madrid"]
