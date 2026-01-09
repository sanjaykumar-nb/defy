"""
V-Inference Backend - Main Application
Decentralized AI Inference Network with ZKML Verification
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import models, inference, marketplace, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 V-Inference Backend Starting...")
    print("📦 Initializing storage...")
    print("⚡ ZKML Simulator ready")
    
    # Seed demo data for presentation
    from app.core.database import db
    from app.core.demo_data import seed_demo_data
    seed_demo_data(db)
    
    print("✅ Backend ready to accept connections")
    yield
    # Shutdown
    print("👋 V-Inference Backend shutting down...")


app = FastAPI(
    title="V-Inference API",
    description="""
    ## Decentralized AI Inference Network with ZKML Verification
    
    V-Inference enables verifiable AI inference on a decentralized network.
    
    ### Features:
    - **Model Management**: Upload, store, and manage AI models
    - **Inference Execution**: Run model inference with ZK proof generation
    - **Marketplace**: List models for others to use, purchase inference credits
    - **ZKML Verification**: Zero-Knowledge proofs ensure correct execution
    
    ### Tech Stack:
    - FastAPI backend
    - EZKL-simulated ZKML proof generation
    - JSON-based storage (simulating Supabase)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api")
app.include_router(models.router, prefix="/api")
app.include_router(inference.router, prefix="/api")
app.include_router(marketplace.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "V-Inference API",
        "version": "1.0.0",
        "description": "Decentralized AI Inference Network with ZKML Verification",
        "docs": "/docs",
        "status": "online",
        "endpoints": {
            "users": "/api/users",
            "models": "/api/models",
            "inference": "/api/inference",
            "marketplace": "/api/marketplace"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "v-inference-backend",
        "version": "1.0.0"
    }


@app.get("/api/stats")
async def get_platform_stats():
    """Get platform-wide statistics"""
    from app.core.database import db
    
    users = db._read_file(db.users_file)
    models = db._read_file(db.models_file)
    jobs = db._read_file(db.jobs_file)
    listings = db.get_active_listings()
    
    completed_jobs = [j for j in jobs if j.get("status") == "completed"]
    verified_jobs = [j for j in jobs if j.get("status") == "verified" or j.get("proof_hash")]
    
    return {
        "platform": "V-Inference",
        "stats": {
            "total_users": len(users),
            "total_models": len(models),
            "total_inferences": len(jobs),
            "completed_inferences": len(completed_jobs),
            "verified_inferences": len(verified_jobs),
            "active_listings": len(listings),
            "verification_rate": round(len(verified_jobs) / max(len(completed_jobs), 1) * 100, 2)
        },
        "network": {
            "chain": "Base Sepolia",
            "verifier_contract": "0x742d35Cc6634C0532925a3b844Bc9e7595f00000",
            "escrow_contract": "0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
