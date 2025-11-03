from datetime import datetime, timedelta
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from crud import citas_repo
from main import app
from services import WorldTimeService

REFERENCE_TIME = datetime(2025, 1, 1, 12, 0, 0)


@pytest.fixture(autouse=True)
def reset_repository():
    """Garantiza un repositorio limpio antes y después de cada prueba."""
    citas_repo.clear()
    yield
    citas_repo.clear()


@pytest.fixture
def mock_world_time(monkeypatch):
    """Simula las respuestas de WorldTimeService para evitar llamadas externas."""

    async def fake_get_current_time(timezone: str = "America/Tijuana"):
        return {
            "timezone": timezone,
            "datetime": REFERENCE_TIME.isoformat(),
            "day_of_week": REFERENCE_TIME.isoweekday() % 7,
            "day_of_year": REFERENCE_TIME.timetuple().tm_yday,
            "week_number": int(REFERENCE_TIME.strftime("%W")),
        }

    async def fake_validate_appointment_date(fecha_cita: str, timezone: str = "America/Tijuana"):
        try:
            appointment_datetime = datetime.fromisoformat(fecha_cita.replace("Z", "+00:00"))
        except ValueError:
            appointment_datetime = datetime.fromisoformat(fecha_cita)

        holiday_name = WorldTimeService.HOLIDAYS.get(appointment_datetime.strftime("%m-%d"))
        if holiday_name:
            return {
                "valida": False,
                "mensaje": f"No se permiten citas en {holiday_name}.",
                "timezone": timezone,
                "hora_actual": REFERENCE_TIME.isoformat(),
                "fecha_cita": fecha_cita,
                "feriado": holiday_name,
            }

        if appointment_datetime < REFERENCE_TIME:
            return {
                "valida": False,
                "mensaje": "La fecha de la cita está en el pasado.",
                "timezone": timezone,
                "hora_actual": REFERENCE_TIME.isoformat(),
                "fecha_cita": fecha_cita,
            }

        return {
            "valida": True,
            "mensaje": "Fecha de cita válida",
            "timezone": timezone,
            "hora_actual": REFERENCE_TIME.isoformat(),
            "fecha_cita": fecha_cita,
        }

    async def fake_get_timezones():
        return ["America/Tijuana", "America/Mexico_City", "Europe/Madrid"]

    monkeypatch.setattr(WorldTimeService, "get_current_time", fake_get_current_time)
    monkeypatch.setattr(WorldTimeService, "validate_appointment_date", fake_validate_appointment_date)
    monkeypatch.setattr(WorldTimeService, "get_timezones", fake_get_timezones)


@pytest.fixture
def client(mock_world_time):
    """Cliente HTTP para interactuar con la API durante las pruebas."""
    return TestClient(app)


@pytest.fixture
def reference_time():
    return REFERENCE_TIME


@pytest.fixture
def future_datetime(reference_time):
    return reference_time + timedelta(days=10)


@pytest.fixture
def past_datetime(reference_time):
    return reference_time - timedelta(days=5)
