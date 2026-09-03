from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from backend.dependencies import get_db
from backend.services.production_service import ProductionService

router = APIRouter(prefix="/api/production", tags=["Production"])

@router.get("")
def get_production_overview(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    machine_id: Optional[str] = None,
    shift: Optional[str] = None,
    fabric_type: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    service = ProductionService(db)
    return service.get_filtered_production(start_date, end_date, machine_id, shift, fabric_type, department)

@router.get("/trends")
def get_production_trends(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    machine_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    service = ProductionService(db)
    return service.get_trends(start_date, end_date, machine_id)

@router.get("/by-machine")
def get_production_by_machine(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    service = ProductionService(db)
    return service.get_aggregated_by("machine_id", start_date, end_date)

@router.get("/by-shift")
def get_production_by_shift(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    service = ProductionService(db)
    return service.get_aggregated_by("shift", start_date, end_date)

@router.get("/by-fabric")
def get_production_by_fabric(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    service = ProductionService(db)
    return service.get_aggregated_by("fabric_type", start_date, end_date)
