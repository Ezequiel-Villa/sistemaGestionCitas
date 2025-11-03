from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class CitaBase(BaseModel):
    """Modelo base para una cita médica"""

    paciente: str = Field(..., min_length=1, description="Nombre del paciente")
    medico: str = Field(..., min_length=1, description="Nombre del médico")
    especialidad: Optional[str] = Field(None, min_length=1, description="Especialidad médica de la cita")
    fecha: datetime = Field(..., description="Fecha y hora de la cita en formato ISO")
    motivo: Optional[str] = Field(None, description="Motivo de la consulta")
    estado: Literal["Pendiente", "Completada", "Cancelada"] = Field(
        default="Pendiente", description="Estado actual de la cita"
    )
    timezone: str = Field(
        default="America/Mexico_City",
        min_length=3,
        description="Zona horaria utilizada para validar la cita",
    )

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


class CitaCreate(CitaBase):
    """Modelo para crear una cita (sin id)"""

    pass


class CitaUpdate(BaseModel):
    """Modelo para actualizar una cita (todos los campos opcionales)"""

    paciente: Optional[str] = Field(None, min_length=1)
    medico: Optional[str] = Field(None, min_length=1)
    especialidad: Optional[str] = Field(None, min_length=1)
    fecha: Optional[datetime] = None
    motivo: Optional[str] = None
    estado: Optional[Literal["Pendiente", "Completada", "Cancelada"]] = None
    timezone: Optional[str] = Field(default=None, min_length=3)


class CitaResponse(CitaBase):
    """Modelo de respuesta con id incluido"""

    id: int = Field(..., description="ID único de la cita")

    model_config = ConfigDict(from_attributes=True, json_encoders={datetime: lambda v: v.isoformat()})
