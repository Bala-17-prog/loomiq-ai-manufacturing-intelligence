import requests
import sys

def test_determinism():
    base_url = 'http://localhost:8000/api'
    img_path = r'd:\loomiq-ai-manufacturing-intelligence\data\fabric_images\defective\stain_01.jpg'
    
    results = []
    for i in range(3):
        with open(img_path, 'rb') as f:
            res = requests.post(f'{base_url}/quality/inspect', files={'file': ('stain_01.jpg', f, 'image/jpeg')})
            if res.status_code != 200:
                print(f"Failed on request {i+1}: {res.text}")
                sys.exit(1)
            results.append(res.json())
            
    r1, r2, r3 = results
    
    # Assert deterministic fields
    assert r1['anomaly_score'] == r2['anomaly_score'] == r3['anomaly_score'], "Anomaly scores differ!"
    assert r1['severity'] == r2['severity'] == r3['severity'], "Severities differ!"
    assert r1['result'] == r2['result'] == r3['result'], "Results differ!"
    assert r1['potential_issue'] == r2['potential_issue'] == r3['potential_issue'], "Potential issues differ!"
    assert r1['image_hash'] == r2['image_hash'] == r3['image_hash'], "Image hashes differ!"
    
    d1, d2, d3 = r1['processing_details'], r2['processing_details'], r3['processing_details']
    assert d1['detected_regions'] == d2['detected_regions'] == d3['detected_regions'], "Detected regions differ!"
    assert d1['largest_region_pixels'] == d2['largest_region_pixels'] == d3['largest_region_pixels'], "Largest regions differ!"
    assert d1['mean_anomaly_intensity'] == d2['mean_anomaly_intensity'] == d3['mean_anomaly_intensity'], "Mean anomaly intensities differ!"
    
    print("Determinism test PASSED! All 3 inspections of the same image produced identical results.")
    
if __name__ == '__main__':
    test_determinism()
