"""
V-Inference Backend - Database Service
JSON-based file storage simulating a database
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class Database:
    """Simple JSON file-based database for demo purposes"""
    
    def __init__(self, storage_path: str = "storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize data files
        self.users_file = self.storage_path / "users.json"
        self.models_file = self.storage_path / "models.json"
        self.jobs_file = self.storage_path / "jobs.json"
        self.listings_file = self.storage_path / "listings.json"
        self.purchases_file = self.storage_path / "purchases.json"
        self.proofs_file = self.storage_path / "proofs.json"
        
        # Initialize files if they don't exist
        self._init_file(self.users_file, [])
        self._init_file(self.models_file, [])
        self._init_file(self.jobs_file, [])
        self._init_file(self.listings_file, [])
        self._init_file(self.purchases_file, [])
        self._init_file(self.proofs_file, [])
    
    def _init_file(self, file_path: Path, default_data: Any):
        if not file_path.exists():
            with open(file_path, 'w') as f:
                json.dump(default_data, f, indent=2, default=str)
    
    def _read_file(self, file_path: Path) -> List[Dict]:
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _write_file(self, file_path: Path, data: List[Dict]):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # User operations
    def create_user(self, user_data: Dict) -> Dict:
        users = self._read_file(self.users_file)
        user_data['id'] = str(uuid.uuid4())
        user_data['created_at'] = datetime.utcnow().isoformat()
        user_data['balance'] = 1000.0  # Demo balance
        users.append(user_data)
        self._write_file(self.users_file, users)
        return user_data
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        users = self._read_file(self.users_file)
        for user in users:
            if user['id'] == user_id:
                return user
        return None
    
    def get_user_by_wallet(self, wallet_address: str) -> Optional[Dict]:
        users = self._read_file(self.users_file)
        for user in users:
            if user.get('wallet_address') == wallet_address:
                return user
        return None
    
    def get_or_create_user(self, wallet_address: str) -> Dict:
        user = self.get_user_by_wallet(wallet_address)
        if not user:
            user = self.create_user({
                'wallet_address': wallet_address,
                'username': f"User_{wallet_address[:8]}"
            })
        return user
    
    def update_user_balance(self, user_id: str, new_balance: float) -> bool:
        users = self._read_file(self.users_file)
        for user in users:
            if user['id'] == user_id:
                user['balance'] = new_balance
                self._write_file(self.users_file, users)
                return True
        return False
    
    # Model operations
    def create_model(self, model_data: Dict) -> Dict:
        models = self._read_file(self.models_file)
        model_data['id'] = str(uuid.uuid4())
        model_data['created_at'] = datetime.utcnow().isoformat()
        model_data['total_inferences'] = 0
        model_data['average_latency_ms'] = 0.0
        models.append(model_data)
        self._write_file(self.models_file, models)
        return model_data
    
    def get_model(self, model_id: str) -> Optional[Dict]:
        models = self._read_file(self.models_file)
        for model in models:
            if model['id'] == model_id:
                return model
        return None
    
    def get_user_models(self, user_id: str) -> List[Dict]:
        models = self._read_file(self.models_file)
        return [m for m in models if m.get('owner_id') == user_id]
    
    def get_all_models(self) -> List[Dict]:
        return self._read_file(self.models_file)
    
    def update_model(self, model_id: str, updates: Dict) -> Optional[Dict]:
        models = self._read_file(self.models_file)
        for model in models:
            if model['id'] == model_id:
                model.update(updates)
                self._write_file(self.models_file, models)
                return model
        return None
    
    def delete_model(self, model_id: str) -> bool:
        models = self._read_file(self.models_file)
        original_len = len(models)
        models = [m for m in models if m['id'] != model_id]
        if len(models) < original_len:
            self._write_file(self.models_file, models)
            return True
        return False
    
    # Job operations
    def create_job(self, job_data: Dict) -> Dict:
        jobs = self._read_file(self.jobs_file)
        job_data['id'] = str(uuid.uuid4())
        job_data['created_at'] = datetime.utcnow().isoformat()
        job_data['status'] = 'pending'
        jobs.append(job_data)
        self._write_file(self.jobs_file, jobs)
        return job_data
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        jobs = self._read_file(self.jobs_file)
        for job in jobs:
            if job['id'] == job_id:
                return job
        return None
    
    def get_user_jobs(self, user_id: str) -> List[Dict]:
        jobs = self._read_file(self.jobs_file)
        return [j for j in jobs if j.get('user_id') == user_id]
    
    def update_job(self, job_id: str, updates: Dict) -> Optional[Dict]:
        jobs = self._read_file(self.jobs_file)
        for job in jobs:
            if job['id'] == job_id:
                job.update(updates)
                self._write_file(self.jobs_file, jobs)
                return job
        return None
    
    # Listing operations
    def create_listing(self, listing_data: Dict) -> Dict:
        listings = self._read_file(self.listings_file)
        listing_data['id'] = str(uuid.uuid4())
        listing_data['created_at'] = datetime.utcnow().isoformat()
        listing_data['total_inferences'] = 0
        listing_data['total_revenue'] = 0.0
        listing_data['is_active'] = True
        listings.append(listing_data)
        self._write_file(self.listings_file, listings)
        return listing_data
    
    def get_listing(self, listing_id: str) -> Optional[Dict]:
        listings = self._read_file(self.listings_file)
        for listing in listings:
            if listing['id'] == listing_id:
                return listing
        return None
    
    def get_listing_by_model(self, model_id: str) -> Optional[Dict]:
        listings = self._read_file(self.listings_file)
        for listing in listings:
            if listing.get('model_id') == model_id:
                return listing
        return None
    
    def get_active_listings(self) -> List[Dict]:
        listings = self._read_file(self.listings_file)
        return [l for l in listings if l.get('is_active', True)]
    
    def update_listing(self, listing_id: str, updates: Dict) -> Optional[Dict]:
        listings = self._read_file(self.listings_file)
        for listing in listings:
            if listing['id'] == listing_id:
                listing.update(updates)
                self._write_file(self.listings_file, listings)
                return listing
        return None
    
    # Purchase operations
    def create_purchase(self, purchase_data: Dict) -> Dict:
        purchases = self._read_file(self.purchases_file)
        purchase_data['id'] = str(uuid.uuid4())
        purchase_data['created_at'] = datetime.utcnow().isoformat()
        purchase_data['escrow_status'] = 'locked'
        purchases.append(purchase_data)
        self._write_file(self.purchases_file, purchases)
        return purchase_data
    
    def get_purchase(self, purchase_id: str) -> Optional[Dict]:
        purchases = self._read_file(self.purchases_file)
        for purchase in purchases:
            if purchase['id'] == purchase_id:
                return purchase
        return None
    
    def get_user_purchases(self, user_id: str) -> List[Dict]:
        purchases = self._read_file(self.purchases_file)
        return [p for p in purchases if p.get('user_id') == user_id]
    
    def get_purchase_by_user_and_listing(self, user_id: str, listing_id: str) -> Optional[Dict]:
        purchases = self._read_file(self.purchases_file)
        for purchase in purchases:
            if purchase.get('user_id') == user_id and purchase.get('listing_id') == listing_id:
                return purchase
        return None
    
    def update_purchase(self, purchase_id: str, updates: Dict) -> Optional[Dict]:
        purchases = self._read_file(self.purchases_file)
        for purchase in purchases:
            if purchase['id'] == purchase_id:
                purchase.update(updates)
                self._write_file(self.purchases_file, purchases)
                return purchase
        return None
    
    # Proof operations
    def create_proof(self, proof_data: Dict) -> Dict:
        proofs = self._read_file(self.proofs_file)
        proof_data['id'] = str(uuid.uuid4())
        proof_data['generated_at'] = datetime.utcnow().isoformat()
        proofs.append(proof_data)
        self._write_file(self.proofs_file, proofs)
        return proof_data
    
    def get_proof(self, proof_id: str) -> Optional[Dict]:
        proofs = self._read_file(self.proofs_file)
        for proof in proofs:
            if proof['id'] == proof_id:
                return proof
        return None
    
    def get_proof_by_job(self, job_id: str) -> Optional[Dict]:
        proofs = self._read_file(self.proofs_file)
        for proof in proofs:
            if proof.get('job_id') == job_id:
                return proof
        return None


# Global database instance
db = Database(storage_path="storage")
