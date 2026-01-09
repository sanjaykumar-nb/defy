"""
V-Inference Backend - Inference API
Endpoints for running AI inference with ZKML verification and Sepolia anchoring
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from datetime import datetime

from ..core.database import db
from ..models.schemas import InferenceInput, InferenceJob, JobStatus, APIResponse
from ..services.zkml_simulator import inference_engine

router = APIRouter(prefix="/inference", tags=["Inference"])


@router.post("/run", response_model=APIResponse)
async def run_inference(request: InferenceInput):
    """
    Run inference on a model with optional ZKML proof generation.
    
    The inference flow:
    1. Validate model exists and user has access
    2. Execute model inference
    3. Generate ZK proof (if enabled)
    4. Anchor proof on Sepolia (if ZKML enabled)
    5. Verify proof
    6. Return results with TX hash
    """
    try:
        # Validate model exists
        model = db.get_model(request.model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Create job record
        job_data = {
            "model_id": request.model_id,
            "user_id": "demo_user",  # In production, get from auth
            "input_data": request.input_data,
            "use_zkml": request.use_zkml
        }
        job = db.create_job(job_data)
        
        # Update job status to processing
        db.update_job(job['id'], {"status": "processing"})
        
        # DEMO MODE: Check if using broken demo model OR simulate_failure toggle
        is_broken_model = (
            request.model_id == "model-broken-demo" or 
            model.get("metadata", {}).get("always_fails", False)
        )
        
        # DEMO MODE: Simulate failure if requested OR if using broken model
        if request.simulate_failure or is_broken_model:
            # Return failed verification result
            update_data = {
                "status": "failed",
                "output_data": {
                    "error": "Verification Failed",
                    "reason": "ZK proof validation failed - computation integrity check failed",
                    "suggestion": "Model produced incorrect output. Escrow will be refunded.",
                    "simulated_failure": True
                },
                "completed_at": datetime.utcnow().isoformat(),
                "verification_status": "failed"
            }
            db.update_job(job['id'], update_data)
            
            return APIResponse(
                success=True,
                message="Inference failed verification (demo mode)",
                data={
                    "job_id": job['id'],
                    "model_id": request.model_id,
                    "output": update_data["output_data"],
                    "inference_time_ms": 0,
                    "total_time_ms": 100,
                    "zkml": {
                        "enabled": True,
                        "proof": {
                            "proof_hash": "0x0000...FAILED",
                            "circuit_hash": "0x0000...INVALID"
                        },
                        "verification": {
                            "is_valid": False,
                            "message": "❌ NOT VERIFIED - Computation failed integrity check",
                            "gas_estimate": {"cost_usd": 0, "chain": "Sepolia"}
                        }
                    }
                }
            )
        
        # Run inference with job_id for on-chain anchoring
        result = inference_engine.run_inference(
            job_id=job['id'],  # Pass job_id for on-chain anchoring
            model_id=request.model_id,
            model_type=model.get("model_type", "classification"),
            input_data=request.input_data,
            use_zkml=request.use_zkml,
            anchor_on_chain=request.use_zkml  # Anchor if ZKML enabled
        )
        
        # Update job with results
        update_data = {
            "status": "completed",
            "output_data": result["output_data"],
            "completed_at": datetime.utcnow().isoformat(),
            "latency_ms": result["total_time_ms"]
        }
        
        if request.use_zkml and "proof" in result:
            update_data["proof_hash"] = result["proof"]["proof_hash"]
            update_data["verification_status"] = result["verification"]["message"]
            
            # Store on-chain info if available
            if result["proof"].get("on_chain", {}).get("anchored"):
                update_data["transaction_hash"] = result["proof"]["on_chain"]["transaction_hash"]
                update_data["block_number"] = result["proof"]["on_chain"]["block_number"]
            
            # Store proof in database
            proof_data = {
                "job_id": job['id'],
                **result["proof"]
            }
            db.create_proof(proof_data)
        
        db.update_job(job['id'], update_data)
        
        # Update model statistics
        current_inferences = model.get("total_inferences", 0) + 1
        current_avg_latency = model.get("average_latency_ms", 0)
        new_avg_latency = (current_avg_latency * (current_inferences - 1) + result["total_time_ms"]) / current_inferences
        
        db.update_model(request.model_id, {
            "total_inferences": current_inferences,
            "average_latency_ms": round(new_avg_latency, 2)
        })
        
        return APIResponse(
            success=True,
            message="Inference completed successfully",
            data={
                "job_id": job['id'],
                "model_id": request.model_id,
                "output": result["output_data"],
                "inference_time_ms": result["inference_time_ms"],
                "total_time_ms": result["total_time_ms"],
                "zkml": {
                    "enabled": request.use_zkml,
                    "proof": result.get("proof"),
                    "verification": result.get("verification")
                } if request.use_zkml else None
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Update job as failed
        if 'job' in locals():
            db.update_job(job['id'], {
                "status": "failed",
                "completed_at": datetime.utcnow().isoformat()
            })
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/job/{job_id}", response_model=APIResponse)
async def get_job(job_id: str):
    """
    Get the status and results of an inference job.
    """
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get proof if exists
    proof = db.get_proof_by_job(job_id)
    
    return APIResponse(
        success=True,
        message="Job retrieved successfully",
        data={
            **job,
            "proof": proof
        }
    )


@router.get("/jobs", response_model=APIResponse)
async def list_jobs(user_id: str = None, model_id: str = None, limit: int = 50):
    """
    List inference jobs with optional filters.
    """
    all_jobs = db._read_file(db.jobs_file)
    
    # Apply filters
    if user_id:
        all_jobs = [j for j in all_jobs if j.get("user_id") == user_id]
    if model_id:
        all_jobs = [j for j in all_jobs if j.get("model_id") == model_id]
    
    # Sort by created_at descending and limit
    all_jobs = sorted(all_jobs, key=lambda x: x.get("created_at", ""), reverse=True)[:limit]
    
    return APIResponse(
        success=True,
        message=f"Found {len(all_jobs)} jobs",
        data=all_jobs
    )


@router.post("/verify-proof/{job_id}", response_model=APIResponse)
async def verify_proof(job_id: str):
    """
    Verify the ZK proof for a completed inference job.
    Checks on-chain verification if proof was anchored on Sepolia.
    """
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    proof = db.get_proof_by_job(job_id)
    if not proof:
        raise HTTPException(status_code=404, detail="No proof found for this job")
    
    # Run verification (includes on-chain check)
    is_valid, message, verification_details = inference_engine.zkml.verify_proof(proof)
    gas_estimate = inference_engine.zkml.estimate_gas_cost()
    
    # Update job status
    db.update_job(job_id, {
        "status": "verified" if is_valid else "failed",
        "verification_status": message
    })
    
    # Get on-chain info
    on_chain_info = proof.get("on_chain", {})
    
    return APIResponse(
        success=True,
        message=message,
        data={
            "job_id": job_id,
            "is_valid": is_valid,
            "proof_hash": proof.get("proof_hash"),
            "verification_message": message,
            "verification_details": verification_details,
            "gas_estimate": gas_estimate,
            "on_chain": {
                "anchored": on_chain_info.get("anchored", False),
                "chain": "Sepolia",
                "chain_id": 11155111,
                "contract_address": on_chain_info.get("contract_address"),
                "transaction_hash": on_chain_info.get("transaction_hash"),
                "block_number": on_chain_info.get("block_number"),
                "explorer_url": on_chain_info.get("explorer_url")
            }
        }
    )


@router.get("/blockchain-status", response_model=APIResponse)
async def get_blockchain_status():
    """
    Get Sepolia blockchain connection status.
    """
    status = inference_engine.zkml.get_network_status()
    
    return APIResponse(
        success=True,
        message="Blockchain status retrieved",
        data=status
    )


@router.get("/sample-inputs", response_model=APIResponse)
async def get_sample_inputs():
    """
    Get sample input data for testing different model types.
    """
    samples = {
        "classification": {
            "description": "Image classification input (MNIST compatible)",
            "input": {
                "features": [
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.9, 0.9, 0.9, 0.9, 0.9, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.9, 0.9, 0.99, 0.9, 0.9, 0.9, 0.9, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.5, 0.5, 0.5, 0.5, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.9, 0.9, 0.5, 0.0, 0.0, 0.5, 0.9, 0.9, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.9, 0.5, 0.5, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
                ]
            }
        },
        "regression": {
            "description": "Regression model input",
            "input": {
                "features": [0.5, 0.3, 0.8, 0.2, 0.9],
                "normalize": True
            }
        },
        "nlp": {
            "description": "NLP/Text model input",
            "input": {
                "text": "This is a sample text for sentiment analysis.",
                "max_length": 512,
                "return_embeddings": False
            }
        },
        "embedding": {
            "description": "Embedding model input",
            "input": {
                "text": "Generate embedding for this text",
                "pooling": "mean"
            }
        }
    }
    
    return APIResponse(
        success=True,
        message="Sample inputs for different model types",
        data=samples
    )
