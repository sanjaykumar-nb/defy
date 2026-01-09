"""
V-Inference Backend - Models API
Endpoints for AI model upload, management, and retrieval
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List
import os
import shutil
from pathlib import Path

from ..core.database import db
from ..models.schemas import AIModel, AIModelCreate, APIResponse

router = APIRouter(prefix="/models", tags=["Models"])

# Storage path for uploaded models
MODELS_STORAGE_PATH = Path("storage/models")
MODELS_STORAGE_PATH.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=APIResponse)
async def upload_model(
    name: str = Form(...),
    description: str = Form(""),
    model_type: str = Form("onnx"),
    is_public: bool = Form(False),
    owner_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload a new AI model to the platform.
    Supports ONNX, PyTorch, and TensorFlow model files.
    """
    try:
        # Validate file extension
        allowed_extensions = [".onnx", ".pt", ".pth", ".h5", ".pb", ".tflite", ".pkl"]
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Create model record first to get ID
        model_data = {
            "name": name,
            "description": description,
            "model_type": model_type,
            "is_public": is_public,
            "owner_id": owner_id,
            "metadata": {
                "original_filename": file.filename,
                "file_size": 0,
                "file_extension": file_ext
            }
        }
        
        model = db.create_model(model_data)
        
        # Save file with model ID
        file_path = MODELS_STORAGE_PATH / f"{model['id']}{file_ext}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update model with file path and size
        file_size = os.path.getsize(file_path)
        db.update_model(model['id'], {
            "file_path": str(file_path),
            "metadata": {
                **model['metadata'],
                "file_size": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2)
            }
        })
        
        model = db.get_model(model['id'])
        
        return APIResponse(
            success=True,
            message="Model uploaded successfully",
            data=model
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=APIResponse)
async def list_models(owner_id: Optional[str] = None):
    """
    List all models, optionally filtered by owner.
    """
    try:
        if owner_id:
            models = db.get_user_models(owner_id)
        else:
            models = db.get_all_models()
        
        return APIResponse(
            success=True,
            message=f"Found {len(models)} models",
            data=models
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_id}", response_model=APIResponse)
async def get_model(model_id: str):
    """
    Get details of a specific model.
    """
    model = db.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return APIResponse(
        success=True,
        message="Model retrieved successfully",
        data=model
    )


@router.put("/{model_id}", response_model=APIResponse)
async def update_model(
    model_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    is_public: Optional[bool] = None
):
    """
    Update model details.
    """
    model = db.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    updates = {}
    if name is not None:
        updates["name"] = name
    if description is not None:
        updates["description"] = description
    if is_public is not None:
        updates["is_public"] = is_public
    
    if updates:
        model = db.update_model(model_id, updates)
    
    return APIResponse(
        success=True,
        message="Model updated successfully",
        data=model
    )


@router.delete("/{model_id}", response_model=APIResponse)
async def delete_model(model_id: str, owner_id: str):
    """
    Delete a model. Only the owner can delete their models.
    """
    model = db.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if model.get("owner_id") != owner_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this model")
    
    # Delete the file if it exists
    if model.get("file_path") and os.path.exists(model["file_path"]):
        os.remove(model["file_path"])
    
    db.delete_model(model_id)
    
    return APIResponse(
        success=True,
        message="Model deleted successfully",
        data=None
    )


@router.get("/{model_id}/stats", response_model=APIResponse)
async def get_model_stats(model_id: str):
    """
    Get usage statistics for a model.
    """
    model = db.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Get all jobs for this model
    all_jobs = db._read_file(db.jobs_file)
    model_jobs = [j for j in all_jobs if j.get("model_id") == model_id]
    
    completed_jobs = [j for j in model_jobs if j.get("status") == "completed"]
    avg_latency = 0
    if completed_jobs:
        latencies = [j.get("latency_ms", 0) for j in completed_jobs]
        avg_latency = sum(latencies) / len(latencies)
    
    stats = {
        "model_id": model_id,
        "total_inferences": len(model_jobs),
        "successful_inferences": len(completed_jobs),
        "failed_inferences": len([j for j in model_jobs if j.get("status") == "failed"]),
        "average_latency_ms": round(avg_latency, 2),
        "success_rate": round(len(completed_jobs) / max(len(model_jobs), 1) * 100, 2)
    }
    
    return APIResponse(
        success=True,
        message="Model statistics retrieved",
        data=stats
    )
