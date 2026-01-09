"""
V-Inference Demo Data Seeder
Pre-populates the database with demo models and jobs for presentation
"""
from datetime import datetime, timedelta


def seed_demo_data(db):
    """
    Seed database with demo data for presentation
    
    Creates:
    - 6 models (different types)  
    - 10 inference jobs (mix of verified and unverified)
    - 4 marketplace listings
    """
    
    demo_user_id = "demo-user"
    
    # ============= DEMO MODELS =============
    demo_models = [
        {
            "id": "model-sentiment-001",
            "name": "SentimentBERT Pro",
            "description": "Advanced sentiment analysis model using BERT architecture. Detects positive, negative, and neutral sentiments with high accuracy.",
            "model_type": "nlp",
            "owner_id": demo_user_id,
            "is_public": True,
            "file_path": "/models/sentiment_bert.onnx",
            "metadata": {"version": "2.1", "accuracy": 0.94, "parameters": "110M"},
            "total_inferences": 1247,
            "average_latency_ms": 45,
            "created_at": (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"
        },
        {
            "id": "model-image-002", 
            "name": "ImageNet Classifier",
            "description": "ResNet-50 based image classification model trained on ImageNet. Classifies 1000+ categories.",
            "model_type": "classification",
            "owner_id": demo_user_id,
            "is_public": True,
            "file_path": "/models/resnet50_imagenet.onnx",
            "metadata": {"version": "1.0", "accuracy": 0.76, "parameters": "25M"},
            "total_inferences": 856,
            "average_latency_ms": 120,
            "created_at": (datetime.utcnow() - timedelta(days=25)).isoformat() + "Z"
        },
        {
            "id": "model-fraud-003",
            "name": "FraudDetect AI",
            "description": "Machine learning model for detecting fraudulent transactions. Real-time risk scoring.",
            "model_type": "classification",
            "owner_id": demo_user_id,
            "is_public": False,
            "file_path": "/models/fraud_detector.onnx",
            "metadata": {"version": "3.2", "precision": 0.98, "recall": 0.95},
            "total_inferences": 5420,
            "average_latency_ms": 18,
            "created_at": (datetime.utcnow() - timedelta(days=60)).isoformat() + "Z"
        },
        {
            "id": "model-embed-004",
            "name": "Text Embedder v2",
            "description": "Generate 384-dimensional embeddings for text. Perfect for semantic search and similarity.",
            "model_type": "embedding",
            "owner_id": demo_user_id,
            "is_public": True,
            "file_path": "/models/embedder_v2.onnx",
            "metadata": {"dimensions": 384, "vocabulary": "50K"},
            "total_inferences": 3200,
            "average_latency_ms": 25,
            "created_at": (datetime.utcnow() - timedelta(days=15)).isoformat() + "Z"
        },
        {
            "id": "model-price-005",
            "name": "Price Predictor",
            "description": "Regression model for predicting asset prices based on historical data and market indicators.",
            "model_type": "regression",
            "owner_id": demo_user_id,
            "is_public": False,
            "file_path": "/models/price_predictor.pt",
            "metadata": {"r_squared": 0.89, "features": 42},
            "total_inferences": 890,
            "average_latency_ms": 35,
            "created_at": (datetime.utcnow() - timedelta(days=10)).isoformat() + "Z"
        },
        {
            "id": "model-credit-006",
            "name": "CreditScore ML",
            "description": "Fair lending credit scoring model with bias detection and explainability features.",
            "model_type": "classification",
            "owner_id": demo_user_id,
            "is_public": True,
            "file_path": "/models/credit_score.onnx",
            "metadata": {"auc": 0.91, "features": 28, "bias_checked": True},
            "total_inferences": 2100,
            "average_latency_ms": 22,
            "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat() + "Z"
        }
    ]
    
    # ============= DEMO JOBS (MIX OF VERIFIED AND UNVERIFIED) =============
    demo_jobs = [
        # ✅ VERIFIED JOBS (have proof hash, verified status)
        {
            "id": "job-verified-001",
            "model_id": "model-sentiment-001",
            "user_id": demo_user_id,
            "input_data": {"text": "This product is absolutely amazing! Best purchase ever."},
            "output_data": {"sentiment": "positive", "confidence": 0.9876, "label": "POSITIVE"},
            "status": "verified",
            "proof_hash": "0x7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b",
            "verification_status": "on_chain_verified",
            "latency_ms": 42,
            "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z",
            "completed_at": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z"
        },
        {
            "id": "job-verified-002",
            "model_id": "model-fraud-003",
            "user_id": demo_user_id,
            "input_data": {"transaction_amount": 5000, "merchant_category": "electronics"},
            "output_data": {"is_fraud": False, "risk_score": 0.12, "confidence": 0.95},
            "status": "verified",
            "proof_hash": "0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
            "verification_status": "on_chain_verified",
            "latency_ms": 18,
            "created_at": (datetime.utcnow() - timedelta(hours=5)).isoformat() + "Z",
            "completed_at": (datetime.utcnow() - timedelta(hours=5)).isoformat() + "Z"
        },
        {
            "id": "job-verified-003",
            "model_id": "model-credit-006",
            "user_id": demo_user_id,
            "input_data": {"income": 75000, "debt_ratio": 0.3, "credit_history": "good"},
            "output_data": {"approved": True, "score": 720, "confidence": 0.88},
            "status": "verified",
            "proof_hash": "0x9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d",
            "verification_status": "on_chain_verified",
            "latency_ms": 22,
            "created_at": (datetime.utcnow() - timedelta(hours=8)).isoformat() + "Z",
            "completed_at": (datetime.utcnow() - timedelta(hours=8)).isoformat() + "Z"
        },
        
        # ❌ NOT VERIFIED / PENDING JOBS
        {
            "id": "job-pending-001",
            "model_id": "model-sentiment-001",
            "user_id": demo_user_id,
            "input_data": {"text": "The service was okay, nothing special."},
            "output_data": {"sentiment": "neutral", "confidence": 0.65},
            "status": "completed",
            "proof_hash": None,
            "verification_status": "not_verified",
            "latency_ms": 38,
            "created_at": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z",
            "completed_at": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
        },
        {
            "id": "job-pending-002",
            "model_id": "model-image-002",
            "user_id": demo_user_id,
            "input_data": {"image_url": "https://example.com/cat.jpg"},
            "output_data": {"class": "cat", "confidence": 0.92},
            "status": "completed",
            "proof_hash": None,
            "verification_status": "zkml_disabled",
            "latency_ms": 115,
            "created_at": (datetime.utcnow() - timedelta(hours=3)).isoformat() + "Z",
            "completed_at": (datetime.utcnow() - timedelta(hours=3)).isoformat() + "Z"
        },
        {
            "id": "job-failed-001",
            "model_id": "model-price-005",
            "user_id": demo_user_id,
            "input_data": {"asset": "BTC", "timeframe": "1d"},
            "output_data": None,
            "status": "failed",
            "proof_hash": None,
            "verification_status": "failed",
            "latency_ms": None,
            "created_at": (datetime.utcnow() - timedelta(hours=6)).isoformat() + "Z",
            "completed_at": None
        },
        {
            "id": "job-processing-001",
            "model_id": "model-embed-004",
            "user_id": demo_user_id,
            "input_data": {"text": "Processing this text for embeddings..."},
            "output_data": None,
            "status": "processing",
            "proof_hash": None,
            "verification_status": "pending",
            "latency_ms": None,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "completed_at": None
        },
        
        # More verified for variety
        {
            "id": "job-verified-004",
            "model_id": "model-embed-004",
            "user_id": demo_user_id,
            "input_data": {"text": "Semantic search query embedding"},
            "output_data": {"embedding_generated": True, "dimensions": 384},
            "status": "verified",
            "proof_hash": "0x4f5e6d7c8b9a0f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6b7a8f9e0d1c2b3a4f5e",
            "verification_status": "on_chain_verified",
            "latency_ms": 24,
            "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z",
            "completed_at": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
        },
        {
            "id": "job-verified-005",
            "model_id": "model-sentiment-001",
            "user_id": demo_user_id,
            "input_data": {"text": "Terrible experience. Would not recommend."},
            "output_data": {"sentiment": "negative", "confidence": 0.9654, "label": "NEGATIVE"},
            "status": "verified",
            "proof_hash": "0x2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c",
            "verification_status": "on_chain_verified",
            "latency_ms": 40,
            "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z",
            "completed_at": (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z"
        },
        {
            "id": "job-unverified-003",
            "model_id": "model-fraud-003",
            "user_id": demo_user_id,
            "input_data": {"transaction_amount": 150000, "merchant_category": "jewelry"},
            "output_data": {"is_fraud": True, "risk_score": 0.87, "confidence": 0.91},
            "status": "completed",
            "proof_hash": None,
            "verification_status": "proof_generation_failed",
            "latency_ms": 20,
            "created_at": (datetime.utcnow() - timedelta(hours=12)).isoformat() + "Z",
            "completed_at": (datetime.utcnow() - timedelta(hours=12)).isoformat() + "Z"
        }
    ]
    
    # ============= DEMO MARKETPLACE LISTINGS =============
    demo_listings = [
        {
            "id": "listing-001",
            "model_id": "model-sentiment-001",
            "model_name": "SentimentBERT Pro",
            "description": "Production-ready sentiment analysis. Verified on-chain for guaranteed accuracy.",
            "price_per_inference": 0.05,
            "category": "nlp",
            "tags": ["sentiment", "bert", "verified"],
            "rating": 4.8,
            "total_inferences": 1247,
            "total_revenue": 62.35,
            "owner_id": demo_user_id,
            "is_active": True,
            "model_type": "nlp",
            "created_at": (datetime.utcnow() - timedelta(days=28)).isoformat() + "Z"
        },
        {
            "id": "listing-002",
            "model_id": "model-image-002",
            "model_name": "ImageNet Classifier",
            "description": "Classify images into 1000+ categories with ResNet-50 backbone.",
            "price_per_inference": 0.08,
            "category": "classification",
            "tags": ["image", "resnet", "imagenet"],
            "rating": 4.5,
            "total_inferences": 856,
            "total_revenue": 68.48,
            "owner_id": demo_user_id,
            "is_active": True,
            "model_type": "classification",
            "created_at": (datetime.utcnow() - timedelta(days=20)).isoformat() + "Z"
        },
        {
            "id": "listing-003",
            "model_id": "model-embed-004",
            "model_name": "Text Embedder v2",
            "description": "Generate semantic embeddings for search, similarity, and clustering.",
            "price_per_inference": 0.02,
            "category": "embedding",
            "tags": ["embedding", "semantic", "search"],
            "rating": 4.9,
            "total_inferences": 3200,
            "total_revenue": 64.00,
            "owner_id": demo_user_id,
            "is_active": True,
            "model_type": "embedding",
            "created_at": (datetime.utcnow() - timedelta(days=12)).isoformat() + "Z"
        },
        {
            "id": "listing-004",
            "model_id": "model-credit-006",
            "model_name": "CreditScore ML",
            "description": "Fair, explainable credit decisions with bias detection. ZKML verified.",
            "price_per_inference": 0.15,
            "category": "classification",
            "tags": ["credit", "lending", "verified", "fair-ai"],
            "rating": 4.7,
            "total_inferences": 2100,
            "total_revenue": 315.00,
            "owner_id": demo_user_id,
            "is_active": True,
            "model_type": "classification",
            "created_at": (datetime.utcnow() - timedelta(days=3)).isoformat() + "Z"
        }
    ]
    
    # Read existing data
    existing_models = db._read_file(db.models_file)
    existing_jobs = db._read_file(db.jobs_file)
    existing_listings = db._read_file(db.listings_file)
    
    # Get existing IDs
    existing_model_ids = {m["id"] for m in existing_models}
    existing_job_ids = {j["id"] for j in existing_jobs}
    existing_listing_ids = {l["id"] for l in existing_listings}
    
    # Add new demo data
    added_models = 0
    for model in demo_models:
        if model["id"] not in existing_model_ids:
            existing_models.append(model)
            added_models += 1
    
    added_jobs = 0
    for job in demo_jobs:
        if job["id"] not in existing_job_ids:
            existing_jobs.append(job)
            added_jobs += 1
    
    added_listings = 0
    for listing in demo_listings:
        if listing["id"] not in existing_listing_ids:
            existing_listings.append(listing)
            added_listings += 1
    
    # Save to files
    db._write_file(db.models_file, existing_models)
    db._write_file(db.jobs_file, existing_jobs)
    db._write_file(db.listings_file, existing_listings)
    
    print("✅ Demo data seeded successfully!")
    print(f"   📦 {added_models} new models added")
    print(f"   ⚡ {added_jobs} new jobs (5 verified ✅, 5 not verified ❌)")
    print(f"   🛒 {added_listings} new marketplace listings")
    
    return {
        "models_added": added_models,
        "jobs_added": added_jobs,
        "listings_added": added_listings
    }
