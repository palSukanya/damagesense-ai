import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import io

def resize_image(image_path: str, max_width: int = 1920, max_height: int = 1080) -> str:
    """
    Resize image while maintaining aspect ratio
    
    Args:
        image_path: Path to image
        max_width: Maximum width
        max_height: Maximum height
        
    Returns:
        Path to resized image
    """
    img = cv2.imread(image_path)
    height, width = img.shape[:2]
    
    # Calculate scaling factor
    scale = min(max_width / width, max_height / height, 1.0)
    
    if scale < 1.0:
        new_width = int(width * scale)
        new_height = int(height * scale)
        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Save resized image
        output_path = str(Path(image_path).with_suffix('.resized.jpg'))
        cv2.imwrite(output_path, img)
        return output_path
    
    return image_path

def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalize image for better processing"""
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    # Split channels
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    # Merge channels
    lab = cv2.merge([l, a, b])
    
    # Convert back to BGR
    normalized = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    return normalized

def remove_reflections(image: np.ndarray) -> np.ndarray:
    """
    Attempt to reduce reflections in image
    """
    # Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Detect bright spots (potential reflections)
    _, bright_mask = cv2.threshold(hsv[:, :, 2], 200, 255, cv2.THRESH_BINARY)
    
    # Dilate to cover reflection area
    kernel = np.ones((5, 5), np.uint8)
    bright_mask = cv2.dilate(bright_mask, kernel, iterations=1)
    
    # Inpaint the reflection areas
    result = cv2.inpaint(image, bright_mask, 3, cv2.INPAINT_TELEA)
    
    return result

def enhance_image_quality(image_path: str, output_path: str = None) -> str:
    """
    Apply multiple enhancement techniques
    
    Args:
        image_path: Input image path
        output_path: Output image path (optional)
        
    Returns:
        Path to enhanced image
    """
    img = cv2.imread(image_path)
    
    # Apply enhancements
    enhanced = normalize_image(img)
    
    # Slight sharpening
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    enhanced = cv2.filter2D(enhanced, -1, kernel * 0.5)
    
    # Save
    if output_path is None:
        output_path = str(Path(image_path).with_suffix('.enhanced.jpg'))
    
    cv2.imwrite(output_path, enhanced)
    return output_path

def create_thumbnail(image_path: str, size: tuple = (256, 256)) -> bytes:
    """
    Create thumbnail of image
    
    Args:
        image_path: Path to image
        size: Thumbnail size (width, height)
        
    Returns:
        Thumbnail as bytes
    """
    img = Image.open(image_path)
    img.thumbnail(size, Image.Resampling.LANCZOS)
    
    # Convert to bytes
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='JPEG', quality=85)
    byte_arr.seek(0)
    
    return byte_arr.getvalue()

def calculate_image_hash(image_path: str) -> str:
    """
    Calculate perceptual hash of image for duplicate detection
    """
    import hashlib
    
    # Read image
    img = cv2.imread(image_path)
    
    # Resize to small size
    img_small = cv2.resize(img, (8, 8), interpolation=cv2.INTER_AREA)
    
    # Convert to grayscale
    img_gray = cv2.cvtColor(img_small, cv2.COLOR_BGR2GRAY)
    
    # Calculate hash
    img_hash = hashlib.md5(img_gray.tobytes()).hexdigest()
    
    return img_hash

def validate_image_file(file_path: str) -> tuple:
    """
    Validate if file is a valid image
    
    Returns:
        (is_valid, error_message)
    """
    try:
        img = cv2.imread(file_path)
        if img is None:
            return False, "Failed to read image file"
        
        height, width = img.shape[:2]
        if height < 100 or width < 100:
            return False, "Image dimensions too small"
        
        return True, None
    except Exception as e:
        return False, f"Image validation error: {str(e)}"

def get_image_metadata(image_path: str) -> dict:
    """
    Extract image metadata
    """
    img = cv2.imread(image_path)
    
    if img is None:
        return {"error": "Failed to load image"}
    
    height, width, channels = img.shape
    file_size = Path(image_path).stat().st_size
    
    return {
        "width": width,
        "height": height,
        "channels": channels,
        "aspect_ratio": round(width / height, 2),
        "megapixels": round((width * height) / 1_000_000, 2),
        "file_size_bytes": file_size,
        "file_size_mb": round(file_size / (1024 * 1024), 2)
    }