"""
V-Inference Backend - Data Models
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class ModelType(str, Enum):
    ONNX = "onnx"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    CUSTOM = "custom"


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


class EscrowStatus(str, Enum):
    LOCKED = "locked"
    RELEASED = "released"
    REFUNDED = "refunded"


# User Models
class UserBase(BaseModel):
    wallet_address: str
    username: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    balance: float = 1000.0  # Mock balance for demo

    class Config:
        from_attributes = True


# AI Model Models
class AIModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    model_type: ModelType = ModelType.ONNX
    is_public: bool = False


class AIModelCreate(AIModelBase):
    pass


class AIModel(AIModelBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_inferences: int = 0
    average_latency_ms: float = 0.0

    class Config:
        from_attributes = True


# Inference Job Models
class InferenceInput(BaseModel):
    model_id: str
    input_data: Dict[str, Any]
    use_zkml: bool = True
    simulate_failure: bool = False  # Demo mode: simulate failed verification


class InferenceJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_id: str
    user_id: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: JobStatus = JobStatus.PENDING
    proof_hash: Optional[str] = None
    verification_status: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    latency_ms: Optional[float] = None

    class Config:
        from_attributes = True


# Marketplace Models
class MarketplaceListing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_id: str
    owner_id: str
    model_name: str
    description: str
    price_per_inference: float
    is_active: bool = True
    total_inferences: int = 0
    total_revenue: float = 0.0
    rating: float = 5.0
    category: str = "general"
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class ListingCreate(BaseModel):
    model_id: str
    price_per_inference: float
    description: Optional[str] = None
    category: str = "general"
    tags: List[str] = Field(default_factory=list)


# Purchase Models
class Purchase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    listing_id: str
    model_id: str
    inferences_bought: int
    inferences_remaining: int
    total_paid: float
    escrow_status: EscrowStatus = EscrowStatus.LOCKED
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class PurchaseCreate(BaseModel):
    listing_id: str
    inferences_count: int = 1


# ZK Proof Models
class ZKProof(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    proof_hash: str
    circuit_hash: str
    verification_key: str
    is_valid: bool = False
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class InferenceResponse(BaseModel):
    job_id: str
    status: JobStatus
    output: Optional[Dict[str, Any]] = None
    proof: Optional[ZKProof] = None
    latency_ms: Optional[float] = None
