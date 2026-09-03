import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def main():
    print("Generating demo data...")
    np.random.seed(42)
    
    # 1. Setup paths
    base_dir = os.path.dirname(os.path.dirname(__file__))
    generated_dir = os.path.join(base_dir, "data", "generated")
    os.makedirs(generated_dir, exist_ok=True)
    
    # 2. Base Configuration
    days = 365
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days - 1)
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    
    departments = ["Spinning", "Weaving", "Processing", "Finishing"]
    machine_types = {"Spinning": "Spinner", "Weaving": "Loom", "Processing": "Dyer", "Finishing": "Finisher"}
    fabric_types = ["Cotton", "Polyester", "Silk", "Wool", "Blend"]
    shifts = ["Morning", "Afternoon", "Night"]
    defect_categories = ["Stain", "Hole", "Broken Yarn", "Irregular Texture", "Surface Anomaly"]
    
    # 3. Generate Machines
    machines = []
    for i in range(1, 21):
        machine_id = f"M-{i:03d}"
        dept = np.random.choice(departments)
        if machine_id == "M-017":
            dept = "Weaving" # Pin M-017 to Weaving for predictability
        
        machines.append({
            "machine_id": machine_id,
            "machine_name": f"{machine_types[dept]} {i:02d}",
            "department": dept,
            "machine_type": machine_types[dept],
            "installation_date": start_date - timedelta(days=np.random.randint(100, 1000)),
            "status": "RUNNING"
        })
    df_machines = pd.DataFrame(machines)
    df_machines.to_csv(os.path.join(generated_dir, "machines.csv"), index=False)
    
    # 4. Generate Production & Metrics
    production_records = []
    metrics_records = []
    defects_records = []
    maintenance_records = []
    
    # Base params for machines
    machine_baselines = {}
    for m in machines:
        machine_baselines[m["machine_id"]] = {
            "temp": np.random.uniform(65, 75),
            "vib": np.random.uniform(5, 12),
            "rpm": np.random.uniform(900, 1100),
            "energy": np.random.uniform(40, 60),
            "running_hours": 0
        }
    
    for day_idx, current_date in enumerate(date_range):
        progress_ratio = day_idx / days # 0.0 to 1.0
        
        for m in machines:
            mid = m["machine_id"]
            base = machine_baselines[mid]
            base["running_hours"] += 24 # Accumulate running hours roughly
            
            # M-017 Degradation Logic
            is_m017 = (mid == "M-017")
            if is_m017:
                # Progressively worse
                temp_mean = base["temp"] + (progress_ratio * 25) # Up to +25 deg
                vib_mean = base["vib"] + (progress_ratio * 15) # Up to +15 mm/s
                rpm_mean = base["rpm"] - (progress_ratio * 150) # Drops
                energy_mean = base["energy"] + (progress_ratio * 20) # Increases
                efficiency_drop = progress_ratio * 0.25 # Drops by 25%
                downtime_prob = 0.05 + (progress_ratio * 0.3)
            else:
                temp_mean = base["temp"]
                vib_mean = base["vib"]
                rpm_mean = base["rpm"]
                energy_mean = base["energy"]
                efficiency_drop = 0
                downtime_prob = 0.05
            
            # Daily Metric (simplified to 1 per day for demo, could be per shift)
            downtime = 0
            if np.random.random() < downtime_prob:
                downtime = np.random.randint(30, 240)
                if is_m017: downtime += int(progress_ratio * 120)
                
            metrics_records.append({
                "machine_id": mid,
                "timestamp": datetime.combine(current_date, datetime.min.time()) + timedelta(hours=12), # noon
                "temperature": max(0, np.random.normal(temp_mean, 2)),
                "vibration": max(0, np.random.normal(vib_mean, 1)),
                "rpm": max(0, np.random.normal(rpm_mean, 20)),
                "energy_consumption": max(0, np.random.normal(energy_mean, 5)),
                "running_hours": base["running_hours"],
                "downtime_minutes": downtime
            })
            
            # Maintenance
            if downtime > 120 and np.random.random() < 0.3:
                maintenance_records.append({
                    "machine_id": mid,
                    "date": current_date,
                    "maintenance_type": "Corrective",
                    "downtime_minutes": downtime,
                    "notes": "High downtime reported, performed maintenance."
                })
            elif day_idx > 0 and day_idx % 90 == 0: # Scheduled
                maintenance_records.append({
                    "machine_id": mid,
                    "date": current_date,
                    "maintenance_type": "Scheduled",
                    "downtime_minutes": 180,
                    "notes": "Quarterly preventative maintenance."
                })
                
            # Production (per shift)
            daily_defects = 0
            for shift in shifts:
                fabric = np.random.choice(fabric_types)
                target = np.random.randint(400, 600)
                
                # Base efficiency 85-98%
                eff = np.random.uniform(0.85, 0.98) - efficiency_drop
                
                # High vibration/temp -> lower efficiency
                if metrics_records[-1]["vibration"] > 20: eff -= 0.05
                if metrics_records[-1]["temperature"] > 85: eff -= 0.05
                
                # Shift penalty
                if shift == "Night": eff -= 0.02
                
                # Downtime penalty
                eff -= (downtime / 1440) 
                
                eff = max(0.1, min(1.0, eff))
                actual = int(target * eff)
                
                production_records.append({
                    "date": current_date,
                    "machine_id": mid,
                    "shift": shift,
                    "fabric_type": fabric,
                    "target_quantity": target,
                    "actual_quantity": actual,
                    "efficiency": round(eff * 100, 2)
                })
                
                # Defects based on efficiency & M-017
                defect_prob = 1.0 - eff
                if np.random.random() < defect_prob:
                    qty = np.random.randint(1, max(2, int(actual * 0.05)))
                    daily_defects += qty
                    defects_records.append({
                        "date": current_date,
                        "machine_id": mid,
                        "fabric_type": fabric,
                        "defect_type": np.random.choice(defect_categories),
                        "severity": np.random.choice(["LOW", "MEDIUM", "HIGH"], p=[0.6, 0.3, 0.1]),
                        "quantity": qty
                    })

    pd.DataFrame(metrics_records).to_csv(os.path.join(generated_dir, "machine_metrics.csv"), index=False)
    pd.DataFrame(production_records).to_csv(os.path.join(generated_dir, "production.csv"), index=False)
    pd.DataFrame(defects_records).to_csv(os.path.join(generated_dir, "defects.csv"), index=False)
    pd.DataFrame(maintenance_records).to_csv(os.path.join(generated_dir, "maintenance.csv"), index=False)
    
    print("Demo data generated successfully.")

if __name__ == "__main__":
    main()
