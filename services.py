from datetime import datetime
from typing import Optional

import httpx


class WorldTimeService:
    """Servicio para interactuar con WorldTimeAPI"""

    BASE_URL = "https://worldtimeapi.org/api"

    @staticmethod
    async def get_current_time(timezone: str = "America/Tijuana") -> Optional[dict]:
        """Obtener la hora actual de una zona horaria específica"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{WorldTimeService.BASE_URL}/timezone/{timezone}")
                response.raise_for_status()
                return response.json()
        except Exception as error:  # pragma: no cover - logging auxiliar
            print(f"Error al obtener tiempo: {error}")
            return None

    @staticmethod
    async def validate_appointment_date(fecha_cita: str, timezone: str = "America/Tijuana") -> dict:
        """Validar si una fecha de cita es válida (no es en el pasado)"""
        time_data = await WorldTimeService.get_current_time(timezone)

        if not time_data:
            return {
                "valida": True,
                "mensaje": "No se pudo validar con WorldTimeAPI, se permite la cita",
                "timezone": timezone,
            }

        try:
            current_datetime = datetime.fromisoformat(time_data["datetime"].replace("Z", "+00:00"))
            appointment_datetime = datetime.fromisoformat(fecha_cita.replace("Z", "+00:00"))

            if appointment_datetime < current_datetime:
                return {
                    "valida": False,
                    "mensaje": f"La fecha de la cita está en el pasado. Hora actual: {current_datetime.isoformat()}",
                    "timezone": timezone,
                    "hora_actual": time_data["datetime"],
                    "fecha_cita": fecha_cita,
                }

            return {
                "valida": True,
                "mensaje": "Fecha de cita válida",
                "timezone": timezone,
                "hora_actual": time_data["datetime"],
                "fecha_cita": fecha_cita,
            }
        except Exception as error:  # pragma: no cover - logging auxiliar
            return {
                "valida": True,
                "mensaje": f"Error al validar fecha: {str(error)}",
                "timezone": timezone,
            }

    @staticmethod
    async def get_timezones() -> Optional[list]:
        """Obtener lista de zonas horarias disponibles"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{WorldTimeService.BASE_URL}/timezone")
                response.raise_for_status()
                return response.json()
        except Exception as error:  # pragma: no cover - logging auxiliar
            print(f"Error al obtener zonas horarias: {error}")
            return None
