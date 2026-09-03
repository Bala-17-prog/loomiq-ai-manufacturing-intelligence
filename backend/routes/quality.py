from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from backend.dependencies import get_db
from backend.vision.anomaly_detector import PrototypeVisualAnomalyDetector
from backend.models.models import QualityInspection
import os
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/quality", tags=["Quality Inspection"])

# Setup detector pointing to data dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
IMAGE_DIR = os.path.join(BASE_DIR, "data", "fabric_images")
detector = PrototypeVisualAnomalyDetector(IMAGE_DIR)

class ProcessingDetails(BaseModel):
    image_width: int
    image_height: int
    processing_time_ms: int
    detected_regions: int
    largest_region_pixels: int
    mean_anomaly_intensity: float
    pipeline: List[str]
    method: str

class InspectionResponse(BaseModel):
    inspection_id: str
    image_hash: str
    result: str
    anomaly_score: float
    severity: str
    potential_issue: str
    detection_strength: float
    original_image_url: str
    processed_image_url: str
    processing_details: ProcessingDetails

@router.post("/inspect", response_model=InspectionResponse)
async def inspect_fabric(file: UploadFile = File(...), db: Session = Depends(get_db)):
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG, and WEBP are supported.")
        
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image size exceeds 10MB limit.")
        
    try:
        # Run CV pipeline
        result_data = detector.process_image(contents, file.filename)
        
        # Save to DB
        inspection = QualityInspection(
            inspection_id=result_data["inspection_id"],
            image_hash=result_data["image_hash"],
            original_image_path=result_data["original_image_url"],
            processed_image_path=result_data["processed_image_url"],
            result=result_data["result"],
            anomaly_score=result_data["anomaly_score"],
            severity=result_data["severity"],
            potential_issue=result_data["potential_issue"],
            detection_strength=result_data["detection_strength"],
            processing_time_ms=result_data["processing_details"]["processing_time_ms"],
            detected_regions=result_data["processing_details"]["detected_regions"]
        )
        db.add(inspection)
        db.commit()
        db.refresh(inspection)
        
        return result_data
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

@router.get("/history")
def get_inspection_history(limit: int = 50, db: Session = Depends(get_db)):
    inspections = db.query(QualityInspection).order_by(QualityInspection.timestamp.desc()).limit(limit).all()
    return inspections
