from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.dependencies import get_db
from backend.services.production_service import ProductionService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("")
def get_dashboard_data(db: Session = Depends(get_db)):
    service = ProductionService(db)
    return service.get_full_dashboard_stats()
