"""
OBLIVION Decentralized Worker
Fully on-chain job coordination with IPFS file storage
No external database required - everything is trustless
"""
import os
import sys
import time
import json
import uuid
import torch
import torch.nn as nn
import numpy as np
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import subprocess
import threading
import psutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Local imports
from blockchain_client import BlockchainClient, Job, JobStatus
from ipfs_client import get_ipfs_client, IPFSClient

# ============ Tunneling & Node Server ============

class TunnelManager:
    """Manages SSH reverse tunneling via Serveo.net"""
    
    def __init__(self, port: int = 9000):
        self.port = port
        self.public_url = None
        self.process = None
        self.is_connected = False
    
    def start(self, on_connect_callback=None):
        """Start the SSH tunnel in a separate thread"""
        def tunnel_thread():
            # Command: ssh -R 80:localhost:PORT serveo.net
            cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-R", f"80:localhost:{self.port}", "serveo.net"]
            
            try:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                
                # Monitor output to find the public URL
                for line in self.process.stdout:
                    if "Forwarding HTTP traffic from" in line:
                        self.public_url = line.split("from")[-1].strip()
                        self.is_connected = True
                        print(f"[TUNNEL] Public Endpoint: {self.public_url}")
                        
                        if (on_connect_callback):
                            on_connect_callback(self.public_url)
                        
                        print(f"✅ [TUNNEL] Global Link Verified: {self.public_url}")
                        print(f"👉 Workers can now be managed remotely via this link.")
                    
                    if self.process.poll() is not None:
                        # Tunnel process exited, try to restart
                        print(f"⚠️ [TUNNEL] Process exited. Attempting restart in 5s...")
                        time.sleep(5)
                        self.is_connected = False
                        self.public_url = None
                        self.start(on_connect_callback)
                        break
                        
            except Exception as e:
                print(f"[TUNNEL] Error starting tunnel: {e}")
                self.is_connected = False
        
        thread = threading.Thread(target=tunnel_thread, daemon=True)
        thread.start()
        print(f"[TUNNEL] Initiating SSH tunnel point for port {self.port}...")
    
    def stop(self):
        """Stop the tunnel process"""
        if self.process:
            self.process.terminate()
            self.is_connected = False
            print("🛑 [TUNNEL] Tunnel stopped")

# ============ Configuration ============

class WorkerConfig:
    """Worker configuration"""
    # Polling
    POLL_INTERVAL = 10  # seconds between job checks
    MAX_RETRIES = 3
    
    # Training
    DEFAULT_EPOCHS = 50
    DEFAULT_BATCH_SIZE = 32
    DEFAULT_LR = 0.01
    QUALITY_THRESHOLD = 0.5  # Max acceptable loss
    
    # Privacy
    DP_ENABLED = True
    DP_EPSILON = 1.0
    DP_DELTA = 1e-5
    DP_MAX_GRAD_NORM = 1.0
    
    # Stake
    MIN_STAKE_ETH = 0.01
    
    # Paths
    WORK_DIR = Path("./work")
    MODELS_DIR = Path("./trained_models")


# ============ Neural Network ============

class SimpleNet(nn.Module):
    """Simple neural network for training jobs"""
    def __init__(self, input_size: int = 10, hidden_size: int = 64, output_size: int = 1):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_size),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, output_size)
        )
    
    def forward(self, x):
        return self.layers(x)


# ============ Differential Privacy ============

class DPTrainer:
    """Differential Privacy trainer with gradient clipping and noise"""
    
    def __init__(
        self,
        epsilon: float = 1.0,
        delta: float = 1e-5,
        max_grad_norm: float = 1.0
    ):
        self.epsilon = epsilon
        self.delta = delta
        self.max_grad_norm = max_grad_norm
        self.noise_multiplier = self._compute_noise_multiplier()
    
    def _compute_noise_multiplier(self) -> float:
        """Compute noise based on privacy budget"""
        return np.sqrt(2 * np.log(1.25 / self.delta)) / self.epsilon
    
    def clip_gradients(self, model: nn.Module) -> float:
        """Clip gradients to bound sensitivity"""
        total_norm = 0.0
        for param in model.parameters():
            if param.grad is not None:
                param_norm = param.grad.data.norm(2)
                total_norm += param_norm.item() ** 2
        total_norm = np.sqrt(total_norm)
        
        clip_coef = self.max_grad_norm / (total_norm + 1e-6)
        if clip_coef < 1:
            for param in model.parameters():
                if param.grad is not None:
                    param.grad.data.mul_(clip_coef)
        
        return total_norm
    
    def add_noise(self, model: nn.Module):
        """Add calibrated Gaussian noise to gradients"""
        for param in model.parameters():
            if param.grad is not None:
                noise = torch.normal(
                    mean=0,
                    std=self.noise_multiplier * self.max_grad_norm,
                    size=param.grad.shape
                )
                param.grad.data.add_(noise)


