import os
import sys

# Add project root to python path to resolve modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import SessionLocal
from backend.models.models import Machine, MachineMetric, Production, Defect

def validate():
    db = SessionLocal()
    print("Running Data Validations...")
    errors = 0
    
    # 1. Valid Machine IDs
    machines = db.query(Machine).all()
    if len(machines) != 20:
        print(f"ERROR: Expected 20 machines, found {len(machines)}")
        errors += 1
    
    # 2. Impossible Negative Production
    neg_prod = db.query(Production).filter(Production.actual_quantity < 0).count()
    if neg_prod > 0:
        print(f"ERROR: Found {neg_prod} records with negative production.")
        errors += 1
        
    # 3. Efficiency within valid bounds (0 to 100)
    invalid_eff = db.query(Production).filter((Production.efficiency < 0) | (Production.efficiency > 100)).count()
    if invalid_eff > 0:
        print(f"ERROR: Found {invalid_eff} records with invalid efficiency.")
        errors += 1
        
    # 4. Valid Shift Names
    valid_shifts = ["Morning", "Afternoon", "Night"]
    invalid_shifts = db.query(Production).filter(~Production.shift.in_(valid_shifts)).count()
    if invalid_shifts > 0:
        print(f"ERROR: Found {invalid_shifts} records with invalid shifts.")
        errors += 1
        
    # 5. Check M-017 Scenario
    m017 = db.query(MachineMetric).filter(MachineMetric.machine_id == "M-017").order_by(MachineMetric.timestamp.asc()).all()
    if len(m017) > 0:
        first_temp = m017[0].temperature
        last_temp = m017[-1].temperature
        if last_temp <= first_temp:
            print("ERROR: M-017 temperature deterioration scenario failed.")
            errors += 1
            
    if errors == 0:
        print("SUCCESS: All validation checks passed.")
        return True
    else:
        print("FAILED: Data validation found errors.")
        return False
        
if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
