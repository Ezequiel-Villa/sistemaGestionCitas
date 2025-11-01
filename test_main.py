import pytest
from fastapi.testclient import TestClient
from main import app
from crud import citas_repo
from datetime import datetime, timedelta


@pytest.fixture(autouse=True)
def reset_repository():
    """Fixture que limpia el repositorio antes de cada test"""
    citas_repo.clear()
    yield
    citas_repo.clear()


@pytest.fixture
def client():
    """Fixture que proporciona el TestClient de FastAPI"""
    return TestClient(app)


def test_root_endpoint(client):
    """Test del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_endpoint(client):
    """Test del endpoint de salud"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


def test_crear_cita(client):
    """Test para crear una cita médica"""
    nueva_cita = {
        "paciente": "Juan Pérez",
        "medico": "Dra. María López",
        "fecha": "2025-11-15T10:30:00",
        "motivo": "Consulta general"
    }
    
    response = client.post("/citas", json=nueva_cita)
    
    assert response.status_code == 201
    data = response.json()
    assert data["paciente"] == "Juan Pérez"
    assert data["medico"] == "Dra. María López"
    assert data["fecha"] == "2025-11-15T10:30:00"
    assert data["motivo"] == "Consulta general"
    assert "id" in data
    assert data["id"] == 1


def test_crear_y_obtener_cita(client):
    """Test para crear una cita y luego obtenerla por ID"""
    # Crear la cita
    nueva_cita = {
        "paciente": "Ana García",
        "medico": "Dr. Carlos Ruiz",
        "fecha": "2025-12-01T14:00:00",
        "motivo": "Chequeo anual"
    }
    
    response_create = client.post("/citas", json=nueva_cita)
    assert response_create.status_code == 201
    cita_id = response_create.json()["id"]
    
    # Obtener la cita creada
    response_get = client.get(f"/citas/{cita_id}")
    assert response_get.status_code == 200
    
    data = response_get.json()
    assert data["id"] == cita_id
    assert data["paciente"] == "Ana García"
    assert data["medico"] == "Dr. Carlos Ruiz"


def test_obtener_todas_las_citas(client):
    """Test para obtener todas las citas"""
    # Crear dos citas
    cita1 = {
        "paciente": "Pedro Sánchez",
        "medico": "Dr. Luis Hernández",
        "fecha": "2025-11-20T09:00:00"
    }
    cita2 = {
        "paciente": "Laura Martínez",
        "medico": "Dra. Elena Gómez",
        "fecha": "2025-11-21T11:00:00",
        "motivo": "Seguimiento"
    }
    
    client.post("/citas", json=cita1)
    client.post("/citas", json=cita2)
    
    # Obtener todas las citas
    response = client.get("/citas")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["paciente"] == "Pedro Sánchez"
    assert data[1]["paciente"] == "Laura Martínez"


def test_actualizar_cita(client):
    """Test para actualizar una cita existente"""
    # Crear cita
    nueva_cita = {
        "paciente": "Roberto López",
        "medico": "Dr. Fernando Díaz",
        "fecha": "2025-11-25T16:00:00",
        "motivo": "Consulta inicial"
    }
    response_create = client.post("/citas", json=nueva_cita)
    cita_id = response_create.json()["id"]
    
    # Actualizar la cita
    actualizacion = {
        "fecha": "2025-11-26T10:00:00",
        "motivo": "Consulta reprogramada"
    }
    response_update = client.put(f"/citas/{cita_id}", json=actualizacion)
    
    assert response_update.status_code == 200
    data = response_update.json()
    assert data["fecha"] == "2025-11-26T10:00:00"
    assert data["motivo"] == "Consulta reprogramada"
    assert data["paciente"] == "Roberto López"  # No cambió


def test_eliminar_cita(client):
    """Test para eliminar una cita"""
    # Crear cita
    nueva_cita = {
        "paciente": "Sofia Ramírez",
        "medico": "Dra. Patricia Torres",
        "fecha": "2025-12-05T13:00:00"
    }
    response_create = client.post("/citas", json=nueva_cita)
    cita_id = response_create.json()["id"]
    
    # Eliminar la cita
    response_delete = client.delete(f"/citas/{cita_id}")
    assert response_delete.status_code == 204
    
    # Verificar que ya no existe
    response_get = client.get(f"/citas/{cita_id}")
    assert response_get.status_code == 404