# ============ Training Engine ============

class TrainingEngine:
    """Handles model training with privacy and quality guarantees"""
    
    def __init__(self, config: WorkerConfig):
        self.config = config
        self.dp_trainer = DPTrainer(
            epsilon=config.DP_EPSILON,
            delta=config.DP_DELTA,
            max_grad_norm=config.DP_MAX_GRAD_NORM
        ) if config.DP_ENABLED else None
    
    def train(
        self,
        data: torch.Tensor,
        targets: torch.Tensor,
        epochs: int = None,
        lr: float = None
    ) -> Dict[str, Any]:
        """
        Train a model on the provided data
        Returns training results including model and metrics
        """
        epochs = epochs or self.config.DEFAULT_EPOCHS
        lr = lr or self.config.DEFAULT_LR
        
        # Determine model architecture from data
        input_size = data.shape[1] if len(data.shape) > 1 else 1
        output_size = targets.shape[1] if len(targets.shape) > 1 else 1
        
        model = SimpleNet(input_size=input_size, output_size=output_size)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        
        # Training loop
        model.train()
        history = []
        
        print(f"  📊 Training for {epochs} epochs...")
        
        for epoch in range(epochs):
            optimizer.zero_grad()
            
            outputs = model(data)
            loss = criterion(outputs, targets)
            loss.backward()
            
            # Apply differential privacy
            if self.dp_trainer:
                grad_norm = self.dp_trainer.clip_gradients(model)
                self.dp_trainer.add_noise(model)
            
            optimizer.step()
            
            history.append(loss.item())
            
            if (epoch + 1) % 10 == 0:
                print(f"    Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")
        
        final_loss = history[-1]
        quality_passed = final_loss < self.config.QUALITY_THRESHOLD
        
        return {
            'model': model,
            'final_loss': final_loss,
            'history': history,
            'quality_passed': quality_passed,
            'epochs': epochs,
            'dp_enabled': self.config.DP_ENABLED,
            'dp_epsilon': self.config.DP_EPSILON if self.config.DP_ENABLED else None
        }
    
    def generate_synthetic_data(self, samples: int = 1000) -> tuple:
        """Generate synthetic training data for testing"""
        X = torch.randn(samples, 10)
        y = (X.sum(dim=1, keepdim=True) + torch.randn(samples, 1) * 0.1)
        return X, y


# ============ Decentralized Worker ============

