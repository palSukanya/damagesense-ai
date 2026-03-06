import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict
from app.config import settings

class VehicleCanonicalMapper:
    """
    Maps detected damages onto a canonical 2D vehicle template
    """
    
    # Define vehicle zones (normalized coordinates)
    VEHICLE_ZONES = {
        "front": {
            "hood": {"x": 0.5, "y": 0.3, "w": 0.4, "h": 0.25},
            "front_bumper": {"x": 0.5, "y": 0.65, "w": 0.5, "h": 0.15},
            "windshield": {"x": 0.5, "y": 0.15, "w": 0.35, "h": 0.1},
            "headlight_left": {"x": 0.25, "y": 0.55, "w": 0.1, "h": 0.08},
            "headlight_right": {"x": 0.75, "y": 0.55, "w": 0.1, "h": 0.08}
        },
        "side": {
            "front_door": {"x": 0.35, "y": 0.4, "w": 0.2, "h": 0.3},
            "rear_door": {"x": 0.6, "y": 0.4, "w": 0.2, "h": 0.3},
            "front_fender": {"x": 0.2, "y": 0.45, "w": 0.15, "h": 0.25},
            "rear_fender": {"x": 0.8, "y": 0.45, "w": 0.15, "h": 0.25},
            "side_mirror": {"x": 0.25, "y": 0.3, "w": 0.05, "h": 0.05}
        },
        "rear": {
            "trunk": {"x": 0.5, "y": 0.35, "w": 0.4, "h": 0.25},
            "rear_bumper": {"x": 0.5, "y": 0.65, "w": 0.5, "h": 0.15},
            "rear_windshield": {"x": 0.5, "y": 0.2, "w": 0.35, "h": 0.1},
            "taillight_left": {"x": 0.25, "y": 0.55, "w": 0.1, "h": 0.08},
            "taillight_right": {"x": 0.75, "y": 0.55, "w": 0.1, "h": 0.08}
        }
    }
    
    @staticmethod
    def create_vehicle_template(width: int = 800, height: int = 400, view: str = "side") -> np.ndarray:
        """
        Create a simple 2D vehicle template
        
        Args:
            width: Template width
            height: Template height
            view: Vehicle view (front, side, rear)
            
        Returns:
            Template image
        """
        # Create white background
        template = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        if view == "side":
            # Draw side view silhouette
            # Main body
            cv2.rectangle(template, 
                         (int(width * 0.15), int(height * 0.35)),
                         (int(width * 0.85), int(height * 0.65)),
                         (200, 200, 200), -1)
            
            # Roof
            cv2.rectangle(template,
                         (int(width * 0.25), int(height * 0.2)),
                         (int(width * 0.7), int(height * 0.35)),
                         (200, 200, 200), -1)
            
            # Wheels
            cv2.circle(template, (int(width * 0.25), int(height * 0.7)), int(height * 0.08), (100, 100, 100), -1)
            cv2.circle(template, (int(width * 0.75), int(height * 0.7)), int(height * 0.08), (100, 100, 100), -1)
            
        elif view == "front":
            # Draw front view
            # Main body
            cv2.rectangle(template,
                         (int(width * 0.2), int(height * 0.25)),
                         (int(width * 0.8), int(height * 0.8)),
                         (200, 200, 200), -1)
            
            # Roof
            cv2.rectangle(template,
                         (int(width * 0.25), int(height * 0.1)),
                         (int(width * 0.75), int(height * 0.25)),
                         (200, 200, 200), -1)
            
            # Wheels
            cv2.rectangle(template,
                         (int(width * 0.15), int(height * 0.7)),
                         (int(width * 0.25), int(height * 0.85)),
                         (100, 100, 100), -1)
            cv2.rectangle(template,
                         (int(width * 0.75), int(height * 0.7)),
                         (int(width * 0.85), int(height * 0.85)),
                         (100, 100, 100), -1)
        
        elif view == "rear":
            # Similar to front view
            cv2.rectangle(template,
                         (int(width * 0.2), int(height * 0.25)),
                         (int(width * 0.8), int(height * 0.8)),
                         (200, 200, 200), -1)
            cv2.rectangle(template,
                         (int(width * 0.25), int(height * 0.1)),
                         (int(width * 0.75), int(height * 0.25)),
                         (200, 200, 200), -1)
            cv2.rectangle(template,
                         (int(width * 0.15), int(height * 0.7)),
                         (int(width * 0.25), int(height * 0.85)),
                         (100, 100, 100), -1)
            cv2.rectangle(template,
                         (int(width * 0.75), int(height * 0.7)),
                         (int(width * 0.85), int(height * 0.85)),
                         (100, 100, 100), -1)
        
        # Add border
        cv2.rectangle(template, (0, 0), (width-1, height-1), (100, 100, 100), 2)
        
        # Add title
        cv2.putText(template, f"{view.upper()} VIEW", 
                   (int(width * 0.35), 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 50, 50), 2)
        
        return template
    
    @staticmethod
    def map_damage_to_template(
        detections: List[Dict],
        template_width: int = 800,
        template_height: int = 400,
        view: str = "side"
    ) -> np.ndarray:
        """
        Map detected damages onto the vehicle template
        
        Args:
            detections: List of damage detections
            template_width: Width of template
            template_height: Height of template
            view: Vehicle view
            
        Returns:
            Annotated template image
        """
        # Create template
        template = VehicleCanonicalMapper.create_vehicle_template(
            template_width, template_height, view
        )
        
        # Severity color map
        severity_colors = {
            "low": (100, 255, 100),      # Green
            "medium": (100, 165, 255),   # Orange
            "high": (50, 50, 255),       # Red
            "critical": (128, 0, 128)    # Purple
        }
        
        # Map each damage to template
        for i, detection in enumerate(detections):
            # For demo purposes, distribute damages across template
            # In production, would use actual part detection
            
            # Calculate position on template (simple distribution)
            num_detections = len(detections)
            x_ratio = (i + 1) / (num_detections + 1)
            y_ratio = 0.5  # Middle height
            
            x = int(template_width * x_ratio)
            y = int(template_height * y_ratio)
            
            # Get severity color
            severity = detection.get("severity", "medium")
            color = severity_colors.get(severity, (150, 150, 150))
            
            # Draw damage marker
            radius = int(20 * (detection.get("severity_score", 0.5) + 0.5))
            cv2.circle(template, (x, y), radius, color, -1)
            cv2.circle(template, (x, y), radius, (0, 0, 0), 2)
            
            # Add label
            damage_type = detection.get("damage_type", "unknown")
            label = f"{i+1}. {damage_type[:4]}"
            cv2.putText(template, label,
                       (x - 20, y - radius - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        return template
    
    @staticmethod
    def create_comprehensive_damage_map(
        detections: List[Dict],
        output_path: str
    ) -> str:
        """
        Create a comprehensive damage map with multiple views
        
        Args:
            detections: List of damage detections
            output_path: Path to save the map
            
        Returns:
            Path to saved map
        """
        # Create templates for different views
        side_view = VehicleCanonicalMapper.map_damage_to_template(
            detections, 600, 300, "side"
        )
        front_view = VehicleCanonicalMapper.map_damage_to_template(
            detections[:len(detections)//2], 400, 300, "front"
        )
        rear_view = VehicleCanonicalMapper.map_damage_to_template(
            detections[len(detections)//2:], 400, 300, "rear"
        )
        
        # Combine into single image
        # Top row: side view
        # Bottom row: front and rear
        
        top_row = side_view
        bottom_left = cv2.resize(front_view, (300, 225))
        bottom_right = cv2.resize(rear_view, (300, 225))
        
        # Create white padding
        padding = np.ones((225, 0, 3), dtype=np.uint8) * 255
        bottom_row = np.hstack([bottom_left, padding, bottom_right])
        
        # Resize bottom row to match top width
        bottom_row_resized = cv2.resize(bottom_row, (600, 225))
        
        # Combine
        final_map = np.vstack([top_row, bottom_row_resized])
        
        # Add legend
        legend_height = 80
        legend = np.ones((legend_height, 600, 3), dtype=np.uint8) * 255
        
        cv2.putText(legend, "SEVERITY LEGEND:", (20, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        cv2.circle(legend, (50, 55), 10, (100, 255, 100), -1)
        cv2.putText(legend, "Low", (70, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        cv2.circle(legend, (150, 55), 10, (100, 165, 255), -1)
        cv2.putText(legend, "Medium", (170, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        cv2.circle(legend, (280, 55), 10, (50, 50, 255), -1)
        cv2.putText(legend, "High", (300, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        cv2.circle(legend, (380, 55), 10, (128, 0, 128), -1)
        cv2.putText(legend, "Critical", (400, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Add to final map
        final_map = np.vstack([final_map, legend])
        
        # Save
        cv2.imwrite(output_path, final_map)
        
        return output_path