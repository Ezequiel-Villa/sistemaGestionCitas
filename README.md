# Sistema de Citas Médicas - FastAPI

Sistema básico de gestión de citas médicas con API REST usando FastAPI.

## Estructura del Proyecto

```
proyecto/
│
├── main.py          # Aplicación FastAPI con todos los endpoints
├── models.py        # Modelos Pydantic para validación
├── crud.py          # Repositorio en memoria para operaciones CRUD
├── services.py      # Servicio de integración con WorldTimeAPI
├── test_main.py     # Pruebas unitarias con pytest
└── requirements.txt # Dependencias del proyecto
```

## Instalación

1. Crear un entorno virtual (opcional pero recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Ejecutar la Aplicación

```bash
python main.py
```

O usando uvicorn directamente:
```bash
uvicorn main:app --reload
```

La API estará disponible en: `http://localhost:8000`

## Documentación Interactiva

FastAPI genera automáticamente documentación interactiva:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints Disponibles

### Health Check
- `GET /` - Endpoint raíz
- `GET /health` - Estado de salud de la API

### Gestión de Citas
- `POST /citas` - Crear una nueva cita (valida fecha con WorldTimeAPI)
- `GET /citas` - Obtener todas las citas
- `GET /citas/{id}` - Obtener una cita específica
- `PUT /citas/{id}` - Actualizar una cita (valida fecha si se actualiza)
- `DELETE /citas/{id}` - Eliminar una cita

### WorldTimeAPI Integration
- `GET /time/current` - Obtener hora actual de una zona horaria
- `GET /time/timezones` - Listar zonas horarias disponibles
- `POST /time/validate` - Validar si una fecha es válida para citas

## Ejemplos de Uso

### Crear una cita
```bash
curl -X POST "http://localhost:8000/citas" \
  -H "Content-Type: application/json" \
  -d '{
    "paciente": "Juan Pérez",
    "medico": "Dra. María López",
    "fecha": "2025-11-15T10:30:00",
    "motivo": "Consulta general"
  }'
```

### Obtener todas las citas
```bash
curl -X GET "http://localhost:8000/citas"
```

### Obtener una cita específica
```bash
curl -X GET "http://localhost:8000/citas/1"
```

### Actualizar una cita
```bash
curl -X PUT "http://localhost:8000/citas/1" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha": "2025-11-16T11:00:00"
  }'
```

### Eliminar una cita
```bash
curl -X DELETE "http://localhost:8000/citas/1"
```

### Obtener hora actual (WorldTimeAPI)
```bash
curl -X GET "http://localhost:8000/time/current?timezone=America/Tijuana"
```

### Validar fecha para cita
```bash
curl -X POST "http://localhost:8000/time/validate?fecha=2025-12-01T10:00:00&timezone=America/Tijuana"
```

## Ejecutar Pruebas

Ejecutar todas las pruebas:
```bash
pytest test_main.py -v
```

Ejecutar con cobertura:
```bash
pytest test_main.py -v --cov=.
```

Ejecutar una prueba específica:
```bash
pytest test_main.py::test_crear_y_obtener_cita -v
```

## Modelo de Datos

### Cita (CitaResponse)
```json
{
  "id": 1,
  "paciente": "Juan Pérez",
  "medico": "Dra. María López",
  "fecha": "2025-11-15T10:30:00",
  "motivo": "Consulta general"
}
```

**Campos:**
- `id` (int): ID único de la cita (generado automáticamente)
- `paciente` (string): Nombre del paciente
- `medico` (string): Nombre del médico
- `fecha` (string): Fecha y hora en formato ISO 8601
- `motivo` (string, opcional): Motivo de la consulta

## Notas

- El almacenamiento es en memoria, por lo que los datos se pierden al reiniciar la aplicación
- Ideal para pruebas y desarrollo
- Los IDs se generan secuencialmente comenzando en 1
- **Integración con WorldTimeAPI**: Al crear o actualizar citas, se valida automáticamente que la fecha no esté en el pasado usando la hora real de la zona horaria especificada
- La validación de fechas usa la zona horaria de Tijuana por defecto, pero puedes especificar otras