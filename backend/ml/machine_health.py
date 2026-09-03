

from backend.ml.features import compute_deviations

class MachineHealthEngine:
    _cache = {}
    
    def __init__(self):
        from sklearn.ensemble import IsolationForest
        self.model = IsolationForest(n_estimators=15, contamination=0.1, random_state=42, n_jobs=1)
        
    def evaluate_health(self, machine_id, metrics):
        if machine_id in self.__class__._cache:
            return self.__class__._cache[machine_id]
            
        if not metrics:
            return {"score": 100, "risk": "LOW", "indicators": []}
            
        import numpy as np
        
        # We need enough data to fit, otherwise default
        if len(metrics) < 10:
            return {"score": 100, "risk": "LOW", "indicators": []}
            
        features = [[m.temperature, m.vibration, m.rpm, m.energy_consumption] for m in metrics]
        X = np.array(features)
        
        # Fit model on the historical data to detect if the latest point is an anomaly
        self.model.fit(X)
        latest_features = X[[0]]
        
        # Anomaly score: negative is anomaly, positive is normal
        anomaly_score_raw = self.model.decision_function(latest_features)[0]
        
        # Calculate transparent health score based on deviations
        deviations = compute_deviations(metrics)
        
        # Base score 100
        score = 100
        indicators = []
        
        # Penalties based on transparent deviations
        if deviations["vibration"]["deviation_pct"] > 15:
            score -= 20
            indicators.append(f"Vibration +{deviations['vibration']['deviation_pct']}% above baseline")
        elif deviations["vibration"]["deviation_pct"] > 5:
            score -= 5
            
        if deviations["temperature"]["deviation_pct"] > 10:
            score -= 15
            indicators.append(f"Temperature +{deviations['temperature']['deviation_pct']}% above baseline")
            
        if deviations["energy"]["deviation_pct"] > 10:
            score -= 10
            indicators.append(f"Energy consumption +{deviations['energy']['deviation_pct']}% above baseline")
            
        if deviations["downtime"]["deviation_pct"] > 20:
            score -= 15
            indicators.append(f"Downtime increased by {deviations['downtime']['deviation_pct']}% vs previous period")
            
        # Ensure score stays in bounds
        score = max(0, min(100, score))
        
        # If isolation forest says strong anomaly, cap score at 49
        if anomaly_score_raw < -0.1 and score > 49:
            score = 48
            indicators.append("Machine learning model detected an abnormal operational pattern")
            
        if score >= 75:
            risk = "LOW"
        elif score >= 50:
            risk = "MEDIUM"
        else:
            risk = "HIGH"
            
        if not indicators and risk == "LOW":
            indicators.append("Machine is operating within normal parameters")
            
        result = {
            "score": score,
            "risk": risk,
            "indicators": indicators,
            "deviations": deviations
        }
        
        self.__class__._cache[machine_id] = result
        return result
