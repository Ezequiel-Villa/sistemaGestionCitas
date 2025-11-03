from datetime import timedelta
import pytest

from crud import citas_repo
from services import WorldTimeService

# Aplica el fixture 'mock_world_time' a TODO el módulo para evitar llamadas reales
pytestmark = pytest.mark.usefixtures("mock_world_time")

def test_root_endpoint(client):
    """El endpoint raíz debe responder 200 y un mensaje de salud."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "API de Citas Médicas funcionando correctamente",
    }

def test_health_endpoint_sin_citas(client):
    """Si no hay citas, /health debe reportar 0."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "total_citas": 0}

def test_crear_cita_exitosa(client, future_datetime):
    """
    Crear una cita válida debe retornar 201, asignar ID incremental
    y reflejar los datos enviados más el estado inicial.
    """
    nueva_cita = {
        "paciente": "Juan Pérez",
        "medico": "Dra. María López",
        "especialidad": "Dermatología",
        "fecha": future_datetime.isoformat(),
        "motivo": "Consulta general",
        "timezone": "America/Mexico_City",
    }
    response = client.post("/citas", json=nueva_cita)
    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 1
    assert data["paciente"] == "Juan Pérez"
    assert data["estado"] == "Pendiente"
    assert data["fecha"] == future_datetime.isoformat()

def test_crear_cita_con_datos_incompletos(client, future_datetime):
    """Faltan campos obligatorios -> FastAPI debe devolver 422 (validación Pydantic)."""
    cita_invalida = {
        "paciente": "Ana",
        "fecha": future_datetime.isoformat(),
    }
    response = client.post("/citas", json=cita_invalida)
    assert response.status_code == 422

def test_crear_cita_en_feriado(client):
    """
    Si la fecha cae en feriado (Navidad 12-25), el servicio mockeado responde error 400
    con detalle que incluye 'feriado': 'Navidad'.
    """
    cita_feriado = {
        "paciente": "Laura Fiestas",
        "medico": "Dr. Noel",
        "fecha": "2025-12-25T09:00:00",
    }
    response = client.post("/citas", json=cita_feriado)
    assert response.status_code == 400
    detalle = response.json()["detail"]
    assert detalle["error"] == "Fecha inválida"
    assert detalle["detalles"]["feriado"] == "Navidad"

def test_obtener_cita_por_id(client, future_datetime):
    """Crea una cita y verifica que GET /citas/{id} la devuelva correctamente."""
    response_creacion = client.post(
        "/citas",
        json={
            "paciente": "Ana García",
            "medico": "Dr. Carlos Ruiz",
            "fecha": future_datetime.isoformat(),
            "motivo": "Chequeo",
        },
    )
    cita_id = response_creacion.json()["id"]

    response = client.get(f"/citas/{cita_id}")
    assert response.status_code == 200
    assert response.json()["medico"] == "Dr. Carlos Ruiz"

def test_obtener_cita_inexistente(client):
    """ID inexistente -> 404 con mensaje 'no encontrada'."""
    response = client.get("/citas/999")
    assert response.status_code == 404
    assert "no encontrada" in response.json()["detail"]

def test_listar_citas(client, future_datetime):
    """Crea tres citas y verifica que /citas las liste todas."""
    for offset in (5, 10, 15):
        client.post(
            "/citas",
            json={
                "paciente": f"Paciente {offset}",
                "medico": "Dr. Lista",
                "fecha": (future_datetime + timedelta(days=offset)).isoformat(),
            },
        )

    response = client.get("/citas")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert {item["paciente"] for item in data} == {
        "Paciente 5",
        "Paciente 10",
        "Paciente 15",
    }

def test_actualizar_cita(client, future_datetime):
    """PUT /citas/{id} debe permitir actualizar estado y motivo."""
    response_creacion = client.post(
        "/citas",
        json={
            "paciente": "Roberto López",
            "medico": "Dr. Fernando",
            "fecha": future_datetime.isoformat(),
        },
    )
    cita_id = response_creacion.json()["id"]

    response_actualizacion = client.put(
        f"/citas/{cita_id}",
        json={"estado": "Completada", "motivo": "Consulta resuelta"},
    )
    assert response_actualizacion.status_code == 200
    data = response_actualizacion.json()
    assert data["estado"] == "Completada"
    assert data["motivo"] == "Consulta resuelta"

def test_actualizar_cita_con_fecha_pasada(client, future_datetime, past_datetime):
    """Cambiar la fecha a una del pasado debe devolver 400 'Fecha inválida'."""
    response_creacion = client.post(
        "/citas",
        json={
            "paciente": "Paciente Tiempo",
            "medico": "Dr. Crono",
            "fecha": future_datetime.isoformat(),
        },
    )
    cita_id = response_creacion.json()["id"]

    response = client.put(f"/citas/{cita_id}", json={"fecha": past_datetime.isoformat()})
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "Fecha inválida"

def test_eliminar_cita(client, future_datetime):
    """DELETE /citas/{id} debe borrar la cita y devolver 204 sin cuerpo."""
    response_creacion = client.post(
        "/citas",
        json={
            "paciente": "Carlos",
            "medico": "Dra. Sofía",
            "fecha": future_datetime.isoformat(),
        },
    )
    cita_id = response_creacion.json()["id"]

    response_eliminacion = client.delete(f"/citas/{cita_id}")
    assert response_eliminacion.status_code == 204
    assert citas_repo.get_by_id(cita_id) is None

def test_eliminar_cita_inexistente(client):
    """Eliminar un ID inexistente -> 404."""
    response = client.delete("/citas/999")
    assert response.status_code == 404

def test_endpoint_estatico(client):
    """GET /app debe servir el index.html (content-type text/html)."""
    response = client.get("/app")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"].lower()

@pytest.mark.parametrize(
    "endpoint",
    [
        "/time/current?timezone=America/Tijuana",
        "/time/timezones",
        "/time/validate?fecha=2025-01-15T10:00:00&timezone=America/Tijuana"
    ],
)
def test_endpoints_world_time_disponibles(client, endpoint):
    """
    Verifica que los endpoints del servicio de tiempo respondan 200 cuando el mock está activo.
    """
    response = client.get(endpoint) if "validate" not in endpoint else client.post(endpoint)
    assert response.status_code == 200

def test_endpoints_world_time_error_controlado(monkeypatch, client):
    """
    Si el servicio externo falla (simulado devolviendo None),
    el endpoint debe responder 503 con un mensaje claro.
    """
    async def fake_timezones():
        return None

    monkeypatch.setattr(WorldTimeService, "get_timezones", fake_timezones)
    response = client.get("/time/timezones")
    assert response.status_code == 503
    assert "No se pudo" in response.json()["detail"]