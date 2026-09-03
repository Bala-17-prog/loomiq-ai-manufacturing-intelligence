import cv2
import numpy as np
import os

def create_fabric_base(width, height):
    base = np.ones((height, width), dtype=np.uint8) * 200
    noise = np.random.normal(0, 15, (height, width)).astype(np.int16)
    base = np.clip(base + noise, 0, 255).astype(np.uint8)
    
    for i in range(0, width, 4):
        base[:, i] = np.clip(base[:, i].astype(np.int16) - 10, 0, 255).astype(np.uint8)
    for i in range(0, height, 4):
        base[i, :] = np.clip(base[i, :].astype(np.int16) - 10, 0, 255).astype(np.uint8)
    return cv2.cvtColor(base, cv2.COLOR_GRAY2BGR)

def generate_images():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    img_dir = os.path.join(base_dir, "data", "fabric_images")
    normal_dir = os.path.join(img_dir, "normal")
    defect_dir = os.path.join(img_dir, "defective")
    
    os.makedirs(normal_dir, exist_ok=True)
    os.makedirs(defect_dir, exist_ok=True)
    
    w, h = 800, 600
    
    normal = create_fabric_base(w, h)
    cv2.imwrite(os.path.join(normal_dir, "normal_01.jpg"), normal)
    
    stain = create_fabric_base(w, h)
    overlay = stain.copy()
    cv2.circle(overlay, (400, 300), 100, (50, 50, 50), -1)
    overlay = cv2.GaussianBlur(overlay, (81, 81), 0)
    cv2.addWeighted(overlay, 0.7, stain, 0.3, 0, stain)
    cv2.imwrite(os.path.join(defect_dir, "stain_01.jpg"), stain)
    
    texture = create_fabric_base(w, h)
    for _ in range(500):
        x = np.random.randint(250, 550)
        y = np.random.randint(200, 400)
        cv2.circle(texture, (x, y), 2, (255, 255, 255), -1)
        cv2.circle(texture, (x+2, y+2), 2, (50, 50, 50), -1)
    cv2.imwrite(os.path.join(defect_dir, "texture_01.jpg"), texture)
    
    anomaly = create_fabric_base(w, h)
    pts = np.array([[300, 200], [450, 220], [420, 350], [280, 320]], np.int32)
    cv2.fillPoly(anomaly, [pts], (20, 20, 20))
    cv2.imwrite(os.path.join(defect_dir, "anomaly_01.jpg"), anomaly)

    print("Demo images generated successfully.")

if __name__ == "__main__":
    generate_images()
