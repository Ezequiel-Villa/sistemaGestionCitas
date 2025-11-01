from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from crud import citas_repo
from main import app
from services import WorldTimeService

REFERENCE_TIME = datetime(2025, 1, 1, 12, 0, 0)


@pytest.fixture(autouse=True)
def reset_repository():
    """Limpiar el repositorio antes y después de cada prueba"""
    citas_repo.clear()
    yield
    citas_repo.clear()


@pytest.fixture(autouse=True)
def mock_world_time(monkeypatch):
    """Simular las respuestas de WorldTimeAPI para las pruebas"""

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
def client():
    """Cliente de pruebas de FastAPI"""
    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["total_citas"] == 0


def test_crear_cita(client):
    nueva_cita = {
        "paciente": "Juan Pérez",
        "medico": "Dra. María López",
        "especialidad": "Dermatología",
        "fecha": "2025-11-15T10:30:00",
        "motivo": "Consulta general",
    }

    response = client.post("/citas", json=nueva_cita)
    assert response.status_code == 201

    data = response.json()
    assert data["paciente"] == "Juan Pérez"
    assert data["especialidad"] == "Dermatología"
    assert data["estado"] == "Pendiente"
    assert data["fecha"] == "2025-11-15T10:30:00"
    assert data["id"] == 1


def test_crear_y_obtener_cita(client):
    nueva_cita = {
        "paciente": "Ana García",
        "medico": "Dr. Carlos Ruiz",
        "especialidad": "Medicina General",
        "fecha": "2025-12-01T14:00:00",
        "motivo": "Chequeo anual",
    }

    response_create = client.post("/citas", json=nueva_cita)
    cita_id = response_create.json()["id"]

    response_get = client.get(f"/citas/{cita_id}")
    assert response_get.status_code == 200

    data = response_get.json()
    assert data["id"] == cita_id
    assert data["paciente"] == "Ana García"
    assert data["medico"] == "Dr. Carlos Ruiz"


def test_obtener_todas_las_citas(client):
    cita1 = {
        "paciente": "Pedro Sánchez",
        "medico": "Dr. Luis Hernández",
        "fecha": "2025-11-20T09:00:00",
    }
    cita2 = {
        "paciente": "Laura Martínez",
        "medico": "Dra. Elena Gómez",
        "fecha": "2025-11-21T11:00:00",
        "motivo": "Seguimiento",
    }

    client.post("/citas", json=cita1)
    client.post("/citas", json=cita2)

    response = client.get("/citas")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["paciente"] == "Pedro Sánchez"
    assert data[1]["paciente"] == "Laura Martínez"


def test_actualizar_cita(client):
    nueva_cita = {
        "paciente": "Roberto López",
        "medico": "Dr. Fernando Díaz",
        "fecha": "2025-11-25T16:00:00",
        "motivo": "Consulta inicial",
    }
    response_create = client.post("/citas", json=nueva_cita)
    cita_id = response_create.json()["id"]

    actualizacion = {
        "motivo": "Consulta de seguimiento",
        "estado": "Completada",
    }

    response_update = client.put(f"/citas/{cita_id}", json=actualizacion)
    assert response_update.status_code == 200
    data = response_update.json()
    assert data["motivo"] == "Consulta de seguimiento"
    assert data["estado"] == "Completada"


def test_eliminar_cita(client):
    nueva_cita = {
        "paciente": "Carlos Ramírez",
        "medico": "Dra. Sofía Torres",
        "fecha": "2025-11-22T18:00:00",
    }
    response_create = client.post("/citas", json=nueva_cita)
    cita_id = response_create.json()["id"]

    response_delete = client.delete(f"/citas/{cita_id}")
    assert response_delete.status_code == 204

    response_get = client.get(f"/citas/{cita_id}")
    assert response_get.status_code == 404


def test_validaciones_de_error(client):
    response = client.get("/citas/999")
    assert response.status_code == 404

    actualizacion = {"motivo": "Nuevo motivo"}
    response_update = client.put("/citas/999", json=actualizacion)
    assert response_update.status_code == 404

    response_delete = client.delete("/citas/999")
    assert response_delete.status_code == 404


def test_crear_cita_sin_motivo(client):
    nueva_cita = {
        "paciente": "Miguel Ángel",
        "medico": "Dr. José Morales",
        "fecha": "2025-11-30T15:00:00",
    }

    response = client.post("/citas", json=nueva_cita)
    assert response.status_code == 201
    data = response.json()
    assert data["motivo"] is None
    assert data["estado"] == "Pendiente"


# ===== WORLD TIME API TESTS =====


def test_obtener_hora_actual(client):
    response = client.get("/time/current?timezone=America/Tijuana")
    assert response.status_code == 200

    data = response.json()
    assert data["timezone"] == "America/Tijuana"
    assert data["datetime"] == REFERENCE_TIME.isoformat()


def test_obtener_zonas_horarias(client):
    response = client.get("/time/timezones")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 3
    assert "America/Tijuana" in data["america_timezones"]


def test_validar_fecha_futura(client):
    fecha_futura = (REFERENCE_TIME + timedelta(days=30)).isoformat()

    response = client.post(f"/time/validate?fecha={fecha_futura}&timezone=America/Tijuana")
    assert response.status_code == 200

    data = response.json()
    assert data["valida"] is True


def test_validar_fecha_pasada(client):
    fecha_pasada = (REFERENCE_TIME - timedelta(days=10)).isoformat()

    response = client.post(f"/time/validate?fecha={fecha_pasada}&timezone=America/Tijuana")
    assert response.status_code == 200

    data = response.json()
    assert data["valida"] is False


def test_crear_cita_con_fecha_pasada(client):
    cita_invalida = {
        "paciente": "Test Usuario",
        "medico": "Dr. Test",
        "fecha": (REFERENCE_TIME - timedelta(days=1)).isoformat(),
        "motivo": "Consulta de prueba",
    }

    response = client.post("/citas", json=cita_invalida)
    assert response.status_code == 400


def test_actualizar_cita_con_fecha_futura(client):
    fecha_futura = (REFERENCE_TIME + timedelta(days=10)).isoformat()
    nueva_cita = {
        "paciente": "Test Update",
        "medico": "Dr. Update",
        "fecha": fecha_futura,
    }

    response_create = client.post("/citas", json=nueva_cita)
    cita_id = response_create.json()["id"]

    nueva_fecha = (REFERENCE_TIME + timedelta(days=20)).isoformat()
    response_update = client.put(f"/citas/{cita_id}", json={"fecha": nueva_fecha})

    assert response_update.status_code == 200
    data = response_update.json()
    assert data["fecha"] == nueva_fecha

