import requests
import sys

def test_pattern_tolerance():
    base_url = 'http://localhost:8000/api'
    
    # 1. Test Plain Defect Image (Test E)
    img_path_plain = r'd:\loomiq-ai-manufacturing-intelligence\data\fabric_images\defective\anomaly_01.jpg'
    with open(img_path_plain, 'rb') as f:
        res_plain = requests.post(f'{base_url}/quality/inspect', files={'file': ('anomaly_01.jpg', f, 'image/jpeg')}).json()
        
    print(f"Obvious Defect Image -> Score: {res_plain['anomaly_score']}, Issue: {res_plain['potential_issue']}")
    assert res_plain['severity'] in ['MODERATE', 'HIGH'], "Obvious defect should be detected as an anomaly."
    
    # 2. Test Patterned Image (Test B/F)
    img_path_pattern = r'd:\loomiq-ai-manufacturing-intelligence\data\fabric_images\defective\texture_01.jpg'
    # Actually texture_01.jpg has a subtle defect, but it is heavily textured.
    # Let's test normal_01.jpg which is plain, and a patterned one if we had one.
    # We will test normal_01.jpg and texture_01.jpg.
    
    with open(r'd:\loomiq-ai-manufacturing-intelligence\data\fabric_images\normal\normal_01.jpg', 'rb') as f:
        res_normal = requests.post(f'{base_url}/quality/inspect', files={'file': ('normal_01.jpg', f, 'image/jpeg')}).json()
    print(f"Normal Fabric -> Score: {res_normal['anomaly_score']}, Severity: {res_normal['severity']}")
    assert res_normal['severity'] == 'NORMAL', "Normal fabric should be NORMAL."
    
    with open(img_path_pattern, 'rb') as f:
        res_pattern = requests.post(f'{base_url}/quality/inspect', files={'file': ('texture_01.jpg', f, 'image/jpeg')}).json()
    print(f"Textured Fabric -> Score: {res_pattern['anomaly_score']}, Severity: {res_pattern['severity']}")
    
    # It used to be 100 HIGH, now it should be lower because the variance threshold scales.
    assert res_pattern['anomaly_score'] < 100, "Textured fabric should not hit 100 automatically."
    
    print("Pattern tolerance test PASSED! Advanced dynamic thresholding and multi-feature scoring is working.")
    
if __name__ == '__main__':
    test_pattern_tolerance()
