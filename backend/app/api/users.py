"""
V-Inference Backend - Users API
Endpoints for user management and wallet connection
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from ..core.database import db
from ..models.schemas import User, UserCreate, APIResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/connect", response_model=APIResponse)
async def connect_wallet(wallet_address: str, username: Optional[str] = None):
    """
    Connect a wallet and create/retrieve user profile.
    This simulates wallet authentication for demo purposes.
    """
    try:
        # Check if user exists
        user = db.get_user_by_wallet(wallet_address)
        
        if user:
            # Update username if provided
            if username and username != user.get("username"):
                users = db._read_file(db.users_file)
                for u in users:
                    if u["id"] == user["id"]:
                        u["username"] = username
                        break
                db._write_file(db.users_file, users)
                user["username"] = username
            
            return APIResponse(
                success=True,
                message="Welcome back!",
                data=user
            )
        
        # Create new user
        user_data = {
            "wallet_address": wallet_address,
            "username": username or f"User_{wallet_address[:8]}"
        }
        user = db.create_user(user_data)
        
        return APIResponse(
            success=True,
            message="Wallet connected successfully",
            data=user
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=APIResponse)
async def get_user(user_id: str):
    """
    Get user profile by ID.
    """
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return APIResponse(
        success=True,
        message="User retrieved",
        data=user
    )


@router.get("/wallet/{wallet_address}", response_model=APIResponse)
async def get_user_by_wallet(wallet_address: str):
    """
    Get user profile by wallet address.
    """
    user = db.get_user_by_wallet(wallet_address)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return APIResponse(
        success=True,
        message="User retrieved",
        data=user
    )


@router.get("/{user_id}/dashboard", response_model=APIResponse)
async def get_user_dashboard(user_id: str):
    """
    Get comprehensive dashboard data for a user.
    """
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's models
    models = db.get_user_models(user_id)
    
    # Get user's jobs
    jobs = db.get_user_jobs(user_id)
    
    # Get user's purchases
    purchases = db.get_user_purchases(user_id)
    
    # Get user's listings
    all_listings = db.get_active_listings()
    my_listings = [l for l in all_listings if l.get("owner_id") == user_id]
    
    # Calculate stats
    total_inferences = sum(m.get("total_inferences", 0) for m in models)
    total_revenue = sum(l.get("total_revenue", 0) for l in my_listings)
    total_spent = sum(p.get("total_paid", 0) for p in purchases)
    
    completed_jobs = [j for j in jobs if j.get("status") == "completed"]
    avg_latency = 0
    if completed_jobs:
        avg_latency = sum(j.get("latency_ms", 0) for j in completed_jobs) / len(completed_jobs)
    
    dashboard = {
        "user": user,
        "stats": {
            "total_models": len(models),
            "total_inferences": total_inferences,
            "total_listings": len(my_listings),
            "total_purchases": len(purchases),
            "total_revenue": round(total_revenue, 2),
            "total_spent": round(total_spent, 2),
            "average_latency_ms": round(avg_latency, 2),
            "balance": user.get("balance", 0)
        },
        "recent_models": models[:5],
        "recent_jobs": sorted(jobs, key=lambda x: x.get("created_at", ""), reverse=True)[:5],
        "active_listings": my_listings,
        "active_purchases": [p for p in purchases if p.get("inferences_remaining", 0) > 0]
    }
    
    return APIResponse(
        success=True,
        message="Dashboard data retrieved",
        data=dashboard
    )


@router.post("/{user_id}/add-funds", response_model=APIResponse)
async def add_funds(user_id: str, amount: float):
    """
    Add demo funds to user balance.
    In production, this would integrate with actual payment/crypto wallet.
    """
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_balance = user.get("balance", 0) + amount
    db.update_user_balance(user_id, new_balance)
    
    return APIResponse(
        success=True,
        message=f"Added ${amount} to balance",
        data={"new_balance": new_balance}
    )
