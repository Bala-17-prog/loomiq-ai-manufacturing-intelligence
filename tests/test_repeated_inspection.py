from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_repeated_inspection():

    img_path = r'd:\loomiq-ai-manufacturing-intelligence\data\fabric_images\defective\anomaly_01.jpg'
    
    results = []
    print("Running 10 repeated inspections on the same image...")
    
    for i in range(10):
        with open(img_path, 'rb') as f:
            res = client.post('/api/quality/inspect', files={'file': ('anomaly_01.jpg', f, 'image/jpeg')}).json()
            results.append(res)
            print(f"Run {i+1} -> Score: {res['anomaly_score']}, Severity: {res['severity']}, Result: {res['result']}, Issue: {res['potential_issue']}, Hash: {res['image_hash'][:8]}..., Processing Time: {res['processing_details']['processing_time_ms']}ms")
            
    reference = results[0]
    
    for i, res in enumerate(results[1:], start=2):
        assert res['anomaly_score'] == reference['anomaly_score'], f"Run {i} failed: anomaly_score changed"
        assert res['severity'] == reference['severity'], f"Run {i} failed: severity changed"
        assert res['result'] == reference['result'], f"Run {i} failed: result changed"
        assert res['potential_issue'] == reference['potential_issue'], f"Run {i} failed: potential_issue changed"
        assert res['image_hash'] == reference['image_hash'], f"Run {i} failed: image_hash changed"
        assert res['detection_strength'] == reference['detection_strength'], f"Run {i} failed: detection_strength changed"
        assert res['processing_details']['detected_regions'] == reference['processing_details']['detected_regions'], f"Run {i} failed: detected_regions changed"
        assert res['processing_details']['largest_region_pixels'] == reference['processing_details']['largest_region_pixels'], f"Run {i} failed: largest_region_pixels changed"
        assert res['processing_details']['mean_anomaly_intensity'] == reference['processing_details']['mean_anomaly_intensity'], f"Run {i} failed: mean_anomaly_intensity changed"
        
    print("\nSUCCESS! All 10 runs produced identical analytical metrics.")

if __name__ == '__main__':
    test_repeated_inspection()
