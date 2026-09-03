from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.dependencies import get_db
from backend.models.models import Production, Defect
from datetime import date

router = APIRouter(prefix="/api/simulator", tags=["What-If Simulator"])

class SimulationParams(BaseModel):
    speed_multiplier: float  # e.g. 1.0 = no change, 1.1 = +10% speed
    downtime_reduction: float # e.g. 0.0 = no change, 0.2 = -20% downtime
    defect_rate_change: float # e.g. 0.0 = no change, -0.05 = -5% defects

@router.post("/simulate")
def run_simulation(params: SimulationParams, db: Session = Depends(get_db)):
    """
    Simulates production outcomes based on parameter changes applied to the latest day's baseline data.
    """
    # Get baseline data (latest day)
    latest_prod = db.query(func.max(Production.date)).scalar()
    if not latest_prod:
        return {"error": "No baseline data available."}
        
    baseline_stats = db.query(
        func.sum(Production.actual_quantity).label("actual"),
        func.sum(Production.target_quantity).label("target")
    ).filter(Production.date == latest_prod).first()
    
    baseline_defects = db.query(func.sum(Defect.quantity)).filter(Defect.date == latest_prod).scalar() or 0
    
    base_actual = float(baseline_stats.actual or 0)
    base_target = float(baseline_stats.target or 0)
    
    # 1. Simulate Production Quantity
    # Speed directly increases actual quantity. Downtime reduction increases time available, hence quantity.
    # Formula: New Actual = Base Actual * Speed Multiplier * (1 + Downtime Reduction)
    simulated_actual = base_actual * params.speed_multiplier * (1 + params.downtime_reduction)
    
    # 2. Simulate Defects
    # Base defect rate
    base_defect_rate = (baseline_defects / base_actual) if base_actual > 0 else 0
    simulated_defect_rate = max(0, base_defect_rate + params.defect_rate_change)
    simulated_defects = simulated_actual * simulated_defect_rate
    
    # 3. Simulate Financial Impact (Mock value: $5 profit per good unit produced)
    base_good_units = base_actual - baseline_defects
    simulated_good_units = simulated_actual - simulated_defects
    
    revenue_per_unit = 5.0
    base_revenue = base_good_units * revenue_per_unit
    simulated_revenue = simulated_good_units * revenue_per_unit
    revenue_impact = simulated_revenue - base_revenue
    
    return {
        "baseline": {
            "production": round(base_actual),
            "defects": round(baseline_defects),
            "good_units": round(base_good_units),
            "revenue": round(base_revenue, 2)
        },
        "simulated": {
            "production": round(simulated_actual),
            "defects": round(simulated_defects),
            "good_units": round(simulated_good_units),
            "revenue": round(simulated_revenue, 2)
        },
        "impact": {
            "production_change": round(simulated_actual - base_actual),
            "revenue_change": round(revenue_impact, 2),
            "percentage_change": round((revenue_impact / base_revenue) * 100, 2) if base_revenue > 0 else 0
        }
    }
