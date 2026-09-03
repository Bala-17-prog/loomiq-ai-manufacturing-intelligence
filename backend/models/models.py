from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class Machine(Base):
    __tablename__ = "machines"
    
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, unique=True, index=True, nullable=False)
    machine_name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    machine_type = Column(String, nullable=False)
    installation_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    
    metrics = relationship("MachineMetric", back_populates="machine")
    production = relationship("Production", back_populates="machine")
    defects = relationship("Defect", back_populates="machine")
    maintenance = relationship("Maintenance", back_populates="machine")

class MachineMetric(Base):
    __tablename__ = "machine_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, ForeignKey("machines.machine_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    temperature = Column(Float, nullable=False)
    vibration = Column(Float, nullable=False)
    rpm = Column(Float, nullable=False)
    energy_consumption = Column(Float, nullable=False)
    running_hours = Column(Float, nullable=False)
    downtime_minutes = Column(Float, nullable=False)
    
    machine = relationship("Machine", back_populates="metrics")

class Production(Base):
    __tablename__ = "production"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    machine_id = Column(String, ForeignKey("machines.machine_id"), nullable=False)
    shift = Column(String, nullable=False)
    fabric_type = Column(String, nullable=False)
    target_quantity = Column(Integer, nullable=False)
    actual_quantity = Column(Integer, nullable=False)
    efficiency = Column(Float, nullable=False)
    
    machine = relationship("Machine", back_populates="production")

class Defect(Base):
    __tablename__ = "defects"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    machine_id = Column(String, ForeignKey("machines.machine_id"), nullable=False)
    fabric_type = Column(String, nullable=False)
    defect_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    
    machine = relationship("Machine", back_populates="defects")

class Maintenance(Base):
    __tablename__ = "maintenance"
    
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, ForeignKey("machines.machine_id"), nullable=False)
    date = Column(Date, nullable=False)
    maintenance_type = Column(String, nullable=False)
    downtime_minutes = Column(Float, nullable=False)
    notes = Column(String, nullable=True)
    
    machine = relationship("Machine", back_populates="maintenance")

class QualityInspection(Base):
    __tablename__ = "quality_inspections"
    
    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(String, unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    image_hash = Column(String, nullable=True)
    original_image_path = Column(String, nullable=False)
    processed_image_path = Column(String, nullable=False)
    result = Column(String, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
    potential_issue = Column(String, nullable=True)
    detection_strength = Column(Float, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    detected_regions = Column(Integer, nullable=True)
