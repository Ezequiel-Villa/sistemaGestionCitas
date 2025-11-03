# Sistema de Citas Médicas - FastAPI

Aplicación web con backend FastAPI para administrar citas médicas desde una SPA servida en `/app`.

## Requisitos previos

- Python 3.11 o superior
- (Opcional) Entorno virtual de Python para aislar dependencias
- Dependencias instaladas mediante `pip install -r requirements.txt`

## Estructura del proyecto

```
proyecto/
│
├── main.py          # API FastAPI y servidor de archivos estáticos
├── models.py        # Modelos de datos y validaciones Pydantic
├── crud.py          # Operaciones CRUD en memoria
├── services.py      # Integración con WorldTimeAPI
├── static/          # Aplicación web (HTML, CSS, JS)
├── test_main.py     # Pruebas con pytest y TestClient
└── requirements.txt # Dependencias del proyecto
```
