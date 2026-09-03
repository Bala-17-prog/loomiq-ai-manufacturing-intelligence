from sqlalchemy.orm import Session
from backend.models.models import Production, Defect
from datetime import date
from sqlalchemy import func

class ProductionRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_daily_production(self, target_date: date):
        return self.db.query(Production).filter(Production.date == target_date).all()
        
    def get_total_production_by_date(self, target_date: date):
        result = self.db.query(
            func.sum(Production.actual_quantity).label("total_actual"),
            func.sum(Production.target_quantity).label("total_target")
        ).filter(Production.date == target_date).first()
        return result
        
    def get_recent_defects(self, limit: int = 50):
        return self.db.query(Defect).order_by(Defect.date.desc()).limit(limit).all()
