import numpy as np
import pandas as pd
from typing import List
from backend.models.models import MachineMetric

def compute_deviations(metrics: List[MachineMetric]):
    """
    Computes deviations of the most recent metric against the historical baseline.
    Returns a dictionary of deviations as percentages and raw baseline values.
    """
    if not metrics:
        return {}
        
    df = pd.DataFrame([{
        "temperature": m.temperature,
        "vibration": m.vibration,
        "rpm": m.rpm,
        "energy": m.energy_consumption,
        "downtime": m.downtime_minutes
    } for m in metrics])
    
    # Baseline is mean of all history
    baseline = df.mean()
    
    # Latest reading
    latest = df.iloc[0] # assuming sorted desc
    
    deviations = {}
    for col in ["temperature", "vibration", "rpm", "energy"]:
        if baseline[col] > 0:
            dev = ((latest[col] - baseline[col]) / baseline[col]) * 100
        else:
            dev = 0
        deviations[col] = {
            "latest": round(latest[col], 2),
            "baseline": round(baseline[col], 2),
            "deviation_pct": round(dev, 2)
        }
        
    # Downtime trend
    recent_downtime = df.head(7)['downtime'].sum()
    past_downtime = df.iloc[7:14]['downtime'].sum() if len(df) > 14 else recent_downtime
    if past_downtime > 0:
        dt_dev = ((recent_downtime - past_downtime) / past_downtime) * 100
    else:
        dt_dev = 100 if recent_downtime > 0 else 0
        
    deviations["downtime"] = {
        "recent_7d": float(recent_downtime),
        "prev_7d": float(past_downtime),
        "deviation_pct": round(dt_dev, 2)
    }
    
    return deviations
