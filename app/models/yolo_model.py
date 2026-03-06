import torch
from ultralytics import YOLO
from pathlib import Path
from app.config import settings
import numpy as np

class DamageDetectionModel:
    """Wrapper for YOLO-based damage detection model"""
    
    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔧 Using device: {self.device}")
        
    def load_model(self):
        """Load the trained YOLO model"""
        model_path = Path(settings.MODEL_PATH)
        
        if not model_path.exists():
            print(f"⚠️ Model not found at {model_path}")
            print("📥 Using YOLOv8n-seg pretrained model as fallback")
            # Use pretrained model for demo purposes
            self.model = YOLO("yolov8n-seg.pt")
        else:
            print(f"✅ Loading model from {model_path}")
            self.model = YOLO(str(model_path))
        
        self.model.to(self.device)
        return self
    
    def predict(self, image_path: str, conf_threshold: float = None, iou_threshold: float = None):
        """
        Run inference on an image
        
        Args:
            image_path: Path to the image
            conf_threshold: Confidence threshold (default from settings)
            iou_threshold: IOU threshold for NMS (default from settings)
            
        Returns:
            YOLO Results object
        """
        if self.model is None:
            self.load_model()
        
        conf = conf_threshold or settings.CONFIDENCE_THRESHOLD
        iou = iou_threshold or settings.IOU_THRESHOLD
        
        results = self.model.predict(
            source=image_path,
            conf=conf,
            iou=iou,
            device=self.device,
            verbose=False
        )
        
        return results[0]  # Return first result (single image)
    
    def extract_detections(self, result):
        """
        Extract structured detection information from YOLO results
        
        Returns:
            List of detection dictionaries
        """
        detections = []
        
        if result.boxes is None or len(result.boxes) == 0:
            return detections
        
        # Get image dimensions
        img_height, img_width = result.orig_shape
        
        for i in range(len(result.boxes)):
            box = result.boxes[i]
            
            # Extract bbox coordinates
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            
            # Extract mask if available
            mask_area = 0
            if result.masks is not None and i < len(result.masks):
                mask = result.masks[i].data.cpu().numpy()[0]
                mask_area = np.sum(mask)
            
            # Calculate area percentage
            bbox_area = (x2 - x1) * (y2 - y1)
            total_area = img_width * img_height
            area_percentage = (bbox_area / total_area) * 100
            
            # Get class and confidence
            class_id = int(box.cls[0].cpu().numpy())
            confidence = float(box.conf[0].cpu().numpy())
            
            # Map class ID to damage type
            damage_type = settings.DAMAGE_CLASSES.get(class_id, f"unknown_{class_id}")
            
            detection = {
                "damage_type": damage_type,
                "confidence": round(confidence, 3),
                "bbox": {
                    "x1": float(x1),
                    "y1": float(y1),
                    "x2": float(x2),
                    "y2": float(y2)
                },
                "bbox_area": float(bbox_area),
                "mask_area": float(mask_area) if mask_area > 0 else None,
                "area_percentage": round(area_percentage, 2),
                "image_dimensions": {
                    "width": img_width,
                    "height": img_height
                }
            }
            
            detections.append(detection)
        
        return detections
    
    def get_model_info(self):
        """Get model information"""
        if self.model is None:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "device": self.device,
            "model_type": str(type(self.model).__name__),
            "task": "segmentation"
        }

# Global model instance
damage_model = DamageDetectionModel()