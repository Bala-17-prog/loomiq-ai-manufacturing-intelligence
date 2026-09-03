from sqlalchemy.orm import Session
from backend.models.models import Machine, MachineMetric

class MachineRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_all_machines(self):
        return self.db.query(Machine).all()
        
    def get_machine_by_id(self, machine_id: str):
        return self.db.query(Machine).filter(Machine.machine_id == machine_id).first()
        
    def get_machine_metrics(self, machine_id: str, limit: int = 100):
        return self.db.query(MachineMetric).filter(
            MachineMetric.machine_id == machine_id
        ).order_by(MachineMetric.timestamp.desc()).limit(limit).all()
