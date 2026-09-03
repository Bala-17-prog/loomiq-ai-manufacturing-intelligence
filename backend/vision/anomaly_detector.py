import cv2
import numpy as np
import os
import uuid
import time
from datetime import datetime

class PrototypeVisualAnomalyDetector:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.raw_dir = os.path.join(base_dir, "raw")
        self.processed_dir = os.path.join(base_dir, "processed")
        
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
    def process_image(self, file_bytes: bytes, filename: str):
        start_time = time.time()
        
        # 1. Validation & Loading
        np_arr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Invalid image file. Could not decode.")
            
        h, w = img.shape[:2]
        if max(h, w) > 6000:
            raise ValueError("Image dimensions exceed the supported limit (6000x6000).")
            
        inspection_id = f"INS-{uuid.uuid4().hex[:8].upper()}"
        ext = filename.split('.')[-1] if '.' in filename else 'jpg'
        
        raw_filename = f"{inspection_id}_raw.{ext}"
        processed_filename = f"{inspection_id}_processed.jpg"
        
        raw_path = os.path.join(self.raw_dir, raw_filename)
        processed_path = os.path.join(self.processed_dir, processed_filename)
        
        cv2.imwrite(raw_path, img)
        
        # 2. Resize for consistent processing
        max_dim = 1200
        orig_h, orig_w = h, w
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)))
            
        original_resized = img.copy()
        overlay = original_resized.copy()
            
        # 3. Preprocessing (Grayscale & Blur)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Calculate global variance
        global_mean, global_stddev = cv2.meanStdDev(gray)
        global_mean = global_mean[0][0]
        global_std = global_stddev[0][0]
        
        # 4. Pattern-Aware Anomaly Detection
        # Use median blur to estimate background robustly without spreading noise
        bg = cv2.medianBlur(gray, 71)
        diff = cv2.absdiff(gray, bg)
        
        # Use Otsu's dynamic thresholding to find the optimal cut-off
        # Otsu requires an 8-bit single-channel image, which 'diff' is.
        _, thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # 5. Contour detection
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter tiny contours dynamically based on image variance
        min_area = 100 + (global_std * 3)
        valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
        
        anomaly_score = 0
        potential_issue = "None"
        severity = "NORMAL"
        result = "PASS"
        detection_signal_strength = 0.0
        largest_region_area = 0.0
        mean_anomaly_intensity = 0.0
        
        # 6. Metric Calculation & Heuristic Rules
        if valid_contours:
            valid_contours = sorted(valid_contours, key=cv2.contourArea, reverse=True)
            c = valid_contours[0]
            largest_region_area = cv2.contourArea(c)
            
            mask = np.zeros_like(gray)
            cv2.drawContours(mask, [c], -1, 255, -1)
            
            # Mean intensity of the anomalous region in the original grayscale image
            region_mean = cv2.mean(gray, mask=mask)[0]
            
            # Mean absolute difference in the diff image (contrast magnitude)
            mean_anomaly_intensity = cv2.mean(diff, mask=mask)[0]
            
            total_img_area = img.shape[0] * img.shape[1]
            relative_size_pct = (largest_region_area / total_img_area) * 100
            
            # Feature 1: Area Score (0-40 points) - 1% of image size is huge
            area_score = min(40, (relative_size_pct / 1.0) * 40)
            
            # Feature 2: Intensity Deviation Score (0-40 points)
            intensity_deviation = abs(region_mean - global_mean)
            
            # Feature 3: Local Contrast Magnitude (0-20 points)
            contrast_score = min(20, (mean_anomaly_intensity / 80) * 20)
            
            # PATTERN TOLERANCE LOGIC (Continuous Scaling):
            # The higher the background noise/pattern (global_std), the harder it is to distinguish a defect.
            # Instead of a hard cliff edge, we calculate a tolerance factor (0.0 to 1.0).
            # If intensity deviation is heavily masked by global variance, reduce scores.
            tolerance_ratio = intensity_deviation / (global_std + 1e-5)
            
            # If the deviation is less than 2x the standard deviation, it's very likely just the pattern.
            if tolerance_ratio < 2.0:
                # Scale smoothly down to 0.1 as the ratio approaches 0
                scaling_factor = max(0.1, (tolerance_ratio / 2.0))
                area_score *= scaling_factor
                contrast_score *= scaling_factor
                
            intensity_score = min(40, (intensity_deviation / 80) * 40)
            
            anomaly_score = int(area_score + intensity_score + contrast_score)
            
            # Mapping rule
            if anomaly_score < 25:
                severity = "NORMAL"
                result = "PASS"
            elif anomaly_score < 50:
                severity = "LOW"
                result = "REVIEW"
            elif anomaly_score < 75:
                severity = "MODERATE"
                result = "REVIEW"
            else:
                severity = "HIGH"
                result = "REVIEW"
                
            x, y, w_box, h_box = cv2.boundingRect(c)
            aspect_ratio = float(w_box) / h_box if h_box > 0 else 1
            
            if anomaly_score >= 25:
                # Conservative defect classification
                if anomaly_score > 75 and intensity_deviation > 80 and region_mean < 50:
                    potential_issue = "Possible Hole"
                elif intensity_deviation > 50 and region_mean < global_mean:
                    potential_issue = "Possible Defect"
                else:
                    potential_issue = "Surface Anomaly"
                    
                # Signal Strength (Signal to Noise Ratio approximation)
                signal_to_noise = mean_anomaly_intensity / (global_std + 1)
                detection_signal_strength = min(99.0, max(50.0, 50 + (signal_to_noise * 10)))
                
                # Visual Annotations
                cv2.rectangle(overlay, (x, y), (x + w_box, y + h_box), (0, 0, 255), -1)
                alpha = 0.3
                cv2.addWeighted(overlay, alpha, original_resized, 1 - alpha, 0, original_resized)
                cv2.rectangle(original_resized, (x, y), (x + w_box, y + h_box), (0, 0, 255), 3)
                
                label = f"{severity} ANOMALY: {potential_issue}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.7
                thickness = 2
                (tw, th), _ = cv2.getTextSize(label, font, font_scale, thickness)
                
                text_y = y - 10 if y - 10 > 20 else y + h_box + 25
                cv2.rectangle(original_resized, (x, text_y - th - 5), (x + tw + 10, text_y + 5), (0, 0, 255), -1)
                cv2.putText(original_resized, label, (x + 5, text_y), font, font_scale, (255, 255, 255), thickness)
            else:
                anomaly_score = max(0, anomaly_score)
                detection_signal_strength = 0.0
                valid_contours = [] # Supress drawing box
                severity = "NORMAL"
        else:
            anomaly_score = 0
            detection_signal_strength = 0.0
            
        if severity == "NORMAL":
            cv2.putText(original_resized, "NO SIGNIFICANT ANOMALY DETECTED", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
        cv2.imwrite(processed_path, original_resized)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        import hashlib
        image_hash = hashlib.sha256(file_bytes).hexdigest()
        
        return {
            "inspection_id": inspection_id,
            "image_hash": image_hash,
            "result": result,
            "anomaly_score": anomaly_score,
            "severity": severity,
            "potential_issue": potential_issue if result == "REVIEW" else "None",
            "detection_strength": round(detection_signal_strength, 1),
            "original_image_url": f"/images/raw/{raw_filename}",
            "processed_image_url": f"/images/processed/{processed_filename}",
            "processing_details": {
                "image_width": orig_w,
                "image_height": orig_h,
                "processing_time_ms": processing_time_ms,
                "detected_regions": len(valid_contours),
                "largest_region_pixels": int(largest_region_area),
                "mean_anomaly_intensity": round(mean_anomaly_intensity, 1),
                "pipeline": [
                    "Image Validation",
                    "Grayscale Conversion",
                    "Global Variance Calculation",
                    "Adaptive Pattern Thresholding",
                    "Multi-feature Scoring",
                    "Contour Isolation"
                ],
                "method": "OpenCV Prototype"
            }
        }
