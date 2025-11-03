from datetime import datetime, timedelta 
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

# --- Ajuste del sys.path para poder hacer 'from crud import ...' y 'from main import app'
#     sin instalar el paquete. Asume que este archivo está en /tests y sube un nivel.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from crud import citas_repo            # Repositorio en memoria de las citas
from main import app                   # Instancia FastAPI a testear
from services import WorldTimeService  # Servicio que consulta worldtimeapi (mockearemos)

# Tiempo de referencia fijo para que las pruebas sean deterministas
REFERENCE_TIME = datetime(2025, 1, 1, 12, 0, 0)

@pytest.fixture(autouse=True)
def reset_repository():
    """
    Fixture que se ejecuta AUTOMÁTICAMENTE antes y después de cada test.
    Deja el 'citas_repo' limpio para que los tests no se contaminen entre sí.
    """
    citas_repo.clear()
    yield
    citas_repo.clear()

@pytest.fixture
def mock_world_time(monkeypatch):
    """
    Reemplaza (monkeypatch) los métodos asíncronos del WorldTimeService por
    versiones falsas (no llaman a Internet). Así las pruebas son rápidas y reproducibles.
    """

    async def fake_get_current_time(timezone: str = "America/Tijuana"):
        # Simula la respuesta de worldtimeapi con un datetime fijo
        return {
            "timezone": timezone,
            "datetime": REFERENCE_TIME.isoformat(),
            "day_of_week": REFERENCE_TIME.isoweekday() % 7,
            "day_of_year": REFERENCE_TIME.timetuple().tm_yday,
            "week_number": int(REFERENCE_TIME.strftime("%W")),
        }

    async def fake_validate_appointment_date(fecha_cita: str, timezone: str = "America/Tijuana"):
        """
        Implementa la misma lógica de validación que haría el servicio real:
        - Rechaza feriados definidos en WorldTimeService.HOLIDAYS
        - Rechaza fechas en el pasado respecto a REFERENCE_TIME
        - Acepta el resto
        """
        try:
            appointment_datetime = datetime.fromisoformat(fecha_cita.replace("Z", "+00:00"))
        except ValueError:
            appointment_datetime = datetime.fromisoformat(fecha_cita)

        holiday_name = WorldTimeService.HOLIDAYS.get(appointment_datetime.strftime("%m-%d"))
        if (holiday_name):
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
        # Simula lista de zonas horarias disponibles
        return ["America/Tijuana", "America/Mexico_City", "Europe/Madrid"]

    # Inyección de dependencias por monkeypatch
    monkeypatch.setattr(WorldTimeService, "get_current_time", fake_get_current_time)
    monkeypatch.setattr(WorldTimeService, "validate_appointment_date", fake_validate_appointment_date)
    monkeypatch.setattr(WorldTimeService, "get_timezones", fake_get_timezones)

@pytest.fixture
def client(mock_world_time):
    """
    Crea un cliente HTTP de pruebas contra la app FastAPI.
    Depende de 'mock_world_time' para que todas las llamadas a tiempo/feriados estén mockeadas.
    """
    return TestClient(app)

# Helpers de tiempo para reutilizar en varios tests
@pytest.fixture
def reference_time():
    return REFERENCE_TIME

@pytest.fixture
def future_datetime(reference_time):
    # Fecha futura determinista (10 días después del REFERENCE_TIME)
    return reference_time + timedelta(days=10)

@pytest.fixture
def past_datetime(reference_time):
    # Fecha en el pasado (5 días antes del REFERENCE_TIME)
    return reference_time - timedelta(days=5)