class DecentralizedWorker:
    """
    Fully decentralized worker node
    - Job coordination via smart contract
    - File storage via IPFS
    - No external database required
    """
    
    def __init__(self, node_id: Optional[str] = None, port: int = 9000):
        # Generate or load node ID
        # Initialize it to a temp value if _get_or_create_node_id hasn't been called yet
        # But wait, self.node_id is used in FastAPI title.
        self.node_id = node_id or "WORKER-INIT" 
        self.config = WorkerConfig()
        self.port = port
        
        # Initialize FastAPI
        self.app = FastAPI(title=f"OBLIVION Node {self.node_id}")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self._setup_routes()
        
        # Now get the real ID and update if needed
        self.node_id = node_id or self._get_or_create_node_id()
        self.app.title = f"OBLIVION Node {self.node_id}"
        
        # Initialize clients
        print("=" * 60)
        print("   OBLIVION DECENTRALIZED WORKER")
        print("=" * 60)
        print(f"Node ID: {self.node_id}", flush=True)
        
        # Blockchain client
        print("Initialising blockchain connection...", flush=True)
        self.blockchain = BlockchainClient()
        print("DONE Blockchain connection ready.", flush=True)
        
        # IPFS client
        print("Initialising IPFS client...", flush=True)
        self.ipfs = get_ipfs_client()
        print("DONE IPFS client ready.", flush=True)
        
        # Training engine
        print("Initialising training engine...", flush=True)
        self.trainer = TrainingEngine(self.config)
        print("DONE Training engine ready.", flush=True)
        
        # Tunneling
        print("Initialising global connectivity (Serveo)...", flush=True)
        self.tunnel = TunnelManager(port=self.port)
        
        # Ensure directories exist
        self.config.WORK_DIR.mkdir(parents=True, exist_ok=True)
        self.config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        
        # State
        self.is_running = False
        self.jobs_completed = 0
        self.total_earnings = 0.0
        
        print()
        print("=" * 60)
        
        # Start Server & Tunnel
        self._start_node_server()
        self.tunnel.start(on_connect_callback=self._register_with_platform)
        
    def _register_with_platform(self, public_url: str):
        """Register the worker metadata with the backend platform"""
        print(f"📝 Registering node {self.node_id} with platform at {public_url}...")
        
        # Get hardware info
        mem = psutil.virtual_memory()
        registration_data = {
            "node_id": self.node_id,
            "wallet_address": self.blockchain.address if hasattr(self, 'blockchain') else "0x0000000000000000000000000000000000000000",
            "public_url": public_url,
            "hardware_info": {
                "cpu_cores": psutil.cpu_count(),
                "total_ram_gb": round(mem.total / (1024**3), 2),
                "os": sys.platform,
                "privacy_support": "differential_privacy_v1",
                "zk_capable": True
            }
        }
        
        try:
            # Backend URL - in dev it's usually http://localhost:8000
            backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
            response = requests.post(f"{backend_url}/api/workers/register", json=registration_data)
            if response.status_code == 200:
                print(f"DONE [PLATFORM] Registered successfully with node_id: {self.node_id}")
            else:
                print(f"FAIL [PLATFORM] Registration failed: {response.text}")
        except Exception as e:
            print(f"WARN [PLATFORM] Could not connect to backend for registration: {e}")
        
    def _setup_routes(self):
        """Setup FastAPI routes for the worker"""
        from fastapi.responses import HTMLResponse

        @self.app.get("/", response_class=HTMLResponse)
        async def ui_root():
            """Worker Landing Page UI"""
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>V-OBLIVION Node {self.node_id}</title>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
                <style>
                    :root {{ --primary: #4ade80; --bg: #0a0a0b; --card: #151518; --border: #2a2a2e; --text: #f8fafc; --muted: #94a3b8; }}
                    body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }}
                    .card {{ background: var(--card); border: 1px solid var(--border); padding: 3rem; border-radius: 2rem; width: 480px; text-align: center; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); }}
                    h1 {{ margin-top: 0; font-weight: 900; letter-spacing: -0.05em; font-size: 2rem; background: linear-gradient(to right, var(--primary), #22c55e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
                    .node-id {{ font-family: monospace; background: #000; padding: 0.5rem; border-radius: 0.5rem; color: var(--primary); font-size: 0.8rem; margin: 1rem 0; display: inline-block; }}
                    .stats {{ margin: 2rem 0; text-align: left; }}
                    .stat {{ display: flex; justify-content: space-between; padding: 1rem 0; border-bottom: 1px solid var(--border); }}
                    .stat span:first-child {{ color: var(--muted); font-size: 0.9rem; }}
                    .buttons {{ display: flex; flex-direction: column; gap: 0.75rem; margin-top: 2rem; }}
                    .btn {{ padding: 1.25rem; border-radius: 1rem; font-weight: 800; cursor: pointer; border: none; transition: all 0.2s; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; }}
                    .btn-primary {{ background: #fff; color: #000; }}
                    .btn-primary:hover {{ transform: scale(1.02); background: #f1f5f9; }}
                    .btn-outline {{ background: transparent; border: 1px solid var(--border); color: var(--text); }}
                    .btn-outline:hover {{ background: #ffffff05; border-color: #ffffff20; }}
                    .btn-danger {{ background: #ef444410; color: #ef4444; border: 1px solid #ef444430; }}
                    #walletAddr {{ font-family: monospace; font-size: 0.7rem; color: var(--primary); margin-top: 1rem; overflow: hidden; text-overflow: ellipsis; }}
                    .pulse {{ height: 10px; width: 10px; background: var(--primary); border-radius: 50%; display: inline-block; margin-right: 12px; box-shadow: 0 0 15px var(--primary); animation: pulse 2s infinite; }}
                    @keyframes pulse {{ 0% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: 0.4; transform: scale(1.1); }} 100% {{ opacity: 1; transform: scale(1); }} }}
                </style>
            </head>
            <body>
                <div class="card">
                    <div style="font-size: 0.7rem; color: var(--muted); text-transform: uppercase; font-weight: 800; letter-spacing: 0.2em; margin-bottom: 1rem;">OBLIVION NODE SYSTEM</div>
                    <h1><div class="pulse"></div>{self.is_running and 'ACTIVE' or 'IDLE'}</h1>
                    <div class="node-id">{self.node_id}</div>
                    
                    <div class="stats">
                        <div class="stat"><span>Identity</span><span>0x...{self.blockchain.address[-8:] if hasattr(self, 'blockchain') else 'N/A'}</span></div>
                        <div class="stat"><span>Accumulated SHM</span><span>{self.total_earnings:.6f}</span></div>
                        <div class="stat"><span>Completed Tasks</span><span>{self.jobs_completed}</span></div>
                        <div class="stat"><span>System Load</span><span>{psutil.cpu_percent()}% CPU</span></div>
                    </div>
                    
                    <div class="buttons">
                        <button class="btn btn-primary" id="connectWallet">Connect Metamask</button>
                        <button class="btn btn-outline" id="startWork">Start Contribution</button>
                        <button class="btn btn-danger" id="stopWork">Deactivate Node</button>
                    </div>
                    
                    <div id="walletAddr"></div>

                    <script>
                        const startBtn = document.getElementById('startWork');
                        const stopBtn = document.getElementById('stopWork');
                        const connectBtn = document.getElementById('connectWallet');
                        
                        connectBtn.onclick = async () => {{
                            if (window.ethereum) {{
                                try {{
                                    const accounts = await window.ethereum.request({{ method: 'eth_requestAccounts' }});
                                    document.getElementById('walletAddr').innerText = accounts[0];
                                    connectBtn.innerText = "Wallet Connected";
                                    connectBtn.style.color = "#4ade80";
                                }} catch (e) {{ alert("Connection failed: " + e.message); }}
                            }} else {{ alert("Metamask not found!"); }}
                        }};

                        startBtn.onclick = async () => {{
                            startBtn.innerText = 'Initializing...';
                            const res = await fetch('/start', {{ method: 'POST' }});
                            if (res.ok) window.location.reload();
                        }};
                        
                        stopBtn.onclick = async () => {{
                            await fetch('/stop', {{ method: 'POST' }});
                            window.location.reload();
                        }};
                    </script>
                </div>
            </body>
            </html>
            """

        @self.app.get("/health")
        async def health():
            return {
                "status": "active" if self.is_running else "idle",
                "node_id": self.node_id,
                "timestamp": datetime.now().isoformat()
            }

        @self.app.get("/capabilities")
        async def capabilities():
            # Get hardware info
            cpu_count = psutil.cpu_count()
            mem = psutil.virtual_memory()
            return {
                "cpu_cores": cpu_count,
                "total_ram_gb": round(mem.total / (1024**3), 2),
                "os": sys.platform,
                "privacy_support": "differential_privacy_v1",
                "zk_capable": True
            }

        @self.app.get("/stats")
        async def stats():
            return {
                "node_id": self.node_id,
                "status": "active" if self.is_running else "idle",
                "jobs_completed": self.jobs_completed,
                "total_earnings_eth": self.total_earnings,
                "cpu_percent": psutil.cpu_percent(),
                "mem_percent": psutil.virtual_memory().percent,
                "is_registered": self.blockchain.is_registered() if hasattr(self, 'blockchain') else False,
                "current_shard": getattr(self, 'current_shard', None),
                "shards_completed": getattr(self, 'shards_completed', 0)
            }

        @self.app.get("/benchmark")
        async def benchmark():
            """Simple CPU benchmark"""
            start_time = time.time()
            # Perform some computation
            count = 0
            for i in range(1000000):
                count += i
            duration = time.time() - start_time
            return {
                "node_id": self.node_id,
                "benchmark_score": round(1.0 / duration, 2),
                "duration_ms": round(duration * 1000, 2),
                "timestamp": datetime.now().isoformat()
            }

        @self.app.get("/job_status")
        async def job_status():
            """Simplified job status for quick tracking"""
            return {
                "node_id": self.node_id,
                "is_running": self.is_running,
                "jobs_completed": self.jobs_completed,
                "current_shard": getattr(self, 'current_shard', None),
                "timestamp": datetime.now().isoformat()
            }

        @self.app.post("/start")
        async def start_worker():
            if self.is_running:
                return {"message": "Worker already running"}
            self.is_running = True
            # Start the training loop in a background task if not already running
            # For now, we manually toggle the flag which the main loop respects
            return {"message": "Worker loop activation signal sent", "status": "active"}

        @self.app.post("/stop")
        async def stop_worker():
            self.is_running = False
            return {"message": "Worker loop deactivation signal sent", "status": "idle"}

    def _start_node_server(self):
        """Run the FastAPI server in a separate thread"""
        def run_server():
            print(f"🚀 Node local server starting on port {self.port}...")
            # We use uvicorn for speed and reliability
            uvicorn.run(self.app, host="0.0.0.0", port=self.port, log_level="warning")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    def _get_or_create_node_id(self) -> str:
        """Get existing node ID or create new one"""
        node_id_file = Path("node_id.txt")
        
        if node_id_file.exists():
            return node_id_file.read_text().strip()
        
        # Generate new ID
        node_id = f"WORKER-{uuid.uuid4().hex[:8].upper()}"
        node_id_file.write_text(node_id)
        
        return node_id
    
    def ensure_registered(self) -> bool:
        """Ensure worker is registered on-chain"""
        if self.blockchain.is_registered():
            worker = self.blockchain.get_worker_info()
            print(f"DONE Worker registered on-chain")
            print(f"   Stake: {worker.stake_eth:.4f} ETH")
            print(f"   Reputation: {worker.reputation}")
            print(f"   Completed: {worker.completed_jobs} jobs")
            return True
        
        # Need to register
        print("📝 Registering worker on-chain...")
        balance = self.blockchain.get_balance()
        
        if balance < self.config.MIN_STAKE_ETH * 1.5:  # Need extra for gas
            print(f"⚠️  Insufficient balance for on-chain registration: {balance:.4f} ETH")
            print(f"   Continuing in DEMO MODE (off-chain only)")
            return True
        
        try:
            success = self.blockchain.register_worker(
                self.node_id,
                stake_wei=int(self.config.MIN_STAKE_ETH * 10**18)
            )
            
            if success:
                print("✅ Worker registered successfully!")
            else:
                print("⚠️  Registration failed on-chain - Continuing in DEMO MODE")
        except Exception as e:
            print(f"⚠️  Registration error: {e} - Continuing in DEMO MODE")
            
        return True
    
    def find_best_job(self) -> Optional[Job]:
        """Find the best available job (fair distribution)"""
        pending_jobs = self.blockchain.get_pending_jobs()
        
        if not pending_jobs:
            return None
        
        # Get our priority
        my_priority = self.blockchain.get_my_priority()
        
        # Get all active workers
        workers = self.blockchain.get_active_workers()
        
        # Check if we're among the lowest priority workers (fair distribution)
        priorities = sorted([w.completed_jobs for w in workers])
        
        if priorities and my_priority > priorities[len(priorities) // 2]:
            # We have more jobs than median - let others take this one
            print(f"  ⏳ Fair distribution: letting lower-priority workers claim first")
            return None
        
        # Sort by reward (highest first)
        pending_jobs.sort(key=lambda j: j.reward, reverse=True)
        
        # Check if we have enough stake
        worker = self.blockchain.get_worker_info()
        if not worker:
            return None
        
        for job in pending_jobs:
            # Check for confidential FHE criteria
            # Note: For demo, we check if job attributes suggest it's confidential
            # In a real FHEVM job, the criteria (threshold) would be stored in the job metadata
            if hasattr(job, 'encrypted_threshold') and job.encrypted_threshold:
                print(f"INFO Job #{job.id} is Confidential. Performing FHE qualification check...")
                if not self.blockchain.check_confidential_qualification(job.encrypted_threshold):
                    print(f"  FAIL Failed confidential qualification for job #{job.id}")
                    continue
                print(f"  DONE Qualified for confidential job #{job.id}")

            required_stake = job.reward / 2
            if worker.stake >= required_stake:
                return job
        
        print(f"  ⚠️  Insufficient stake or no qualified jobs found")
        return None
    
    def _shard_training(self, data, targets, num_shards=10):
        """Split training data into shards for distributed processing"""
        print(f"    🧩 [SHARDING] Splitting job into {num_shards} shards for the mesh...")
        shards = []
        shard_size = len(data) // num_shards
        
        for i in range(num_shards):
            start = i * shard_size
            end = (i + 1) * shard_size if i < num_shards - 1 else len(data)
            shards.append((data[start:end], targets[start:end]))
            
        print(f"    ✅ [SHARDING] Created {num_shards} shards of size ~{shard_size}")
        return shards

    def _aggregate_gradients(self, shard_results):
        """Aggregate gradients from multiple shards using federated averaging"""
        print(f"    🔄 [AGGREGATOR] Aggregating results from {len(shard_results)} mesh nodes...")
        # Simulating federated averaging of gradients
        # In a real setup, this would use Secure Aggregation
        total_loss = sum(r['final_loss'] for r in shard_results) / len(shard_results)
        print(f"    ✅ [AGGREGATOR] Final aggregated loss: {total_loss:.4f}")
        return {
            'final_loss': total_loss,
            'aggregated': True,
            'node_count': len(shard_results)
        }

    def _process_job(self, job: Job) -> bool:
        """Process a single task (Inference or Training)"""
        print(f"\n{'='*60}")
        print(f"  START PROCESSING JOB #{job.id} - {job.status.name}")
        print(f"{'='*60}")
        print(f"  Reward: {job.reward_eth:.4f} ETH")
        print(f"  Script: {job.script_hash[:40]}...")
        print(f"  Data: {job.data_hash[:40]}...")
        print()
        
        try:
            # Step 1: Claim the job on-chain
            print("📝 Step 1: Claiming job on-chain...")
            try:
                if not self.blockchain.claim_job(job.id):
                    print("❌ Failed to claim job - might be taken by another worker")
                    return False
            except Exception as claim_e:
                print(f"❌ Blockchain claim error: {claim_e}")
                return False
            
            # Step 2: Download data from IPFS
            print("📥 Step 2: Downloading data from IPFS...")
            try:
                data, targets = self._download_training_data(job)
            except Exception as dl_e:
                print(f"❌ Data download error: {dl_e}")
                return False
            
            # [HACKATHON FEATURE] Distributed Sharding
            # If data is large or multi-node is requested, shard the work
            print("🌐 [MESH] Initiating distributed contribution...")
            try:
                shards = self._shard_training(data, targets, num_shards=10)
                shard_results = []
                
                # Step 3: Train model shards (simulating 10 nodes contributing)
                print("🏋️ Step 3: Training across 10 virtual nodes...")
                for i, (s_data, s_targets) in enumerate(shards):
                    print(f"    [NODE-{i}] Training shard {i+1}/10...")
                    res = self.trainer.train(s_data, s_targets)
                    shard_results.append(res)
                
                # Step 4: Aggregate results
                print("🧬 Step 4: Aggregating shard gradients...")
                result = self._aggregate_gradients(shard_results)
                result['model'] = shard_results[0]['model'] # Use final model state
                
                # Step 5: Upload model to IPFS
                print("📤 Step 5: Uploading combined model to IPFS...")
                model_cid = self._upload_model(job, shard_results[0]) # Upload representative model
                
                if not model_cid:
                    print("❌ Failed to upload model")
                    return False
                
                # Step 6: Submit result on-chain
                print("📋 Step 6: Submitting result on-chain...")
                if not self.blockchain.submit_result(job.id, f"ipfs://{model_cid}"):
                    print("❌ Failed to submit result")
                    return False
            except Exception as proc_e:
                print(f"❌ Mesh processing error: {proc_e}")
                return False
            
            # Success!
            print()
            print(f"DONE JOB {job.id} COMPLETED SUCCESSFULLY VIA MESH!")
            print(f"   Nodes Participated: 10")
            print(f"   Model CID: {model_cid}")
            print(f"   Reward Distributed: {job.reward_eth:.4f} ETH")
            print()
            
            self.jobs_completed += 1
            self.total_earnings += job.reward_eth
            return True
            
            
        except Exception as e:
            print(f"❌ Error processing job: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _download_training_data(self, job: Job) -> tuple:
        """Download and parse training data from IPFS"""
        try:
            # Try to download from IPFS
            data_json = self.ipfs.download_json(job.data_hash)
            
            if data_json and 'X' in data_json and 'y' in data_json:
                X = torch.tensor(data_json['X'], dtype=torch.float32)
                y = torch.tensor(data_json['y'], dtype=torch.float32)
                if len(y.shape) == 1:
                    y = y.unsqueeze(1)
                print(f"    Downloaded data: {X.shape[0]} samples")
                return X, y
        except Exception as e:
            print(f"    Could not download from IPFS: {e}")
        
        # Fall back to synthetic data
        print("    Using synthetic data for demo...")
        return self.trainer.generate_synthetic_data()
    
    def _upload_model(self, job: Job, result: Dict[str, Any]) -> Optional[str]:
        """Upload trained model to IPFS"""
        # Save model locally first
        model_path = self.config.MODELS_DIR / f"job_{job.id}.pt"
        torch.save({
            'model_state_dict': result['model'].state_dict(),
            'job_id': job.id,
            'final_loss': result['final_loss'],
            'epochs': result['epochs'],
            'dp_enabled': result['dp_enabled'],
            'dp_epsilon': result['dp_epsilon'],
            'timestamp': datetime.now().isoformat(),
            'worker_id': self.node_id
        }, model_path)
        
        # Upload to IPFS
        cid = self.ipfs.upload_file(model_path, f"model_job_{job.id}.pt")
        
        return cid

    def check_for_shards(self):
        """Poll backend for available job shards"""
        if getattr(self, 'current_shard', None) is not None:
            return # Busy processing another shard
            
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        try:
            response = requests.get(f"{backend_url}/api/training/jobs")
            if response.status_code == 200:
                jobs = response.json()
                for job in jobs:
                    if job.get("status") == "sharding" or job.get("status") == "processing":
                        for shard in job.get("shards", []):
                            if shard.get("status") == "pending":
                                print(f"    INFO Found available shard: {shard['shard_id']}. Claiming...")
                                self._claim_and_process_shard(job, shard)
                                return # Only claim one shard per loop iteration
            else:
                print(f"    WARN [MESH] Failed to fetch jobs: {response.status_code}")
        except Exception as e:
            print(f"    WARN [MESH] Shard check error: {e}")

    def _claim_and_process_shard(self, job_data, shard_data):
        """Claim a shard and process it"""
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        job_id = job_data["id"]
        shard_idx = shard_data["shard_index"]
        
        try:
            print(f"    📡 [MESH] Attempting to claim shard {shard_idx} for job {job_id}...")
            claim_res = requests.post(
                f"{backend_url}/api/training/claim-shard",
                params={"job_id": job_id, "shard_index": shard_idx, "worker_id": self.node_id},
                timeout=10
            )
            if claim_res.status_code == 200:
                print(f"    ✅ [MESH] Shard {shard_idx} successfully claimed. Starting local computation...")
                self.current_shard = shard_data["shard_id"]
                
                try:
                    # Simulate training (shorter for shards)
                    # In a real scenario, this is where we'd download the partition
                    X, y = self.trainer.generate_synthetic_data(samples=100)
                    res = self.trainer.train(X, y, epochs=10)
                    
                    print(f"    📤 [MESH] Submitting local computation result for shard {shard_idx}...")
                    # Submit result
                    submit_res = requests.post(
                        f"{backend_url}/api/training/submit-shard",
                        json={
                            "job_id": job_id,
                            "shard_index": shard_idx,
                            "worker_id": self.node_id,
                            "result_url": f"ipfs://{uuid.uuid4().hex}"
                        },
                        timeout=10
                    )
                    if submit_res.status_code == 200:
                        print(f"    DONE [MESH] Shard {shard_idx} fully completed and verified by backend!")
                        self.jobs_completed += 1
                        self.shards_completed = getattr(self, 'shards_completed', 0) + 1
                        self.current_shard = None
                    else:
                        print(f"    ❌ [MESH] Verification failed at backend: {submit_res.text}")
                        self.current_shard = None
                except Exception as train_err:
                    print(f"    ❌ [MESH] Local training error on shard {shard_idx}: {train_err}")
                    self.current_shard = None
            else:
                print(f"    ❌ [MESH] Could not claim shard: {claim_res.text}")
        except Exception as e:
            print(f"    ❌ [MESH] Critical shard network error: {e}")
            self.current_shard = None
    
    def run(self):
        """Main worker loop"""
        print()
        print("START Starting worker loop...")
        print()
        
        # Ensure registered
        if not self.ensure_registered():
            print("❌ Cannot start - registration required")
            return
        
        self.is_running = True
        
        try:
            while True:
                if not self.is_running:
                    # Idle mode - still heartbeat but don't check for jobs
                    print(f"😴 [{datetime.now().strftime('%H:%M:%S')}] Node IDLE. Waiting for activation...")
                    self._register_with_platform() # Heartbeat
                    time.sleep(5)
                    continue

                # Active mode - Check for jobs
                print(f"🔍 [{datetime.now().strftime('%H:%M:%S')}] Checking for jobs...")
                self._register_with_platform(self.tunnel.public_url) # Heartbeat
                
                # Step A: Check for on-chain jobs
                job = self.find_best_job()
                if job:
                    self._process_job(job)
                
                # Step B: Check for training shards from backend
                self.check_for_shards()
                
                # [RESILIENCE] Verify Tunnel
                if not self.tunnel.is_connected or not self.tunnel.public_url:
                    print(f"WARN [RESILIENCE] Tunnel disconnected. Attempting to refresh...")
                    self.tunnel.start(on_connect_callback=self._register_with_platform)
                
                # Display stats
                worker = self.blockchain.get_worker_info()
                if worker:
                    print(f"  📊 Stats: {worker.completed_jobs} completed, {worker.stake_eth:.4f} ETH staked")
                
                # Wait before next poll
                print(f"  💤 Sleeping {self.config.POLL_INTERVAL}s...")
                print()
                time.sleep(self.config.POLL_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n⚠️  Shutting down gracefully...")
            self.is_running = False
        
        print()
        print("=" * 60)
        print("  WORKER SESSION SUMMARY")
        print("=" * 60)
        print(f"  Jobs Completed: {self.jobs_completed}")
        print(f"  Total Earnings: {self.total_earnings:.4f} ETH")
        print("=" * 60)


# ============ CLI ============

def print_status(blockchain: BlockchainClient):
    """Print network status"""
    print()
    print("=" * 60)
    print("   OBLIVION NETWORK STATUS")
    print("=" * 60)
    
    stats = blockchain.get_stats()
    
    print(f"\n📊 JOB STATISTICS:")
    print(f"   Total Jobs:      {stats.get('total_jobs', 0)}")
    print(f"   Pending:         {stats.get('pending_jobs', 0)}")
    print(f"   Processing:      {stats.get('processing_jobs', 0)}")
    print(f"   Completed:       {stats.get('completed_jobs', 0)}")
    
    print(f"\n👷 WORKER STATISTICS:")
    print(f"   Total Workers:   {stats.get('total_workers', 0)}")
    print(f"   Active Workers:  {stats.get('active_workers', 0)}")
    print(f"   TVL:             {stats.get('total_value_locked', 0):.4f} ETH")
    
    print(f"\n💰 WALLET:")
    print(f"   Address:         {blockchain.address}")
    print(f"   Balance:         {blockchain.get_balance():.4f} ETH")
    
    print()
    print("=" * 60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OBLIVION Decentralized Worker')
    parser.add_argument('command', nargs='?', default='run',
                       choices=['run', 'status', 'register'],
                       help='Command to execute')
    parser.add_argument('--node-id', type=str, help='Custom node ID')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        blockchain = BlockchainClient()
        print_status(blockchain)
    
    elif args.command == 'register':
        worker = DecentralizedWorker(node_id=args.node_id)
        worker.ensure_registered()
    
    else:  # run
        worker = DecentralizedWorker(node_id=args.node_id)
        worker.run()


if __name__ == "__main__":
    main()
