from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CitaBase(BaseModel):
    """Modelo base para una cita médica"""
    paciente: str = Field(..., min_length=1, description="Nombre del paciente")
    medico: str = Field(..., min_length=1, description="Nombre del médico")
    fecha: str = Field(..., description="Fecha de la cita en formato ISO")
    motivo: Optional[str] = Field(None, description="Motivo de la consulta")


class CitaCreate(CitaBase):
    """Modelo para crear una cita (sin id)"""
    pass


class CitaUpdate(BaseModel):
    """Modelo para actualizar una cita (todos los campos opcionales)"""
    paciente: Optional[str] = Field(None, min_length=1)
    medico: Optional[str] = Field(None, min_length=1)
    fecha: Optional[str] = None
    motivo: Optional[str] = None


class CitaResponse(CitaBase):
    """Modelo de respuesta con id incluido"""
    id: int = Field(..., description="ID único de la cita")

    class Config:
        from_attributes = True