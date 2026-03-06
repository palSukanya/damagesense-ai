import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.models.yolo_model import damage_model
from app.models.severity import SeverityEngine
from app.services.image_quality_service import ImageQualityService
from app.database.schemas import Inspection, Damage, Vehicle
from app.config import settings

class DetectionService:
    """Main service for vehicle damage detection and assessment"""
    
    def __init__(self):
        # Ensure model is loaded
        if damage_model.model is None:
            damage_model.load_model()
    
    def process_inspection(
        self,
        image_path: str,
        vehicle_id: str,
        inspection_type: str = "general",
        db: Session = None
    ) -> Dict:
        """
        Complete inspection pipeline:
        1. Image quality check
        2. Damage detection
        3. Severity assessment
        4. Database storage
        5. Report generation
        
        Args:
            image_path: Path to uploaded image
            vehicle_id: Vehicle identifier
            inspection_type: Type of inspection (claim, intake, service, resale)
            db: Database session
            
        Returns:
            Complete inspection report
        """
        inspection_id = f"INS-{uuid.uuid4().hex[:8].upper()}"
        
        # Step 1: Image quality assessment
        print(f"📸 Assessing image quality for {inspection_id}...")
        quality_result = ImageQualityService.assess_quality(image_path)
        
        if not quality_result["is_acceptable"]:
            return {
                "inspection_id": inspection_id,
                "status": "rejected",
                "reason": "Poor image quality",
                "quality_report": quality_result,
                "message": "Image quality is insufficient. " + quality_result.get("guidance", "")
            }
        
        # Step 2: Damage detection
        print(f"🔍 Running damage detection for {inspection_id}...")
        result = damage_model.predict(image_path)
        detections = damage_model.extract_detections(result)
        
        if not detections:
            print(f"✅ No damage detected for {inspection_id}")
            return {
                "inspection_id": inspection_id,
                "status": "complete",
                "damages_detected": 0,
                "overall_assessment": "No visible damage",
                "quality_score": quality_result["overall_score"],
                "detections": []
            }
        
        print(f"⚠️ Found {len(detections)} damages for {inspection_id}")
        
        # Step 3: Severity assessment for each damage
        print(f"📊 Assessing severity for {inspection_id}...")
        assessed_detections = [
            SeverityEngine.assess_single_damage(d) for d in detections
        ]
        
        # Step 4: Overall assessment
        overall_assessment = SeverityEngine.assess_overall_severity(assessed_detections)
        repair_time = SeverityEngine.estimate_repair_time(assessed_detections)
        
        # Step 5: Create annotated image
        annotated_path = self._create_annotated_image(image_path, result, inspection_id)
        
        # Step 6: Store in database if session provided
        if db:
            self._save_to_database(
                db=db,
                inspection_id=inspection_id,
                vehicle_id=vehicle_id,
                image_path=image_path,
                annotated_path=annotated_path,
                quality_score=quality_result["overall_score"],
                detections=assessed_detections,
                overall_assessment=overall_assessment,
                repair_time=repair_time,
                inspection_type=inspection_type
            )
        
        # Step 7: Generate final report
        report = {
            "inspection_id": inspection_id,
            "vehicle_id": vehicle_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "complete",
            
            # Image quality
            "image_quality": {
                "score": quality_result["overall_score"],
                "acceptable": quality_result["is_acceptable"],
                "metrics": quality_result["metrics"]
            },
            
            # Detection results
            "damages_detected": len(assessed_detections),
            "detections": assessed_detections,
            
            # Overall assessment
            "overall_assessment": overall_assessment,
            "estimated_repair_time_hours": repair_time,
            
            # Business decisions
            "recommendations": self._generate_recommendations(overall_assessment),
            "auto_approve_eligible": overall_assessment.get("auto_approve_eligible", False),
            
            # Paths
            "original_image": image_path,
            "annotated_image": annotated_path
        }
        
        print(f"✅ Inspection {inspection_id} completed successfully")
        return report
    
    def _create_annotated_image(self, image_path: str, result, inspection_id: str) -> str:
        """Create and save annotated image with bounding boxes and labels"""
        import cv2
        
        # Read original image
        image = cv2.imread(image_path)
        
        # Let YOLO plot the results
        annotated = result.plot()
        
        # Save annotated image
        output_filename = f"{inspection_id}_annotated.jpg"
        output_path = settings.ANNOTATED_DIR / output_filename
        cv2.imwrite(str(output_path), annotated)
        
        return str(output_path)
    
    def _save_to_database(
        self,
        db: Session,
        inspection_id: str,
        vehicle_id: str,
        image_path: str,
        annotated_path: str,
        quality_score: float,
        detections: List[Dict],
        overall_assessment: Dict,
        repair_time: float,
        inspection_type: str
    ):
        """Save inspection results to database"""
        
        # Get or create vehicle
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
        if not vehicle:
            vehicle = Vehicle(vehicle_id=vehicle_id)
            db.add(vehicle)
            db.commit()
            db.refresh(vehicle)
        
        # Create inspection record
        inspection = Inspection(
            inspection_id=inspection_id,
            vehicle_id=vehicle.id,
            image_path=image_path,
            annotated_image_path=annotated_path,
            image_quality_score=quality_score,
            damages_detected=len(detections),
            detection_results={"detections": detections},
            overall_severity=overall_assessment["overall_severity"],
            overall_confidence=overall_assessment["overall_score"],
            estimated_repair_cost=overall_assessment["total_estimated_cost"],
            estimated_repair_hours=repair_time,
            has_safety_critical_damage=overall_assessment["safety_critical"],
            requires_manual_review=not overall_assessment.get("auto_approve_eligible", False),
            auto_approved=overall_assessment.get("auto_approve_eligible", False),
            inspection_type=inspection_type
        )
        db.add(inspection)
        db.commit()
        db.refresh(inspection)
        
        # Create individual damage records
        for det in detections:
            damage = Damage(
                inspection_id=inspection.id,
                damage_type=det["damage_type"],
                damage_category=det["damage_category"],
                bbox_x1=det["bbox"]["x1"],
                bbox_y1=det["bbox"]["y1"],
                bbox_x2=det["bbox"]["x2"],
                bbox_y2=det["bbox"]["y2"],
                damage_area_pixels=det["bbox_area"],
                damage_area_percentage=det["area_percentage"],
                severity=det["severity"],
                severity_score=det["severity_score"],
                confidence=det["confidence"],
                estimated_cost=det["estimated_repair_cost"],
                is_safety_critical=det["damage_category"] == "functional"
            )
            db.add(damage)
        
        db.commit()
        print(f"💾 Saved inspection {inspection_id} to database")
    
    def _generate_recommendations(self, assessment: Dict) -> List[str]:
        """Generate actionable recommendations based on assessment"""
        recommendations = []
        
        severity = assessment["overall_severity"]
        total_cost = assessment["total_estimated_cost"]
        safety_critical = assessment["safety_critical"]
        
        # Severity-based recommendations
        if severity == "critical":
            recommendations.append("⚠️ CRITICAL: Immediate attention required")
            recommendations.append("Recommend comprehensive inspection by certified technician")
        elif severity == "high":
            recommendations.append("High severity damage detected - prioritize repair")
        elif severity == "medium":
            recommendations.append("Moderate damage - schedule repair within 2 weeks")
        else:
            recommendations.append("Minor damage - cosmetic repair can be deferred")
        
        # Safety recommendations
        if safety_critical:
            recommendations.append("🚨 SAFETY CRITICAL: Do not operate vehicle until repaired")
        
        # Cost-based recommendations
        if total_cost > settings.AUTO_APPROVE_THRESHOLD:
            recommendations.append(f"Cost exceeds auto-approval threshold (₹{settings.AUTO_APPROVE_THRESHOLD:,.0f})")
            recommendations.append("Manual adjuster review required")
        else:
            recommendations.append(f"✅ Eligible for auto-approval (cost: ₹{total_cost:,.2f})")
        
        return recommendations
    
    def get_inspection_history(self, vehicle_id: str, db: Session, limit: int = 10) -> List[Dict]:
        """Get inspection history for a vehicle"""
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
        if not vehicle:
            return []
        
        inspections = (
            db.query(Inspection)
            .filter(Inspection.vehicle_id == vehicle.id)
            .order_by(Inspection.created_at.desc())
            .limit(limit)
            .all()
        )
        
        return [
            {
                "inspection_id": insp.inspection_id,
                "date": insp.created_at.isoformat(),
                "damages_detected": insp.damages_detected,
                "overall_severity": insp.overall_severity,
                "estimated_cost": insp.estimated_repair_cost,
                "inspection_type": insp.inspection_type
            }
            for insp in inspections
        ]