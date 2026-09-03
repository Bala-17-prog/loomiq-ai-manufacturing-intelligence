from sqlalchemy.orm import Session
from backend.repositories.production_repository import ProductionRepository
from backend.repositories.machine_repository import MachineRepository
from backend.models.models import Production, MachineMetric, Defect, Machine
from datetime import date, timedelta
from sqlalchemy import func

class ProductionService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ProductionRepository(db)
        self.machine_repo = MachineRepository(db)
        
    def get_full_dashboard_stats(self):
        # Determine "today" as the most recent date in production to always have data
        latest_prod = self.db.query(func.max(Production.date)).scalar()
        if not latest_prod:
            return {}
            
        # 1. KPIs
        prod_stats = self.repository.get_total_production_by_date(latest_prod)
        actual = prod_stats.total_actual or 0
        target = prod_stats.total_target or 0
        achievement = (actual / target * 100) if target > 0 else 0
        
        avg_eff = self.db.query(func.avg(Production.efficiency)).filter(Production.date == latest_prod).scalar() or 0
        
        total_defects = self.db.query(func.sum(Defect.quantity)).filter(Defect.date == latest_prod).scalar() or 0
        defect_rate = (total_defects / actual * 100) if actual > 0 else 0
        
        # Downtime uses metrics table for the latest date
        # Assuming latest date matches
        downtime = self.db.query(func.sum(MachineMetric.downtime_minutes)).filter(
            func.date(MachineMetric.timestamp) == latest_prod
        ).scalar() or 0
        
        total_machines = self.db.query(Machine).count()
        active_machines = self.db.query(Machine).filter(Machine.status == "RUNNING").count()
        
        # 2. Production Trend (last 7 days)
        start_trend = latest_prod - timedelta(days=6)
        trend_data = self.db.query(
            Production.date, 
            func.sum(Production.actual_quantity).label("actual"),
            func.sum(Production.target_quantity).label("target")
        ).filter(Production.date >= start_trend).group_by(Production.date).order_by(Production.date).all()
        
        production_trend = [{"date": str(r.date), "actual": r.actual, "target": r.target} for r in trend_data]
        
        # 3. Machine Health Distribution (Stubbed until ML is built)
        # We will refine this in Phase 11
        health_dist = {"Healthy": 16, "Warning": 3, "Critical": 1}
        
        # 4. Recent Alerts (Stubbed)
        alerts = [
            {"id": 1, "machine": "M-017", "level": "critical", "message": "High vibration detected"},
            {"id": 2, "machine": "M-012", "level": "warning", "message": "Temperature above normal"},
            {"id": 3, "machine": "M-005", "level": "info", "message": "Scheduled maintenance approaching"}
        ]
        
        return {
            "date": str(latest_prod),
            "kpis": {
                "production": actual,
                "target": target,
                "achievement": round(achievement, 1),
                "efficiency": round(avg_eff, 1),
                "defect_rate": round(defect_rate, 2),
                "downtime_minutes": int(downtime),
                "active_machines": f"{active_machines} / {total_machines}",
                "machines_attention": 3 # stubbed
            },
            "production_trend": production_trend,
            "health_distribution": health_dist,
            "recent_alerts": alerts
        }

    def _build_filter(self, query, start_date, end_date, machine_id=None, shift=None, fabric_type=None, department=None):
        if start_date: query = query.filter(Production.date >= start_date)
        if end_date: query = query.filter(Production.date <= end_date)
        if machine_id: query = query.filter(Production.machine_id == machine_id)
        if shift: query = query.filter(Production.shift == shift)
        if fabric_type: query = query.filter(Production.fabric_type == fabric_type)
        if department: 
            query = query.join(Machine).filter(Machine.department == department)
        return query

    def get_filtered_production(self, start_date, end_date, machine_id, shift, fabric_type, department):
        # 1. Base Query
        query = self.db.query(
            func.sum(Production.actual_quantity).label("actual"),
            func.sum(Production.target_quantity).label("target"),
            func.avg(Production.efficiency).label("efficiency")
        )
        query = self._build_filter(query, start_date, end_date, machine_id, shift, fabric_type, department)
        stats = query.first()
        
        actual = stats.actual or 0
        target = stats.target or 0
        eff = stats.efficiency or 0
        achievement = (actual / target * 100) if target > 0 else 0
        
        return {
            "production_quantity": actual,
            "target_quantity": target,
            "achievement": round(achievement, 1),
            "efficiency": round(eff, 1)
        }

    def get_trends(self, start_date, end_date, machine_id):
        query = self.db.query(
            Production.date,
            func.sum(Production.actual_quantity).label("actual"),
            func.sum(Production.target_quantity).label("target"),
            func.avg(Production.efficiency).label("efficiency")
        )
        query = self._build_filter(query, start_date, end_date, machine_id)
        results = query.group_by(Production.date).order_by(Production.date).all()
        
        return [{"date": str(r.date), "actual": r.actual, "target": r.target, "efficiency": round(r.efficiency, 1)} for r in results]

    def get_aggregated_by(self, field, start_date, end_date):
        field_attr = getattr(Production, field)
        query = self.db.query(
            field_attr.label("category"),
            func.sum(Production.actual_quantity).label("actual"),
            func.sum(Production.target_quantity).label("target")
        )
        query = self._build_filter(query, start_date, end_date)
        results = query.group_by(field_attr).all()
        
        return [{"category": str(r.category), "actual": r.actual, "target": r.target} for r in results]
