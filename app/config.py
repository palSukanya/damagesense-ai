import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "DamageSense AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads" / "raw"
    ANNOTATED_DIR: Path = BASE_DIR / "uploads" / "annotated"
    MODEL_DIR: Path = BASE_DIR.parent / "models"
    TEMPLATE_DIR: Path = BASE_DIR.parent / "templates"
    
    # Model Settings
    MODEL_PATH: str = str(MODEL_DIR / "best.pt")
    CONFIDENCE_THRESHOLD: float = 0.25
    IOU_THRESHOLD: float = 0.45
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./damagesense.db"
    # For PostgreSQL: "postgresql://user:password@localhost/damagesense"
    
    # Damage Classification
    DAMAGE_CLASSES: dict = {
        0: "scratch",
        1: "dent",
        2: "crack",
        3: "broken_part",
        4: "paint_damage",
        5: "glass_damage"
    }
    
    # Severity Thresholds (based on area percentage)
    SEVERITY_LOW_THRESHOLD: float = 5.0      # < 5% = Low
    SEVERITY_MEDIUM_THRESHOLD: float = 15.0  # 5-15% = Medium, >15% = High
    
    # Image Quality Thresholds
    MIN_RESOLUTION: tuple = (640, 480)
    BLUR_THRESHOLD: float = 100.0  # Laplacian variance
    BRIGHTNESS_MIN: float = 50.0
    BRIGHTNESS_MAX: float = 200.0
    
    # Business Rules
    AUTO_APPROVE_THRESHOLD: float = 50000.0  # Auto-approve claims below this amount (INR)
    SAFETY_CRITICAL_PARTS: list = ["headlight", "brake", "tire", "windshield"]
    
    # API Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png"}
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)
settings.MODEL_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)