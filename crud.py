from datetime import datetime
from typing import Dict, List, Optional

from models import CitaCreate, CitaResponse, CitaUpdate


class CitasRepository:
    """Repositorio en memoria para gestionar citas"""

    def __init__(self):
        self.citas: Dict[int, dict] = {}
        self.next_id: int = 1

    def _serialize_fecha(self, fecha: datetime | str) -> str:
        if isinstance(fecha, datetime):
            return fecha.isoformat()
        return fecha

    def create(self, cita: CitaCreate) -> CitaResponse:
        """Crear una nueva cita"""
        cita_dict = cita.model_dump()
        cita_dict["id"] = self.next_id
        cita_dict["fecha"] = self._serialize_fecha(cita_dict["fecha"])

        self.citas[self.next_id] = cita_dict
        self.next_id += 1

        return CitaResponse(**cita_dict)

    def get_all(self) -> List[CitaResponse]:
        """Obtener todas las citas"""
        return [CitaResponse(**cita) for cita in self.citas.values()]

    def get_by_id(self, cita_id: int) -> Optional[CitaResponse]:
        """Obtener una cita por ID"""
        cita = self.citas.get(cita_id)
        if cita:
            return CitaResponse(**cita)
        return None

    def update(self, cita_id: int, cita_update: CitaUpdate) -> Optional[CitaResponse]:
        """Actualizar una cita existente"""
        if cita_id not in self.citas:
            return None

        cita_actual = self.citas[cita_id]
        update_data = cita_update.model_dump(exclude_unset=True)

        if "fecha" in update_data:
            update_data["fecha"] = self._serialize_fecha(update_data["fecha"])

        cita_actual.update(update_data)
        self.citas[cita_id] = cita_actual
        return CitaResponse(**cita_actual)

    def delete(self, cita_id: int) -> bool:
        """Eliminar una cita"""
        if cita_id in self.citas:
            del self.citas[cita_id]
            return True
        return False

    def clear(self):
        """Limpiar todas las citas (útil para testing)"""
        self.citas.clear()
        self.next_id = 1


# Instancia global del repositorio
citas_repo = CitasRepository()
