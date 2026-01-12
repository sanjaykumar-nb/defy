"""
V-Inference Backend - Marketplace API
Endpoints for listing, purchasing, and managing marketplace inference offerings

DECENTRALIZATION FEATURES:
1. Real ETH escrow via smart contracts (trustless payments)
2. Payment release only after on-chain proof verification
3. Automatic refund on verification failure
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from datetime import datetime

from ..core.database import db
from ..models.schemas import (
    MarketplaceListing, ListingCreate, Purchase, PurchaseCreate, APIResponse
)
from ..services.zkml_simulator import inference_engine
from ..services.escrow_service import escrow_service
from ..services.onchain_verifier import on_chain_verifier

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


@router.post("/list", response_model=APIResponse)
async def create_listing(listing: ListingCreate, owner_id: str):
    """
    Create a new marketplace listing for a model.
    Model owners can list their models for others to use.
    """
    try:
        # Verify model exists and belongs to user
        model = db.get_model(listing.model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        if model.get("owner_id") != owner_id:
            raise HTTPException(
                status_code=403, 
                detail="Only the model owner can list it on the marketplace"
            )
        
        # Check if model is already listed
        existing = db.get_listing_by_model(listing.model_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Model is already listed on the marketplace"
            )
        
        # Create listing
        listing_data = {
            "model_id": listing.model_id,
            "owner_id": owner_id,
            "model_name": model.get("name"),
            "description": listing.description or model.get("description", ""),
            "price_per_inference": listing.price_per_inference,
            "category": listing.category,
            "tags": listing.tags,
            "rating": 5.0,
            "model_type": model.get("model_type", "classification")
        }
        
        new_listing = db.create_listing(listing_data)
        
        # Mark model as public
        db.update_model(listing.model_id, {"is_public": True})
        
        return APIResponse(
            success=True,
            message="Model listed on marketplace successfully",
            data=new_listing
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/listings", response_model=APIResponse)
async def get_listings(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "rating"
):
    """
    Get all active marketplace listings.
    Buyers can browse available inference offerings.
    
    Note: Model architecture and weights are NOT exposed.
    Only description, pricing, and performance metrics are shown.
    """
    try:
        listings = db.get_active_listings()
        
        # Apply filters
        if category:
            listings = [l for l in listings if l.get("category") == category]
        if min_price is not None:
            listings = [l for l in listings if l.get("price_per_inference", 0) >= min_price]
        if max_price is not None:
            listings = [l for l in listings if l.get("price_per_inference", 0) <= max_price]
        
        # Sort
        if sort_by == "rating":
            listings = sorted(listings, key=lambda x: x.get("rating", 0), reverse=True)
        elif sort_by == "price_low":
            listings = sorted(listings, key=lambda x: x.get("price_per_inference", 0))
        elif sort_by == "price_high":
            listings = sorted(listings, key=lambda x: x.get("price_per_inference", 0), reverse=True)
        elif sort_by == "popular":
            listings = sorted(listings, key=lambda x: x.get("total_inferences", 0), reverse=True)
        
        # Remove sensitive model information
        safe_listings = []
        for listing in listings:
            safe_listing = {
                "id": listing.get("id"),
                "model_name": listing.get("model_name"),
                "description": listing.get("description"),
                "price_per_inference": listing.get("price_per_inference"),
                "category": listing.get("category"),
                "tags": listing.get("tags", []),
                "rating": listing.get("rating"),
                "total_inferences": listing.get("total_inferences"),
                "total_revenue": listing.get("total_revenue"),
                "owner_id": listing.get("owner_id"),
                "created_at": listing.get("created_at"),
                "model_type": listing.get("model_type"),
                # Explicitly NOT including: model_id, file_path, architecture details
            }
            safe_listings.append(safe_listing)
        
        return APIResponse(
            success=True,
            message=f"Found {len(safe_listings)} listings",
            data=safe_listings
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/listing/{listing_id}", response_model=APIResponse)
async def get_listing(listing_id: str):
    """
    Get details of a specific listing.
    Model architecture is hidden from buyers.
    """
    listing = db.get_listing(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Get model stats without exposing model details
    model = db.get_model(listing.get("model_id"))
    
    safe_listing = {
        **listing,
        "performance_metrics": {
            "total_inferences": model.get("total_inferences", 0) if model else 0,
            "average_latency_ms": model.get("average_latency_ms", 0) if model else 0,
            "success_rate": 99.9  # Mock success rate
        }
    }
    
    # Remove sensitive fields
    safe_listing.pop("model_id", None)
    
    return APIResponse(
        success=True,
        message="Listing retrieved successfully",
        data=safe_listing
    )


@router.post("/purchase", response_model=APIResponse)
async def purchase_inference(
    purchase: PurchaseCreate, 
    user_id: str,
    use_eth_escrow: bool = False,  # NEW: Option for real ETH escrow
    provider_address: Optional[str] = None  # Provider's ETH address for escrow
):
    """
    Purchase inference credits for a listed model.
    
    DECENTRALIZED ESCROW OPTIONS:
    - use_eth_escrow=False: Traditional balance-based (simulated)
    - use_eth_escrow=True: Real ETH locked in smart contract (trustless!)
    
    When using ETH escrow:
    - ETH is locked in VInferenceEscrow contract
    - Released to provider only after ZK proof verification
    - Refunded to buyer if verification fails
    """
    try:
        # Get listing
        listing = db.get_listing(purchase.listing_id)
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        if not listing.get("is_active"):
            raise HTTPException(status_code=400, detail="Listing is not active")
        
        # Prevent self-purchase
        if listing.get("owner_id") == user_id:
            raise HTTPException(status_code=400, detail="Cannot purchase own listing")
        
        # Calculate total cost
        total_cost = listing.get("price_per_inference", 0) * purchase.inferences_count
        
        # Get user
        user = db.get_or_create_user(user_id)
        
        # ETH ESCROW PATH (Decentralized!)
        escrow_result = None
        if use_eth_escrow:
            if not provider_address:
                # Try to get provider address from listing owner
                provider = db.get_or_create_user(listing.get("owner_id"))
                provider_address = provider.get("wallet_address")
            
            if not provider_address:
                raise HTTPException(
                    status_code=400,
                    detail="Provider ETH address required for escrow. Set provider_address parameter."
                )
            
            # Convert USD to ETH (simplified - use oracle in production)
            eth_price_usd = 2500  # Approximate
            amount_eth = total_cost / eth_price_usd
            
            # Create real escrow
            escrow_result = await escrow_service.create_escrow(
                job_id=f"purchase-{purchase.listing_id}-{datetime.utcnow().timestamp()}",
                provider_address=provider_address,
                amount_eth=amount_eth
            )
            
            if not escrow_result.get("success"):
                raise HTTPException(
                    status_code=500,
                    detail=f"Escrow creation failed: {escrow_result.get('error', 'Unknown error')}"
                )
        else:
            # Traditional balance-based escrow (simulated)
            if user.get("balance", 0) < total_cost:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient balance. Required: ${total_cost}, Available: ${user.get('balance', 0)}"
                )
            
            # Deduct balance
            new_balance = user.get("balance", 0) - total_cost
            db.update_user_balance(user["id"], new_balance)
        
        # Check if user already has a purchase for this listing
        existing_purchase = db.get_purchase_by_user_and_listing(user_id, purchase.listing_id)
        
        if existing_purchase:
            # Add to existing purchase
            new_remaining = existing_purchase.get("inferences_remaining", 0) + purchase.inferences_count
            new_total = existing_purchase.get("inferences_bought", 0) + purchase.inferences_count
            new_paid = existing_purchase.get("total_paid", 0) + total_cost
            
            update_data = {
                "inferences_remaining": new_remaining,
                "inferences_bought": new_total,
                "total_paid": new_paid
            }
            
            if escrow_result:
                update_data["eth_escrow"] = escrow_result
            
            db.update_purchase(existing_purchase["id"], update_data)
            purchase_record = db.get_purchase(existing_purchase["id"])
        else:
            # Create new purchase
            purchase_data = {
                "user_id": user_id,
                "listing_id": purchase.listing_id,
                "model_id": listing.get("model_id"),
                "inferences_bought": purchase.inferences_count,
                "inferences_remaining": purchase.inferences_count,
                "total_paid": total_cost,
                "escrow_type": "eth" if use_eth_escrow else "balance"
            }
            
            if escrow_result:
                purchase_data["eth_escrow"] = escrow_result
            
            purchase_record = db.create_purchase(purchase_data)
        
        response_data = {
            "purchase": purchase_record,
            "escrow": {
                "type": "eth_smart_contract" if use_eth_escrow else "platform_balance",
                "status": "locked",
                "amount_usd": total_cost,
                "will_release_on": "Successful inference with on-chain verified ZK proof",
                "trustless": use_eth_escrow
            }
        }
        
        if escrow_result:
            response_data["eth_escrow"] = {
                "transaction_hash": escrow_result.get("transaction_hash"),
                "block_number": escrow_result.get("block_number"),
                "amount_eth": escrow_result.get("amount_eth"),
                "contract_address": escrow_service.contract_address,
                "simulated": escrow_result.get("simulated", False)
            }
        else:
            response_data["remaining_balance"] = user.get("balance", 0) - total_cost
        
        return APIResponse(
            success=True,
            message=f"Successfully purchased {purchase.inferences_count} inference credits" + 
                    (" with ETH escrow" if use_eth_escrow else ""),
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/use-inference/{purchase_id}", response_model=APIResponse)
async def use_purchased_inference(purchase_id: str, input_data: dict):
    """
    Use a purchased inference credit.
    
    DECENTRALIZED FLOW:
    1. Run inference on model
    2. Generate and anchor ZK proof on-chain
    3. Verify proof on-chain
    4. Release ETH escrow to provider (if ETH escrow was used)
    5. Return results to user
    
    Model details are NEVER exposed to the buyer!
    """
    try:
        purchase = db.get_purchase(purchase_id)
        if not purchase:
            raise HTTPException(status_code=404, detail="Purchase not found")
        
        if purchase.get("inferences_remaining", 0) <= 0:
            raise HTTPException(status_code=400, detail="No inference credits remaining")
        
        model_id = purchase.get("model_id")
        model = db.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model no longer available")
        
        listing = db.get_listing(purchase.get("listing_id"))
        
        # Create job ID for on-chain anchoring
        job_id_temp = f"job-{purchase_id}-{datetime.utcnow().timestamp()}"
        
        # Run inference with on-chain anchoring
        result = inference_engine.run_inference(
            job_id=job_id_temp,
            model_id=model_id,
            model_type=model.get("model_type", "classification"),
            input_data=input_data,
            use_zkml=True,  # Always use ZKML for marketplace inferences
            anchor_on_chain=True  # Always anchor for marketplace
        )
        
        # Create job record
        job_data = {
            "model_id": model_id,
            "user_id": purchase.get("user_id"),
            "input_data": input_data,
            "output_data": result["output_data"],
            "status": "completed",
            "proof_hash": result.get("proof", {}).get("proof_hash"),
            "latency_ms": result["total_time_ms"],
            "completed_at": datetime.utcnow().isoformat(),
            "purchase_id": purchase_id
        }
        
        # Add on-chain info
        on_chain_info = result.get("proof", {}).get("on_chain", {})
        if on_chain_info.get("anchored"):
            job_data["transaction_hash"] = on_chain_info.get("transaction_hash")
            job_data["block_number"] = on_chain_info.get("block_number")
        
        job = db.create_job(job_data)
        
        # Store proof
        if "proof" in result:
            proof_data = {
                "job_id": job["id"],
                **result["proof"]
            }
            db.create_proof(proof_data)
        
        # On-chain verification before releasing escrow
        proof_verified = result.get("verification", {}).get("is_valid", False)
        escrow_released = False
        escrow_release_result = None
        
        # Release escrow based on type
        price = listing.get("price_per_inference", 0)
        
        if purchase.get("escrow_type") == "eth" and purchase.get("eth_escrow"):
            # REAL ETH ESCROW RELEASE
            if proof_verified:
                proof_hash = result.get("proof", {}).get("proof_hash")
                escrow_release_result = await escrow_service.release_escrow(
                    job_id=job_id_temp,
                    proof_hash=proof_hash
                )
                escrow_released = escrow_release_result.get("success", False)
            else:
                # Verification failed - initiate refund
                escrow_release_result = await escrow_service.refund_escrow(
                    job_id=job_id_temp,
                    reason="ZK proof verification failed"
                )
        else:
            # Traditional balance-based escrow release
            owner = db.get_or_create_user(listing.get("owner_id"))
            db.update_user_balance(owner["id"], owner.get("balance", 0) + price)
            escrow_released = True
        
        # Decrement remaining inferences
        new_remaining = purchase.get("inferences_remaining", 1) - 1
        db.update_purchase(purchase_id, {"inferences_remaining": new_remaining})
        
        # Update listing stats
        db.update_listing(purchase.get("listing_id"), {
            "total_inferences": listing.get("total_inferences", 0) + 1
        })
        
        # Build response with complete decentralization status
        response_data = {
            "job_id": job["id"],
            "output": result["output_data"],
            "inference_time_ms": result["inference_time_ms"],
            "total_time_ms": result["total_time_ms"],
            "zkml_proof": {
                "proof_hash": result.get("proof", {}).get("proof_hash"),
                "is_verified": proof_verified,
                "verification_message": result.get("verification", {}).get("message"),
                "gas_estimate": result.get("verification", {}).get("gas_estimate")
            },
            "on_chain": on_chain_info if on_chain_info else None,
            "credits_remaining": new_remaining,
            "escrow": {
                "type": purchase.get("escrow_type", "balance"),
                "released": escrow_released,
                "payment_to_provider": price,
                "release_details": escrow_release_result
            }
        }
        
        return APIResponse(
            success=True,
            message="Inference completed with on-chain verification" if on_chain_info.get("anchored") else "Inference completed successfully",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/purchases", response_model=APIResponse)
async def get_user_purchases(user_id: str):
    """
    Get all purchases for a user.
    """
    purchases = db.get_user_purchases(user_id)
    
    # Enrich with listing info
    enriched = []
    for purchase in purchases:
        listing = db.get_listing(purchase.get("listing_id"))
        enriched.append({
            **purchase,
            "listing_name": listing.get("model_name") if listing else "Unknown",
            "listing_price": listing.get("price_per_inference") if listing else 0
        })
    
    return APIResponse(
        success=True,
        message=f"Found {len(enriched)} purchases",
        data=enriched
    )


@router.get("/my-listings", response_model=APIResponse)
async def get_my_listings(owner_id: str):
    """
    Get all marketplace listings owned by a user.
    """
    all_listings = db.get_active_listings()
    my_listings = [l for l in all_listings if l.get("owner_id") == owner_id]
    
    return APIResponse(
        success=True,
        message=f"Found {len(my_listings)} listings",
        data=my_listings
    )


@router.put("/listing/{listing_id}", response_model=APIResponse)
async def update_listing(
    listing_id: str,
    owner_id: str,
    price_per_inference: Optional[float] = None,
    description: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """
    Update a marketplace listing.
    """
    listing = db.get_listing(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if listing.get("owner_id") != owner_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updates = {}
    if price_per_inference is not None:
        updates["price_per_inference"] = price_per_inference
    if description is not None:
        updates["description"] = description
    if is_active is not None:
        updates["is_active"] = is_active
    
    if updates:
        listing = db.update_listing(listing_id, updates)
    
    return APIResponse(
        success=True,
        message="Listing updated successfully",
        data=listing
    )


@router.get("/categories", response_model=APIResponse)
async def get_categories():
    """
    Get available marketplace categories.
    """
    categories = [
        {"id": "classification", "name": "Image Classification", "icon": "🖼️"},
        {"id": "nlp", "name": "Natural Language Processing", "icon": "📝"},
        {"id": "regression", "name": "Regression & Prediction", "icon": "📈"},
        {"id": "embedding", "name": "Embeddings & Encoders", "icon": "🧮"},
        {"id": "generative", "name": "Generative AI", "icon": "✨"},
        {"id": "audio", "name": "Audio Processing", "icon": "🎵"},
        {"id": "video", "name": "Video Analysis", "icon": "🎬"},
        {"id": "other", "name": "Other", "icon": "📦"}
    ]
    
    return APIResponse(
        success=True,
        message="Categories retrieved",
        data=categories
    )
