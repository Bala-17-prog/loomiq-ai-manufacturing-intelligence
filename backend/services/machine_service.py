from sqlalchemy.orm import Session
from backend.repositories.machine_repository import MachineRepository
from backend.ml.machine_health import MachineHealthEngine

class MachineService:
    def __init__(self, db: Session):
        self.repository = MachineRepository(db)
        
    def get_all_machines(self):
        return self.repository.get_all_machines()
        
    def get_machine_details(self, machine_id: str):
        machine = self.repository.get_machine_by_id(machine_id)
        if not machine:
            return None
            
        metrics = self.repository.get_machine_metrics(machine_id, limit=365) # pass historical metrics
        
        engine = MachineHealthEngine()
        health_assessment = engine.evaluate_health(machine_id, metrics)
        
        return {
            "machine_id": machine.machine_id,
            "machine_name": machine.machine_name,
            "department": machine.department,
            "status": machine.status,
            "installation_date": machine.installation_date,
            "health": health_assessment
        }
        
    def get_machine_metrics(self, machine_id: str, limit: int = 100):
        return self.repository.get_machine_metrics(machine_id, limit)
