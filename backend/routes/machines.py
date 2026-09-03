from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.dependencies import get_db
from backend.services.machine_service import MachineService

router = APIRouter(prefix="/api/machines", tags=["Machines"])

@router.get("")
def get_all_machines(db: Session = Depends(get_db)):
    service = MachineService(db)
    machines = service.get_all_machines()
    return machines

@router.get("/{machine_id}")
def get_machine(machine_id: str, db: Session = Depends(get_db)):
    service = MachineService(db)
    machine = service.get_machine_details(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.get("/{machine_id}/metrics")
def get_machine_metrics(machine_id: str, limit: int = 30, db: Session = Depends(get_db)):
    service = MachineService(db)
    metrics = service.get_machine_metrics(machine_id, limit)
    return metrics
