from typing import List, Optional, Dict
from models import CitaCreate, CitaUpdate, CitaResponse


class CitasRepository:
    """Repositorio en memoria para gestionar citas"""
    
    def __init__(self):
        self.citas: Dict[int, dict] = {}
        self.next_id: int = 1
    
    def create(self, cita: CitaCreate) -> CitaResponse:
        """Crear una nueva cita"""
        cita_dict = cita.model_dump()
        cita_dict['id'] = self.next_id
        
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
        
        # Obtener la cita actual
        cita_actual = self.citas[cita_id]
        
        # Actualizar solo los campos que vienen en el request
        update_data = cita_update.model_dump(exclude_unset=True)
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