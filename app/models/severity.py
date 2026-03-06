from app.config import settings
from typing import List, Dict
import numpy as np

class SeverityEngine:
    """
    Hybrid severity assessment engine combining:
    - Area-based scoring
    - Damage type weighting
    - Safety criticality
    - Part replacement cost factors
    """
    
    # Damage type severity weights
    DAMAGE_TYPE_WEIGHTS = {
        "scratch": 0.3,
        "dent": 0.5,
        "crack": 0.7,
        "broken_part": 0.9,
        "paint_damage": 0.4,
        "glass_damage": 0.8
    }
    
    # Vehicle part cost multipliers (relative)
    PART_COST_MULTIPLIERS = {
        "bumper": 1.0,
        "door": 1.5,
        "hood": 1.3,
        "fender": 1.2,
        "roof": 1.4,
        "windshield": 2.0,
        "headlight": 1.8,
        "taillight": 1.5,
        "mirror": 1.0,
        "unknown": 1.0
    }
    
    # Base repair costs (INR) - rough estimates
    BASE_REPAIR_COSTS = {
        "scratch": 2000,
        "dent": 5000,
        "crack": 8000,
        "broken_part": 15000,
        "paint_damage": 3000,
        "glass_damage": 12000
    }
    
    @staticmethod
    def assess_single_damage(detection: Dict) -> Dict:
        """
        Assess severity of a single damage detection
        
        Args:
            detection: Detection dictionary with damage info
            
        Returns:
            Enhanced detection with severity assessment
        """
        damage_type = detection.get("damage_type", "unknown")
        area_percentage = detection.get("area_percentage", 0)
        confidence = detection.get("confidence", 0)
        
        # Component 1: Area-based severity
        if area_percentage < settings.SEVERITY_LOW_THRESHOLD:
            area_severity = "low"
            area_score = 0.3
        elif area_percentage < settings.SEVERITY_MEDIUM_THRESHOLD:
            area_severity = "medium"
            area_score = 0.6
        else:
            area_severity = "high"
            area_score = 0.9
        
        # Component 2: Damage type weight
        type_weight = SeverityEngine.DAMAGE_TYPE_WEIGHTS.get(damage_type, 0.5)
        
        # Component 3: Combined severity score
        severity_score = (area_score * 0.6) + (type_weight * 0.4)
        
        # Determine final severity
        if severity_score < 0.4:
            final_severity = "low"
        elif severity_score < 0.7:
            final_severity = "medium"
        else:
            final_severity = "high"
        
        # Estimate repair cost
        base_cost = SeverityEngine.BASE_REPAIR_COSTS.get(damage_type, 5000)
        area_multiplier = 1 + (area_percentage / 100)  # Scale by area
        estimated_cost = base_cost * area_multiplier
        
        # Add severity assessment to detection
        detection["severity"] = final_severity
        detection["severity_score"] = round(severity_score, 3)
        detection["severity_breakdown"] = {
            "area_based": area_severity,
            "area_score": round(area_score, 2),
            "type_weight": round(type_weight, 2)
        }
        detection["estimated_repair_cost"] = round(estimated_cost, 2)
        detection["damage_category"] = SeverityEngine._classify_damage_category(damage_type)
        
        return detection
    
    @staticmethod
    def _classify_damage_category(damage_type: str) -> str:
        """Classify damage into cosmetic/structural/functional"""
        cosmetic = ["scratch", "paint_damage"]
        structural = ["dent", "crack"]
        functional = ["broken_part", "glass_damage"]
        
        if damage_type in cosmetic:
            return "cosmetic"
        elif damage_type in structural:
            return "structural"
        elif damage_type in functional:
            return "functional"
        else:
            return "unknown"
    
    @staticmethod
    def assess_overall_severity(detections: List[Dict]) -> Dict:
        """
        Assess overall vehicle damage severity
        
        Args:
            detections: List of individual damage detections
            
        Returns:
            Overall assessment dictionary
        """
        if not detections:
            return {
                "overall_severity": "none",
                "overall_score": 0.0,
                "total_estimated_cost": 0.0,
                "damage_count": 0,
                "highest_severity": None,
                "safety_critical": False
            }
        
        # Calculate metrics
        severity_scores = [d["severity_score"] for d in detections]
        severities = [d["severity"] for d in detections]
        costs = [d["estimated_repair_cost"] for d in detections]
        
        # Overall score (weighted average with max influence)
        avg_score = np.mean(severity_scores)
        max_score = np.max(severity_scores)
        overall_score = (avg_score * 0.4) + (max_score * 0.6)
        
        # Overall severity
        if overall_score < 0.4:
            overall_severity = "low"
        elif overall_score < 0.7:
            overall_severity = "medium"
        else:
            overall_severity = "high"
        
        # Check for critical conditions
        high_severity_count = severities.count("high")
        if high_severity_count >= 3 or max_score > 0.85:
            overall_severity = "critical"
        
        # Total cost
        total_cost = sum(costs)
        
        # Safety critical check
        safety_critical = any(
            d.get("damage_category") == "functional" and d.get("severity") in ["high", "critical"]
            for d in detections
        )
        
        return {
            "overall_severity": overall_severity,
            "overall_score": round(overall_score, 3),
            "total_estimated_cost": round(total_cost, 2),
            "damage_count": len(detections),
            "highest_severity": max(severities, key=lambda x: ["low", "medium", "high", "critical"].index(x)),
            "severity_distribution": {
                "low": severities.count("low"),
                "medium": severities.count("medium"),
                "high": severities.count("high")
            },
            "safety_critical": safety_critical,
            "auto_approve_eligible": total_cost < settings.AUTO_APPROVE_THRESHOLD and not safety_critical
        }
    
    @staticmethod
    def estimate_repair_time(detections: List[Dict]) -> float:
        """
        Estimate total repair time in hours
        
        Args:
            detections: List of damage detections
            
        Returns:
            Estimated hours
        """
        # Base time per damage type (hours)
        base_times = {
            "scratch": 0.5,
            "dent": 2.0,
            "crack": 1.5,
            "broken_part": 3.0,
            "paint_damage": 1.0,
            "glass_damage": 2.5
        }
        
        total_hours = 0
        for detection in detections:
            damage_type = detection.get("damage_type", "unknown")
            severity = detection.get("severity", "low")
            
            base_time = base_times.get(damage_type, 1.5)
            
            # Multiply by severity
            severity_multiplier = {"low": 0.8, "medium": 1.0, "high": 1.5}.get(severity, 1.0)
            
            total_hours += base_time * severity_multiplier
        
        return round(total_hours, 1)