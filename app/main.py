from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid
from datetime import datetime

from app.config import settings
from app.database.db import get_db, init_db
from app.models.yolo_model import damage_model
from app.services.detection_service import DetectionService
from app.services.image_quality_service import ImageQualityService
from app.services.history_service import HistoryService
from app.utils.overlay_utils import VehicleCanonicalMapper
from app.utils.image_utils import validate_image_file, get_image_metadata

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered vehicle damage detection and intelligent assessment system"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving images
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR.parent)), name="uploads")

# Initialize detection service
detection_service = DetectionService()

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("🚀 Starting DamageSense AI...")
    print(f"📁 Upload directory: {settings.UPLOAD_DIR}")
    print(f"📁 Model directory: {settings.MODEL_DIR}")
    
    # Load model
    print("🔧 Loading damage detection model...")
    damage_model.load_model()
    print("✅ Model loaded successfully")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} is ready!")

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "analyze": "/api/v1/analyze",
            "history": "/api/v1/history/{vehicle_id}",
            "quality_check": "/api/v1/quality-check",
            "model_info": "/api/v1/model/info"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_status = damage_model.get_model_info()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model": model_status,
        "database": "connected"
    }

@app.post("/api/v1/analyze")
async def analyze_damage(
    image: UploadFile = File(..., description="Vehicle image to analyze"),
    vehicle_id: str = Form(..., description="Vehicle identifier (registration number or VIN)"),
    inspection_type: str = Form("general", description="Type of inspection: claim, intake, service, resale"),
    check_history: bool = Form(True, description="Compare with historical data"),
    db: Session = Depends(get_db)
):
    """
    Main endpoint for vehicle damage analysis
    
    Performs:
    1. Image quality assessment
    2. Damage detection
    3. Severity scoring
    4. Historical comparison (optional)
    5. Business recommendations
    
    Returns comprehensive inspection report
    """
    print(f"\n{'='*60}")
    print(f"📋 New inspection request for vehicle: {vehicle_id}")
    print(f"{'='*60}")
    
    # Validate file extension
    file_ext = Path(image.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Save uploaded file
    file_id = uuid.uuid4().hex[:8]
    filename = f"{vehicle_id}_{file_id}{file_ext}"
    file_path = settings.UPLOAD_DIR / filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        print(f"📁 Saved image: {filename}")
        
        # Validate image
        is_valid, error_msg = validate_image_file(str(file_path))
        if not is_valid:
            file_path.unlink()  # Delete invalid file
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Process inspection
        report = detection_service.process_inspection(
            image_path=str(file_path),
            vehicle_id=vehicle_id,
            inspection_type=inspection_type,
            db=db
        )
        
        # If rejected due to quality, return early
        if report.get("status") == "rejected":
            return JSONResponse(
                status_code=400,
                content=report
            )
        
        # Historical comparison if requested
        if check_history and report.get("status") == "complete":
            detections = report.get("detections", [])
            if detections:
                history_result = HistoryService.compare_with_history(
                    vehicle_id=vehicle_id,
                    current_detections=detections,
                    db=db
                )
                report["historical_comparison"] = history_result
        
        # Generate canonical damage map if damages detected
        if report.get("damages_detected", 0) > 0:
            map_filename = f"{vehicle_id}_{file_id}_damage_map.jpg"
            map_path = settings.ANNOTATED_DIR / map_filename
            
            VehicleCanonicalMapper.create_comprehensive_damage_map(
                detections=report["detections"],
                output_path=str(map_path)
            )
            report["damage_map"] = f"/uploads/annotated/{map_filename}"
        
        # Convert file paths to URLs
        report["original_image_url"] = f"/uploads/raw/{filename}"
        if "annotated_image" in report:
            annotated_filename = Path(report["annotated_image"]).name
            report["annotated_image_url"] = f"/uploads/annotated/{annotated_filename}"
        
        print(f"✅ Analysis complete for {vehicle_id}")
        print(f"   Damages found: {report.get('damages_detected', 0)}")
        print(f"   Overall severity: {report.get('overall_assessment', {}).get('overall_severity', 'N/A')}")
        print(f"{'='*60}\n")
        
        return JSONResponse(content=report)
        
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        
        print(f"❌ Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/v1/quality-check")
async def check_image_quality(
    image: UploadFile = File(..., description="Image to check quality")
):
    """
    Check image quality before processing
    
    Returns quality metrics and recommendations
    """
    # Save temporary file
    temp_id = uuid.uuid4().hex[:8]
    file_ext = Path(image.filename).suffix.lower()
    temp_path = settings.UPLOAD_DIR / f"temp_{temp_id}{file_ext}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Assess quality
        quality_result = ImageQualityService.assess_quality(str(temp_path))
        
        # Get image metadata
        metadata = get_image_metadata(str(temp_path))
        
        # Clean up
        temp_path.unlink()
        
        return {
            "quality_assessment": quality_result,
            "image_metadata": metadata
        }
        
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/history/{vehicle_id}")
async def get_vehicle_history(
    vehicle_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get inspection history for a vehicle
    
    Args:
        vehicle_id: Vehicle identifier
        limit: Maximum number of records to return
    """
    history = detection_service.get_inspection_history(
        vehicle_id=vehicle_id,
        db=db,
        limit=limit
    )
    
    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"No inspection history found for vehicle {vehicle_id}"
        )
    
    return {
        "vehicle_id": vehicle_id,
        "total_inspections": len(history),
        "history": history
    }

@app.get("/api/v1/damage-timeline/{vehicle_id}")
async def get_damage_timeline(
    vehicle_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete damage timeline showing damage evolution
    """
    timeline = HistoryService.get_vehicle_damage_timeline(vehicle_id, db)
    
    if not timeline:
        raise HTTPException(
            status_code=404,
            detail=f"No timeline found for vehicle {vehicle_id}"
        )
    
    return {
        "vehicle_id": vehicle_id,
        "timeline": timeline
    }

@app.get("/api/v1/damage-evolution/{vehicle_id}")
async def get_damage_evolution(
    vehicle_id: str,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive damage evolution report
    """
    report = HistoryService.generate_damage_evolution_report(vehicle_id, db)
    
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    
    return report

@app.get("/api/v1/model/info")
async def get_model_info():
    """Get information about the loaded model"""
    return damage_model.get_model_info()

@app.get("/api/v1/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get overall system statistics"""
    from app.database.schemas import Inspection, Vehicle, Damage
    
    total_vehicles = db.query(Vehicle).count()
    total_inspections = db.query(Inspection).count()
    total_damages = db.query(Damage).count()
    
    # Severity distribution
    severity_dist = {}
    for severity in ["low", "medium", "high", "critical"]:
        count = db.query(Inspection).filter(
            Inspection.overall_severity == severity
        ).count()
        severity_dist[severity] = count
    
    return {
        "total_vehicles_inspected": total_vehicles,
        "total_inspections": total_inspections,
        "total_damages_detected": total_damages,
        "severity_distribution": severity_dist,
        "avg_damages_per_inspection": round(total_damages / max(total_inspections, 1), 2)
    }

@app.get("/api/v1/image/{inspection_id}/{image_type}")
async def get_inspection_image(
    inspection_id: str,
    image_type: str,  # 'original' or 'annotated'
    db: Session = Depends(get_db)
):
    """Get image from a specific inspection"""
    from app.database.schemas import Inspection
    
    inspection = db.query(Inspection).filter(
        Inspection.inspection_id == inspection_id
    ).first()
    
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    if image_type == "original":
        image_path = inspection.image_path
    elif image_type == "annotated":
        image_path = inspection.annotated_image_path
    else:
        raise HTTPException(status_code=400, detail="Invalid image type")
    
    if not image_path or not Path(image_path).exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_path)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Resource not found", "detail": str(exc)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )