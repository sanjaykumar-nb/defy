from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime

router = APIRouter(tags=["workers"])

from app.core.database import db

# Persistent storage via database.py
# workers_metadata is still used as a cache for performance if needed, 
# but for simplicity we'll use db directly.

class HardwareInfo(BaseModel):
    cpu_cores: int
    total_ram_gb: float
    os: str
    privacy_support: str
    zk_capable: bool

class WorkerRegistration(BaseModel):
    node_id: str
    wallet_address: str
    public_url: str
    hardware_info: HardwareInfo

class WorkerStatus(BaseModel):
    node_id: str
    public_url: str
    status: str
    last_seen: str
    hardware_info: HardwareInfo
    is_live: bool

@router.post("/workers/register")
async def register_worker(registration: WorkerRegistration, background_tasks: BackgroundTasks):
    node_id = registration.node_id
    
    # Persist to database
    worker_data = registration.dict()
    worker_data["last_seen"] = datetime.now().isoformat()
    worker_data["is_live"] = False
    
    # Store in database
    workers = db._read_file(db.workers_file)
    # Update existing or append new
    updated = False
    for i, w in enumerate(workers):
        if w.get("node_id") == node_id:
            workers[i].update(worker_data)
            updated = True
            break
    if not updated:
        workers.append(worker_data)
    db._write_file(db.workers_file, workers)
    
    # Run immediate verification
    background_tasks.add_task(verify_worker_liveness, node_id)
    
    return {"message": "Registration received", "node_id": node_id}

@router.get("/workers", response_model=List[WorkerStatus])
async def list_workers():
    """List all registered workers and their current live status"""
    workers = db._read_file(db.workers_file)
    return [
        WorkerStatus(
            node_id=w["node_id"],
            public_url=w["public_url"],
            status="active" if w.get("is_live", False) else "offline",
            last_seen=w.get("last_seen", datetime.now().isoformat()),
            hardware_info=w["hardware_info"],
            is_live=w.get("is_live", False)
        )
        for w in workers
    ]

@router.get("/workers/{node_id}/verify")
async def manual_verify_worker(node_id: str):
    """Manually trigger a liveness check for a specific worker"""
    workers = db._read_file(db.workers_file)
    worker = next((w for w in workers if w["node_id"] == node_id), None)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    is_live = await verify_worker_liveness(node_id)
    return {"node_id": node_id, "is_live": is_live}

async def verify_worker_liveness(node_id: str) -> bool:
    """Check a worker's /health endpoint to verify it's reachable and active"""
    workers = db._read_file(db.workers_file)
    worker = next((w for w in workers if w["node_id"] == node_id), None)
    
    if not worker:
        return False
        
    public_url = worker["public_url"].rstrip("/")
    if not public_url.startswith("http"):
        public_url = f"http://{public_url}"
    
    try:
        # Pinging the worker's health endpoint
        response = requests.get(f"{public_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("node_id") == node_id:
                # Fetch capabilities too
                cap_res = requests.get(f"{public_url}/capabilities", timeout=5)
                capabilities = cap_res.json() if cap_res.status_code == 200 else {}
                
                # Update status in DB
                for w in workers:
                    if w["node_id"] == node_id:
                        w["is_live"] = True
                        w["last_seen"] = datetime.now().isoformat()
                        if capabilities:
                            w["hardware_info"] = capabilities
                        break
                db._write_file(db.workers_file, workers)
                return True
    except Exception as e:
        print(f"WARN [BACKEND] Verification failed for worker {node_id} at {public_url}: {e}")
        
    return False
