import cv2
import numpy as np
from pathlib import Path
from app.config import settings

class ImageQualityService:
    """Service for assessing image quality before processing"""
    
    @staticmethod
    def assess_quality(image_path: str) -> dict:
        """
        Assess image quality across multiple dimensions
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with quality metrics and overall score
        """
        image = cv2.imread(image_path)
        
        if image is None:
            return {
                "overall_score": 0.0,
                "is_acceptable": False,
                "issues": ["Failed to load image"],
                "metrics": {}
            }
        
        # Run all quality checks
        blur_score, blur_acceptable = ImageQualityService._check_blur(image)
        brightness_score, brightness_acceptable = ImageQualityService._check_brightness(image)
        resolution_score, resolution_acceptable = ImageQualityService._check_resolution(image)
        
        # Calculate overall score (weighted average)
        overall_score = (
            blur_score * 0.4 +
            brightness_score * 0.3 +
            resolution_score * 0.3
        )
        
        # Check if acceptable
        is_acceptable = blur_acceptable and brightness_acceptable and resolution_acceptable
        
        # Collect issues
        issues = []
        if not blur_acceptable:
            issues.append("Image is too blurry")
        if not brightness_acceptable:
            issues.append("Poor lighting conditions")
        if not resolution_acceptable:
            issues.append("Resolution too low")
        
        # Quality guidance
        guidance = ImageQualityService._generate_guidance(issues)
        
        return {
            "overall_score": round(overall_score, 2),
            "is_acceptable": is_acceptable,
            "issues": issues,
            "guidance": guidance,
            "metrics": {
                "blur_score": round(blur_score, 2),
                "blur_variance": round(ImageQualityService._calculate_blur_variance(image), 2),
                "brightness_score": round(brightness_score, 2),
                "avg_brightness": round(ImageQualityService._calculate_brightness(image), 2),
                "resolution_score": round(resolution_score, 2),
                "resolution": f"{image.shape[1]}x{image.shape[0]}"
            }
        }
    
    @staticmethod
    def _check_blur(image: np.ndarray) -> tuple:
        """
        Check image blur using Laplacian variance
        Returns: (score, is_acceptable)
        """
        variance = ImageQualityService._calculate_blur_variance(image)
        
        # Score: 0-1 based on variance
        # Good image: variance > 500
        # Acceptable: variance > 100
        if variance > 500:
            score = 1.0
        elif variance > settings.BLUR_THRESHOLD:
            score = 0.7
        else:
            score = max(0.0, variance / settings.BLUR_THRESHOLD)
        
        is_acceptable = variance >= settings.BLUR_THRESHOLD
        
        return score, is_acceptable
    
    @staticmethod
    def _calculate_blur_variance(image: np.ndarray) -> float:
        """Calculate Laplacian variance (blur metric)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        return variance
    
    @staticmethod
    def _check_brightness(image: np.ndarray) -> tuple:
        """
        Check image brightness
        Returns: (score, is_acceptable)
        """
        brightness = ImageQualityService._calculate_brightness(image)
        
        # Optimal range: 80-180
        # Acceptable range: 50-200
        if settings.BRIGHTNESS_MIN <= brightness <= settings.BRIGHTNESS_MAX:
            if 80 <= brightness <= 180:
                score = 1.0
            else:
                # Calculate distance from optimal range
                if brightness < 80:
                    score = 0.7 + (brightness - settings.BRIGHTNESS_MIN) / (80 - settings.BRIGHTNESS_MIN) * 0.3
                else:
                    score = 0.7 + (settings.BRIGHTNESS_MAX - brightness) / (settings.BRIGHTNESS_MAX - 180) * 0.3
        else:
            # Outside acceptable range
            if brightness < settings.BRIGHTNESS_MIN:
                score = max(0.0, brightness / settings.BRIGHTNESS_MIN * 0.5)
            else:
                score = max(0.0, (255 - brightness) / (255 - settings.BRIGHTNESS_MAX) * 0.5)
        
        is_acceptable = settings.BRIGHTNESS_MIN <= brightness <= settings.BRIGHTNESS_MAX
        
        return score, is_acceptable
    
    @staticmethod
    def _calculate_brightness(image: np.ndarray) -> float:
        """Calculate average brightness using HSV"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        brightness = np.mean(hsv[:, :, 2])
        return brightness
    
    @staticmethod
    def _check_resolution(image: np.ndarray) -> tuple:
        """
        Check image resolution
        Returns: (score, is_acceptable)
        """
        height, width = image.shape[:2]
        min_width, min_height = settings.MIN_RESOLUTION
        
        # Check both dimensions
        width_ok = width >= min_width
        height_ok = height >= min_height
        
        is_acceptable = width_ok and height_ok
        
        # Calculate score
        if is_acceptable:
            # Bonus for higher resolution
            if width >= 1920 and height >= 1080:
                score = 1.0
            elif width >= 1280 and height >= 720:
                score = 0.9
            else:
                score = 0.8
        else:
            # Penalty for low resolution
            width_ratio = width / min_width
            height_ratio = height / min_height
            score = min(width_ratio, height_ratio) * 0.6
        
        return score, is_acceptable
    
    @staticmethod
    def _generate_guidance(issues: list) -> str:
        """Generate user-friendly guidance for improving image quality"""
        if not issues:
            return "Image quality is good. Proceed with capture."
        
        guidance_map = {
            "Image is too blurry": "Hold the camera steady or use a tripod. Ensure good focus.",
            "Poor lighting conditions": "Improve lighting. Move to a well-lit area or use flash.",
            "Resolution too low": "Use a higher quality camera or move closer to the subject."
        }
        
        guidance_list = [guidance_map.get(issue, issue) for issue in issues]
        return " | ".join(guidance_list)
    
    @staticmethod
    def get_quality_report(image_path: str) -> str:
        """Get a formatted quality report string"""
        quality = ImageQualityService.assess_quality(image_path)
        
        status = "✅ PASS" if quality["is_acceptable"] else "❌ FAIL"
        
        report = f"""
Image Quality Assessment: {status}
Overall Score: {quality['overall_score']}/1.0

Metrics:
- Blur Score: {quality['metrics']['blur_score']} (variance: {quality['metrics']['blur_variance']})
- Brightness Score: {quality['metrics']['brightness_score']} (avg: {quality['metrics']['avg_brightness']})
- Resolution Score: {quality['metrics']['resolution_score']} ({quality['metrics']['resolution']})

{"Issues Found:" if quality['issues'] else "No issues found."}
{chr(10).join(f"- {issue}" for issue in quality['issues'])}

{"Guidance: " + quality['guidance'] if quality['guidance'] else ""}
        """.strip()
        
        return report