def test_obtener_cita_inexistente(client):
    """Test para intentar obtener una cita que no existe"""
    response = client.get("/citas/999")
    assert response.status_code == 404
    assert "no encontrada" in response.json()["detail"]


def test_actualizar_cita_inexistente(client):
    """Test para intentar actualizar una cita que no existe"""
    actualizacion = {"motivo": "Nuevo motivo"}
    response = client.put("/citas/999", json=actualizacion)
    assert response.status_code == 404


def test_eliminar_cita_inexistente(client):
    """Test para intentar eliminar una cita que no existe"""
    response = client.delete("/citas/999")
    assert response.status_code == 404


def test_crear_cita_sin_motivo(client):
    """Test para crear una cita sin el campo opcional 'motivo'"""
    nueva_cita = {
        "paciente": "Miguel Ángel",
        "medico": "Dr. José Morales",
        "fecha": "2025-11-30T15:00:00"
    }
    
    response = client.post("/citas", json=nueva_cita)
    assert response.status_code == 201
    data = response.json()
    assert data["motivo"] is None


# ===== TESTS DE WORLDTIMEAPI =====

def test_obtener_hora_actual(client):
    """Test para obtener la hora actual de una zona horaria"""
    response = client.get("/time/current?timezone=America/Tijuana")
    assert response.status_code == 200
    
    data = response.json()
    assert "timezone" in data
    assert "datetime" in data
    assert data["timezone"] == "America/Tijuana"


def test_obtener_zonas_horarias(client):
    """Test para obtener lista de zonas horarias"""
    response = client.get("/time/timezones")
    assert response.status_code == 200
    
    data = response.json()
    assert "total" in data
    assert "america_timezones" in data
    assert len(data["america_timezones"]) > 0


def test_validar_fecha_futura(client):
    """Test para validar una fecha futura (válida)"""
    # Crear una fecha futura
    fecha_futura = (datetime.now() + timedelta(days=30)).isoformat()
    
    response = client.post(f"/time/validate?fecha={fecha_futura}&timezone=America/Tijuana")
    assert response.status_code == 200
    
    data = response.json()
    assert "valida" in data
    assert data["valida"] == True


def test_validar_fecha_pasada(client):
    """Test para validar una fecha pasada (inválida)"""
    # Crear una fecha en el pasado
    fecha_pasada = "2020-01-01T10:00:00"
    
    response = client.post(f"/time/validate?fecha={fecha_pasada}&timezone=America/Tijuana")
    assert response.status_code == 200
    
    data = response.json()
    assert "valida" in data
    assert data["valida"] == False
    assert "mensaje" in data


def test_crear_cita_con_fecha_pasada(client):
    """Test para intentar crear una cita con fecha en el pasado"""
    cita_invalida = {
        "paciente": "Test Usuario",
        "medico": "Dr. Test",
        "fecha": "2020-01-01T10:00:00",
        "motivo": "Consulta de prueba"
    }
    
    response = client.post("/citas", json=cita_invalida)
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data


def test_actualizar_cita_con_fecha_futura(client):
    """Test para actualizar una cita con fecha válida"""
    # Crear cita con fecha futura
    fecha_futura = (datetime.now() + timedelta(days=10)).isoformat()
    nueva_cita = {
        "paciente": "Test Update",
        "medico": "Dr. Update",
        "fecha": fecha_futura
    }
    
    response_create = client.post("/citas", json=nueva_cita)
    assert response_create.status_code == 201
    cita_id = response_create.json()["id"]
    
    # Actualizar con otra fecha futura
    nueva_fecha = (datetime.now() + timedelta(days=20)).isoformat()
    response_update = client.put(f"/citas/{cita_id}", json={"fecha": nueva_fecha})
    
    assert response_update.status_code == 200
    data = response_update.json()
    assert data["fecha"] == nueva_fecha