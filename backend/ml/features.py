import numpy as np

from typing import List
from backend.models.models import MachineMetric

def compute_deviations(metrics: List[MachineMetric]):
    """
    Computes deviations of the most recent metric against the historical baseline.
    Returns a dictionary of deviations as percentages and raw baseline values.
    """
    if not metrics:
        return {}
        
    features = []
    downtimes = []
    for m in metrics:
        features.append([m.temperature, m.vibration, m.rpm, m.energy_consumption])
        downtimes.append(m.downtime_minutes)
        
    X = np.array(features)
    baseline_vals = np.mean(X, axis=0)
    latest_vals = X[0]
    
    deviations = {}
    cols = ["temperature", "vibration", "rpm", "energy"]
    for i, col in enumerate(cols):
        b_val = baseline_vals[i]
        l_val = latest_vals[i]
        if b_val > 0:
            dev = ((l_val - b_val) / b_val) * 100
        else:
            dev = 0
        deviations[col] = {
            "latest": round(float(l_val), 2),
            "baseline": round(float(b_val), 2),
            "deviation_pct": round(float(dev), 2)
        }
        
    # Downtime trend
    recent_downtime = sum(downtimes[:7])
    if len(downtimes) > 14:
        past_downtime = sum(downtimes[7:14])
    else:
        past_downtime = recent_downtime
        
    if past_downtime > 0:
        dt_dev = ((recent_downtime - past_downtime) / past_downtime) * 100
    else:
        dt_dev = 100 if recent_downtime > 0 else 0
        
    deviations["downtime"] = {
        "recent_7d": float(recent_downtime),
        "prev_7d": float(past_downtime),
        "deviation_pct": round(float(dt_dev), 2)
    }
    
    return deviations
