import os
import sys
import pandas as pd
from datetime import datetime

# Add project root to python path to resolve modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import SessionLocal, engine, Base
from backend.models.models import Machine, MachineMetric, Production, Defect, Maintenance

def main():
    print("Initializing database...")
    base_dir = os.path.dirname(os.path.dirname(__file__))
    generated_dir = os.path.join(base_dir, "data", "generated")
    
    # Check if files exist
    if not os.path.exists(os.path.join(generated_dir, "machines.csv")):
        print("Demo data not found. Run generate_demo_data.py first.")
        return
        
    db = SessionLocal()
    try:
        # Clear existing data safely by dropping all and recreating via Alembic or directly 
        # But we rely on Alembic. For this script, we'll just truncate or delete.
        print("Clearing existing data...")
        db.query(Maintenance).delete()
        db.query(Defect).delete()
        db.query(Production).delete()
        db.query(MachineMetric).delete()
        db.query(Machine).delete()
        db.commit()
        
        # 1. Load Machines
        print("Loading Machines...")
        df_machines = pd.read_csv(os.path.join(generated_dir, "machines.csv"))
        df_machines['installation_date'] = pd.to_datetime(df_machines['installation_date']).dt.date
        machines = df_machines.to_dict(orient="records")
        db.bulk_insert_mappings(Machine, machines)
        db.commit()
        
        # 2. Load Metrics
        print("Loading Metrics...")
        df_metrics = pd.read_csv(os.path.join(generated_dir, "machine_metrics.csv"))
        df_metrics['timestamp'] = pd.to_datetime(df_metrics['timestamp'])
        metrics = df_metrics.to_dict(orient="records")
        db.bulk_insert_mappings(MachineMetric, metrics)
        db.commit()
        
        # 3. Load Production
        print("Loading Production...")
        df_prod = pd.read_csv(os.path.join(generated_dir, "production.csv"))
        df_prod['date'] = pd.to_datetime(df_prod['date']).dt.date
        prods = df_prod.to_dict(orient="records")
        db.bulk_insert_mappings(Production, prods)
        db.commit()
        
        # 4. Load Defects
        print("Loading Defects...")
        if os.path.exists(os.path.join(generated_dir, "defects.csv")):
            df_defects = pd.read_csv(os.path.join(generated_dir, "defects.csv"))
            if not df_defects.empty:
                df_defects['date'] = pd.to_datetime(df_defects['date']).dt.date
                defs = df_defects.to_dict(orient="records")
                db.bulk_insert_mappings(Defect, defs)
                db.commit()
                
        # 5. Load Maintenance
        print("Loading Maintenance...")
        if os.path.exists(os.path.join(generated_dir, "maintenance.csv")):
            df_maint = pd.read_csv(os.path.join(generated_dir, "maintenance.csv"))
            if not df_maint.empty:
                df_maint['date'] = pd.to_datetime(df_maint['date']).dt.date
                maints = df_maint.to_dict(orient="records")
                db.bulk_insert_mappings(Maintenance, maints)
                db.commit()
                
        print("Database initialized successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
