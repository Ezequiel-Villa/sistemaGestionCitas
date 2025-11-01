import httpx
from typing import Optional
from datetime import datetime


class WorldTimeService:
    """Servicio para interactuar con WorldTimeAPI"""
    
    BASE_URL = "https://worldtimeapi.org/api"
    
    @staticmethod
    async def get_current_time(timezone: str = "America/Tijuana") -> Optional[dict]:
        """
        Obtener la hora actual de una zona horaria específica
        
        Args:
            timezone: Zona horaria (ej: America/Tijuana, America/Mexico_City)
        
        Returns:
            Diccionario con información de tiempo o None si hay error
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{WorldTimeService.BASE_URL}/timezone/{timezone}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error al obtener tiempo: {e}")
            return None
    
    @staticmethod
    async def validate_appointment_date(fecha_cita: str, timezone: str = "America/Tijuana") -> dict:
        """
        Validar si una fecha de cita es válida (no es en el pasado)
        
        Args:
            fecha_cita: Fecha de la cita en formato ISO
            timezone: Zona horaria a validar
        
        Returns:
            Diccionario con resultado de validación
        """
        time_data = await WorldTimeService.get_current_time(timezone)
        
        if not time_data:
            return {
                "valida": True,  # Si no podemos validar, asumimos que es válida
                "mensaje": "No se pudo validar con WorldTimeAPI, se permite la cita",
                "timezone": timezone
            }
        
        try:
            # Obtener la hora actual de la API
            current_datetime = datetime.fromisoformat(time_data["datetime"].replace("Z", "+00:00"))
            
            # Parsear la fecha de la cita
            appointment_datetime = datetime.fromisoformat(fecha_cita.replace("Z", "+00:00"))
            
            # Validar que la cita no sea en el pasado
            if appointment_datetime < current_datetime:
                return {
                    "valida": False,
                    "mensaje": f"La fecha de la cita está en el pasado. Hora actual: {current_datetime.isoformat()}",
                    "timezone": timezone,
                    "hora_actual": time_data["datetime"],
                    "fecha_cita": fecha_cita
                }
            
            return {
                "valida": True,
                "mensaje": "Fecha de cita válida",
                "timezone": timezone,
                "hora_actual": time_data["datetime"],
                "fecha_cita": fecha_cita
            }
            
        except Exception as e:
            return {
                "valida": True,  # Si hay error en parsing, permitimos la cita
                "mensaje": f"Error al validar fecha: {str(e)}",
                "timezone": timezone
            }
    
    @staticmethod
    async def get_timezones() -> Optional[list]:
        """Obtener lista de zonas horarias disponibles"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{WorldTimeService.BASE_URL}/timezone")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error al obtener zonas horarias: {e}")
            return None