from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Vehicle(Base):
    """Vehicle information table"""
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, unique=True, index=True)  # Registration number or VIN
    make = Column(String, nullable=True)
    model = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    color = Column(String, nullable=True)
    vehicle_type = Column(String, nullable=True)  # 2W, 3W, 4W
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    inspections = relationship("Inspection", back_populates="vehicle")

class Inspection(Base):
    """Vehicle inspection records"""
    __tablename__ = "inspections"
    
    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(String, unique=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    
    # Image info
    image_path = Column(String)
    annotated_image_path = Column(String, nullable=True)
    image_quality_score = Column(Float)
    
    # Detection results
    damages_detected = Column(Integer, default=0)
    detection_results = Column(JSON)  # Stores all damage detections
    
    # Overall assessment
    overall_severity = Column(String)  # low, medium, high, critical
    overall_confidence = Column(Float)
    
    # Estimated costs
    estimated_repair_cost = Column(Float, nullable=True)
    estimated_repair_hours = Column(Float, nullable=True)
    
    # Flags
    has_safety_critical_damage = Column(Boolean, default=False)
    requires_manual_review = Column(Boolean, default=False)
    auto_approved = Column(Boolean, default=False)
    
    # Temporal tracking
    new_damages_count = Column(Integer, default=0)
    existing_damages_count = Column(Integer, default=0)
    
    # Metadata
    inspector_id = Column(String, nullable=True)
    inspection_type = Column(String)  # claim, intake, service, resale
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="inspections")
    damages = relationship("Damage", back_populates="inspection")

class Damage(Base):
    """Individual damage records"""
    __tablename__ = "damages"
    
    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"))
    
    # Damage details
    damage_type = Column(String)  # scratch, dent, crack, etc.
    damage_category = Column(String)  # cosmetic, structural, functional
    vehicle_part = Column(String, nullable=True)  # hood, door, bumper, etc.
    
    # Location and size
    bbox_x1 = Column(Float)
    bbox_y1 = Column(Float)
    bbox_x2 = Column(Float)
    bbox_y2 = Column(Float)
    damage_area_pixels = Column(Float)
    damage_area_percentage = Column(Float)
    
    # Assessment
    severity = Column(String)  # low, medium, high
    severity_score = Column(Float)
    confidence = Column(Float)
    
    # Cost estimation
    estimated_cost = Column(Float, nullable=True)
    
    # Flags
    is_safety_critical = Column(Boolean, default=False)
    is_new_damage = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    inspection = relationship("Inspection", back_populates="damages")

class DamageHistory(Base):
    """Historical damage tracking for fraud detection"""
    __tablename__ = "damage_history"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    damage_fingerprint = Column(String)  # Hash of damage location/type
    first_detected = Column(DateTime)
    last_detected = Column(DateTime)
    detection_count = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)