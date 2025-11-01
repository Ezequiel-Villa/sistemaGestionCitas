from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from crud import citas_repo
from models import CitaCreate, CitaResponse, CitaUpdate
from services import WorldTimeService

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Sistema de Citas Médicas",
    description="API REST y experiencia web para gestionar citas médicas",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", tags=["Health"])
def root():
    """Endpoint raíz para verificar que la API está funcionando"""
    return {"status": "ok", "message": "API de Citas Médicas funcionando correctamente"}


@app.get("/app", include_in_schema=False)
def serve_frontend():
    """Servir la aplicación web estática"""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interfaz no disponible")
    return FileResponse(index_path)


@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint de salud"""
    return {
        "status": "healthy",
        "total_citas": len(citas_repo.citas),
    }


@app.post("/citas", response_model=CitaResponse, status_code=status.HTTP_201_CREATED, tags=["Citas"])
async def crear_cita(cita: CitaCreate):
    """Crear una nueva cita médica validando la fecha con WorldTimeAPI"""

    validacion = await WorldTimeService.validate_appointment_date(cita.fecha.isoformat())

    if not validacion["valida"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Fecha inválida",
                "mensaje": validacion["mensaje"],
                "detalles": validacion,
            },
        )

    nueva_cita = citas_repo.create(cita)
    return nueva_cita


@app.get("/citas", response_model=List[CitaResponse], tags=["Citas"])
def obtener_todas_las_citas():
    """Obtener todas las citas médicas registradas"""
    return citas_repo.get_all()


@app.get("/citas/{cita_id}", response_model=CitaResponse, tags=["Citas"])
def obtener_cita(cita_id: int):
    """Obtener una cita específica por su ID"""
    cita = citas_repo.get_by_id(cita_id)
    if not cita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con id {cita_id} no encontrada",
        )
    return cita


@app.put("/citas/{cita_id}", response_model=CitaResponse, tags=["Citas"])
async def actualizar_cita(cita_id: int, cita_update: CitaUpdate):
    """Actualizar una cita existente"""

    if cita_update.fecha:
        validacion = await WorldTimeService.validate_appointment_date(cita_update.fecha.isoformat())

        if not validacion["valida"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Fecha inválida",
                    "mensaje": validacion["mensaje"],
                    "detalles": validacion,
                },
            )

    cita_actualizada = citas_repo.update(cita_id, cita_update)
    if not cita_actualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con id {cita_id} no encontrada",
        )
    return cita_actualizada


@app.delete("/citas/{cita_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Citas"])
def eliminar_cita(cita_id: int):
    """Eliminar una cita médica"""
    eliminada = citas_repo.delete(cita_id)
    if not eliminada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con id {cita_id} no encontrada",
        )
    return None


@app.get("/time/current", tags=["WorldTimeAPI"])
async def obtener_hora_actual(timezone: str = "America/Tijuana"):
    """Obtener la hora actual de una zona horaria específica usando WorldTimeAPI"""
    time_data = await WorldTimeService.get_current_time(timezone)

    if not time_data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar con WorldTimeAPI",
        )

    return {
        "timezone": time_data.get("timezone"),
        "datetime": time_data.get("datetime"),
        "date": time_data.get("datetime", "").split("T")[0],
        "time": time_data.get("datetime", "").split("T")[1].split(".")[0]
        if "T" in time_data.get("datetime", "")
        else "",
        "day_of_week": time_data.get("day_of_week"),
        "day_of_year": time_data.get("day_of_year"),
        "week_number": time_data.get("week_number"),
    }


@app.get("/time/timezones", tags=["WorldTimeAPI"])
async def obtener_zonas_horarias():
    """Obtener lista de zonas horarias disponibles"""
    timezones = await WorldTimeService.get_timezones()

    if not timezones:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo obtener la lista de zonas horarias",
        )

    america_timezones = [tz for tz in timezones if tz.startswith("America/")]

    return {
        "total": len(timezones),
        "america_count": len(america_timezones),
        "america_timezones": america_timezones[:20],
        "ejemplo_uso": "GET /time/current?timezone=America/Tijuana",
    }


@app.post("/time/validate", tags=["WorldTimeAPI"])
async def validar_fecha_cita(fecha: str, timezone: str = "America/Tijuana"):
    """Validar si una fecha es válida para agendar una cita (no está en el pasado)"""
    validacion = await WorldTimeService.validate_appointment_date(fecha, timezone)
    return validacion


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
