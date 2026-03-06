import hashlib
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database.schemas import DamageHistory, Damage, Inspection, Vehicle

class HistoryService:
    """Service for temporal damage tracking and fraud detection"""
    
    @staticmethod
    def create_damage_fingerprint(damage: Dict) -> str:
        """
        Create a unique fingerprint for a damage based on:
        - Location (bbox)
        - Type
        - Approximate size
        
        Returns: Hash string
        """
        # Normalize bbox to relative coordinates (0-1)
        img_width = damage["image_dimensions"]["width"]
        img_height = damage["image_dimensions"]["height"]
        
        x1_rel = damage["bbox"]["x1"] / img_width
        y1_rel = damage["bbox"]["y1"] / img_height
        x2_rel = damage["bbox"]["x2"] / img_width
        y2_rel = damage["bbox"]["y2"] / img_height
        
        # Center point
        center_x = (x1_rel + x2_rel) / 2
        center_y = (y1_rel + y2_rel) / 2
        
        # Size
        size = damage["area_percentage"]
        
        # Create fingerprint string (with some tolerance for slight variations)
        fingerprint_str = f"{damage['damage_type']}_{center_x:.2f}_{center_y:.2f}_{size:.1f}"
        
        # Hash it
        return hashlib.md5(fingerprint_str.encode()).hexdigest()
    
    @staticmethod
    def compare_with_history(
        vehicle_id: str,
        current_detections: List[Dict],
        db: Session,
        time_window_days: int = 90
    ) -> Dict:
        """
        Compare current damages with historical records
        
        Returns:
            - new_damages: List of new damages
            - existing_damages: List of previously seen damages
            - fraud_alerts: List of suspicious patterns
        """
        # Get vehicle
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
        if not vehicle:
            # First time seeing this vehicle - all damages are new
            return {
                "new_damages": current_detections,
                "existing_damages": [],
                "fraud_alerts": [],
                "is_first_inspection": True
            }
        
        # Get damage history within time window
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        history_records = (
            db.query(DamageHistory)
            .filter(
                DamageHistory.vehicle_id == vehicle.id,
                DamageHistory.last_detected >= cutoff_date
            )
            .all()
        )
        
        # Create set of known fingerprints
        known_fingerprints = {record.damage_fingerprint for record in history_records}
        
        # Classify damages
        new_damages = []
        existing_damages = []
        fraud_alerts = []
        
        for detection in current_detections:
            fingerprint = HistoryService.create_damage_fingerprint(detection)
            
            if fingerprint in known_fingerprints:
                # This damage was seen before
                detection["is_new_damage"] = False
                detection["fingerprint"] = fingerprint
                existing_damages.append(detection)
                
                # Update history
                history_record = next(
                    (r for r in history_records if r.damage_fingerprint == fingerprint),
                    None
                )
                if history_record:
                    history_record.last_detected = datetime.utcnow()
                    history_record.detection_count += 1
            else:
                # New damage
                detection["is_new_damage"] = True
                detection["fingerprint"] = fingerprint
                new_damages.append(detection)
                
                # Create new history record
                new_history = DamageHistory(
                    vehicle_id=vehicle.id,
                    damage_fingerprint=fingerprint,
                    first_detected=datetime.utcnow(),
                    last_detected=datetime.utcnow(),
                    detection_count=1
                )
                db.add(new_history)
        
        # Fraud detection logic
        fraud_alerts = HistoryService._detect_fraud_patterns(
            vehicle_id=vehicle_id,
            new_damages=new_damages,
            existing_damages=existing_damages,
            db=db
        )
        
        db.commit()
        
        return {
            "new_damages": new_damages,
            "new_damages_count": len(new_damages),
            "existing_damages": existing_damages,
            "existing_damages_count": len(existing_damages),
            "fraud_alerts": fraud_alerts,
            "is_first_inspection": False
        }
    
    @staticmethod
    def _detect_fraud_patterns(
        vehicle_id: str,
        new_damages: List[Dict],
        existing_damages: List[Dict],
        db: Session
    ) -> List[Dict]:
        """
        Detect suspicious patterns that may indicate fraud
        
        Returns:
            List of fraud alert dictionaries
        """
        alerts = []
        
        # Pattern 1: Sudden spike in damage count
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
        recent_inspections = (
            db.query(Inspection)
            .filter(Inspection.vehicle_id == vehicle.id)
            .order_by(Inspection.created_at.desc())
            .limit(5)
            .all()
        )
        
        if len(recent_inspections) >= 2:
            avg_previous_damages = sum(i.damages_detected for i in recent_inspections[1:]) / (len(recent_inspections) - 1)
            if len(new_damages) > avg_previous_damages * 3:
                alerts.append({
                    "type": "sudden_damage_spike",
                    "severity": "medium",
                    "message": f"Unusual spike in new damages: {len(new_damages)} new vs avg {avg_previous_damages:.1f}",
                    "recommendation": "Manual review recommended"
                })
        
        # Pattern 2: Multiple high-value damages claimed at once
        high_value_new = [d for d in new_damages if d["estimated_repair_cost"] > 10000]
        if len(high_value_new) >= 3:
            alerts.append({
                "type": "multiple_high_value_claims",
                "severity": "high",
                "message": f"{len(high_value_new)} high-value new damages detected simultaneously",
                "recommendation": "Investigate claim circumstances"
            })
        
        # Pattern 3: Re-claiming existing damage
        if len(existing_damages) > len(new_damages) and len(existing_damages) >= 3:
            alerts.append({
                "type": "predominantly_existing_damage",
                "severity": "high",
                "message": f"{len(existing_damages)} damages match previous records",
                "recommendation": "Verify claim is for new incident, not pre-existing damage"
            })
        
        # Pattern 4: Frequent claims
        recent_30_days = (
            db.query(Inspection)
            .filter(
                Inspection.vehicle_id == vehicle.id,
                Inspection.created_at >= datetime.utcnow() - timedelta(days=30)
            )
            .count()
        )
        
        if recent_30_days >= 3:
            alerts.append({
                "type": "frequent_claims",
                "severity": "medium",
                "message": f"{recent_30_days} inspections in the last 30 days",
                "recommendation": "Review claim history pattern"
            })
        
        return alerts
    
    @staticmethod
    def get_vehicle_damage_timeline(vehicle_id: str, db: Session) -> List[Dict]:
        """
        Get complete damage timeline for a vehicle
        
        Returns:
            Chronological list of all inspection events
        """
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
        if not vehicle:
            return []
        
        inspections = (
            db.query(Inspection)
            .filter(Inspection.vehicle_id == vehicle.id)
            .order_by(Inspection.created_at.asc())
            .all()
        )
        
        timeline = []
        for insp in inspections:
            damages = db.query(Damage).filter(Damage.inspection_id == insp.id).all()
            
            timeline.append({
                "date": insp.created_at.isoformat(),
                "inspection_id": insp.inspection_id,
                "inspection_type": insp.inspection_type,
                "damages_count": insp.damages_detected,
                "overall_severity": insp.overall_severity,
                "estimated_cost": insp.estimated_repair_cost,
                "new_damages": insp.new_damages_count,
                "existing_damages": insp.existing_damages_count,
                "damages_detail": [
                    {
                        "type": d.damage_type,
                        "severity": d.severity,
                        "cost": d.estimated_cost,
                        "is_new": d.is_new_damage
                    }
                    for d in damages
                ]
            })
        
        return timeline
    
    @staticmethod
    def generate_damage_evolution_report(vehicle_id: str, db: Session) -> Dict:
        """
        Generate a comprehensive report on how vehicle damage has evolved
        """
        timeline = HistoryService.get_vehicle_damage_timeline(vehicle_id, db)
        
        if not timeline:
            return {"error": "No inspection history found"}
        
        # Calculate trends
        total_inspections = len(timeline)
        total_damages_ever = sum(event["damages_count"] for event in timeline)
        total_cost_accumulated = sum(event["estimated_cost"] or 0 for event in timeline)
        
        # Severity progression
        severity_progression = [event["overall_severity"] for event in timeline]
        
        # Cost progression
        cost_progression = [
            {
                "date": event["date"],
                "cost": event["estimated_cost"]
            }
            for event in timeline
        ]
        
        return {
            "vehicle_id": vehicle_id,
            "first_inspection": timeline[0]["date"],
            "last_inspection": timeline[-1]["date"],
            "total_inspections": total_inspections,
            "total_damages_recorded": total_damages_ever,
            "total_cost_accumulated": round(total_cost_accumulated, 2),
            "severity_progression": severity_progression,
            "cost_progression": cost_progression,
            "timeline": timeline
        }