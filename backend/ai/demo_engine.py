from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from backend.models.models import MachineMetric, Machine, QualityInspection, Production, Defect
from backend.services.machine_service import MachineService
from backend.services.production_service import ProductionService
from typing import Dict, Any, Optional

class DemoEngine:
    def __init__(self, db: Session):
        self.db = db
        self.machine_service = MachineService(db)
        self.production_service = ProductionService(db)

    def get_highest_downtime(self) -> Dict[str, Any]:
        """
        Calculates the machine with the highest downtime in the last recorded period 
        using actual data from MachineMetric.
        """
        # Group by machine_id and sum downtime_minutes
        result = self.db.query(
            MachineMetric.machine_id,
            func.sum(MachineMetric.downtime_minutes).label('total_downtime')
        ).group_by(MachineMetric.machine_id).order_by(desc('total_downtime')).first()

        if not result:
            return {"error": "No machine downtime data available."}
            
        machine_id, total_minutes = result
        hours = round(total_minutes / 60, 1)

        return {
            "intent": "highest_downtime",
            "machine_id": machine_id,
            "downtime_hours": hours,
            "downtime_minutes": total_minutes,
            "source": "database"
        }

    def get_machine_risk(self) -> Dict[str, Any]:
        """
        Uses MachineService/MachineHealthEngine to find the machine needing the most attention
        (lowest health score / highest risk).
        """
        machines = self.machine_service.get_all_machines()
        if not machines:
            return {"error": "No machines found."}

        worst_machine = None
        worst_score = 101

        for m in machines:
            details = self.machine_service.get_machine_details(m.machine_id)
            if not details:
                continue
            health = details.get("health", {})
            score = health.get("score", 100)
            
            if score < worst_score:
                worst_score = score
                worst_machine = details

        if not worst_machine:
            return {"error": "Could not calculate machine risk."}

        health = worst_machine["health"]
        factors = []
        for key, val in health.get("deviations", {}).items():
            if isinstance(val, dict) and "deviation_pct" in val:
                factors.append({
                    "metric": key,
                    "deviation_percent": round(val["deviation_pct"], 2)
                })

        return {
            "intent": "machine_risk",
            "machine_id": worst_machine["machine_id"],
            "machine_name": worst_machine["machine_name"],
            "health_score": health["score"],
            "risk_level": health["risk"],
            "factors": factors,
            "indicators": health.get("indicators", []),
            "source": "machine_health_engine"
        }

    def get_production_summary(self) -> Dict[str, Any]:
        """
        Gets the total production summary for the dashboard.
        """
        stats = self.production_service.get_full_dashboard_stats()
        if not stats or "kpis" not in stats:
            return {"error": "No production data available."}

        kpis = stats["kpis"]
        return {
            "intent": "production_summary",
            "date": stats.get("date"),
            "production_quantity": kpis.get("production", 0),
            "target_quantity": kpis.get("target", 0),
            "achievement_percent": kpis.get("achievement", 0),
            "efficiency_percent": kpis.get("efficiency", 0),
            "source": "production_service"
        }

    def get_defect_rate(self) -> Dict[str, Any]:
        """
        Calculates the PRODUCTION defect rate using the Production table.
        Defect Rate = (defect_units / actual_production) * 100
        """
        prod_result = self.db.query(func.sum(Production.actual_quantity)).scalar()
        defect_result = self.db.query(func.sum(Defect.quantity)).scalar()

        total_prod = prod_result or 0
        total_defect = defect_result or 0
        
        if total_prod == 0:
            return {"error": "No production defect data available."}

        defect_rate = round((total_defect / total_prod) * 100, 2)

        return {
            "intent": "defect_rate",
            "metric_name": "Production Defect Rate",
            "total_production_units": total_prod,
            "defective_units": total_defect,
            "defect_rate_percent": defect_rate,
            "source": "database"
        }

    def get_visual_inspection_review_rate(self) -> Dict[str, Any]:
        """
        Calculates the Visual Inspection Review Rate using the QualityInspection table.
        Review Rate = (REVIEW / Total Inspections) * 100
        """
        total = self.db.query(func.count(QualityInspection.id)).scalar()
        if total == 0:
            return {"error": "No visual inspection data available."}

        reviewed = self.db.query(func.count(QualityInspection.id)).filter(QualityInspection.result == "REVIEW").scalar()
        passed = self.db.query(func.count(QualityInspection.id)).filter(QualityInspection.result == "PASS").scalar()
        
        review_rate = round((reviewed / total) * 100, 2)

        return {
            "intent": "visual_inspection",
            "metric_name": "Visual Inspection Review Rate",
            "total_inspections": total,
            "inspections_passed": passed,
            "inspections_require_review": reviewed,
            "review_rate_percent": review_rate,
            "source": "opencv_pipeline"
        }
