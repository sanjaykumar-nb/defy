"""
V-Inference Backend - IPFS Service
Decentralized storage for AI models using IPFS
Supports multiple providers: Local IPFS node, Pinata, Infura, Web3.Storage
"""
import os
import json
import hashlib
import aiohttp
import asyncio
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

# Configuration - Use environment variables in production
IPFS_PROVIDER = os.getenv("IPFS_PROVIDER", "pinata")  # local, pinata, infura, web3storage
PINATA_API_KEY = os.getenv("PINATA_API_KEY", "")
PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY", "")
INFURA_PROJECT_ID = os.getenv("INFURA_PROJECT_ID", "")
INFURA_PROJECT_SECRET = os.getenv("INFURA_PROJECT_SECRET", "")
LOCAL_IPFS_API = os.getenv("LOCAL_IPFS_API", "http://127.0.0.1:5001")

# Public IPFS gateways for retrieval
IPFS_GATEWAYS = [
    "https://ipfs.io/ipfs/",
    "https://gateway.pinata.cloud/ipfs/",
    "https://cloudflare-ipfs.com/ipfs/",
    "https://dweb.link/ipfs/",
    "https://w3s.link/ipfs/"
]

# Local cache for downloaded models
IPFS_CACHE_PATH = Path("storage/ipfs_cache")
IPFS_CACHE_PATH.mkdir(parents=True, exist_ok=True)


class IPFSService:
    """
    IPFS Service for decentralized model storage
    
    Features:
    - Upload models to IPFS (via Pinata, Infura, or local node)
    - Download models from IPFS with caching
    - Pin management for persistence
    - Content verification using CID
    """
    
    def __init__(self):
        self.provider = IPFS_PROVIDER
        self.connected = False
        self.gateway = IPFS_GATEWAYS[0]
        
        # Check configuration
        self._check_config()
    
    def _check_config(self):
        """Check if IPFS provider is properly configured"""
        if self.provider == "pinata":
            if PINATA_API_KEY and PINATA_SECRET_KEY:
                self.connected = True
                print(f"✅ IPFS Service connected via Pinata")
            else:
                print("⚠️ IPFS: Pinata API keys not configured - using simulation mode")
                self.connected = False
        elif self.provider == "infura":
            if INFURA_PROJECT_ID and INFURA_PROJECT_SECRET:
                self.connected = True
                print(f"✅ IPFS Service connected via Infura")
            else:
                print("⚠️ IPFS: Infura credentials not configured - using simulation mode")
                self.connected = False
        elif self.provider == "local":
            # Will check connection when actually used
            self.connected = True
            print(f"✅ IPFS Service configured for local node at {LOCAL_IPFS_API}")
        else:
            print(f"⚠️ IPFS: Unknown provider '{self.provider}' - using simulation mode")
            self.connected = False
    
    def generate_local_cid(self, file_path: str) -> str:
        """Generate a simulated CID based on file hash (for simulation mode)"""
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        # Create a CID-like string (v1 CID format simulation)
        return f"bafybeig{file_hash[:50]}"
    
    async def upload_file(self, file_path: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Upload a file to IPFS
        
        Args:
            file_path: Path to the file to upload
            metadata: Optional metadata for pinning service
            
        Returns:
            Dict with CID, size, and upload details
        """
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)
        
        # Real upload if configured
        if self.connected and self.provider == "pinata":
            return await self._upload_to_pinata(file_path, metadata)
        elif self.connected and self.provider == "infura":
            return await self._upload_to_infura(file_path)
        elif self.connected and self.provider == "local":
            return await self._upload_to_local_ipfs(file_path)
        
        # Simulation mode - generate local CID
        cid = self.generate_local_cid(file_path)
        
        # Copy to local cache as "IPFS storage"
        cache_path = IPFS_CACHE_PATH / cid
        cache_path.mkdir(parents=True, exist_ok=True)
        
        import shutil
        cached_file = cache_path / filename
        shutil.copy2(file_path, cached_file)
        
        return {
            "success": True,
            "cid": cid,
            "ipfs_hash": cid,
            "filename": filename,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "gateway_url": f"{self.gateway}{cid}",
            "upload_timestamp": datetime.utcnow().isoformat(),
            "provider": "simulation",
            "simulated": True,
            "local_cache": str(cached_file)
        }
    
    async def _upload_to_pinata(self, file_path: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Upload file to Pinata IPFS pinning service"""
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        
        filename = os.path.basename(file_path)
        
        # Prepare metadata
        pin_metadata = {
            "name": filename,
            "keyvalues": metadata or {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                with open(file_path, 'rb') as f:
                    form_data = aiohttp.FormData()
                    form_data.add_field('file', f, filename=filename)
                    form_data.add_field('pinataMetadata', json.dumps(pin_metadata))
                    form_data.add_field('pinataOptions', json.dumps({"cidVersion": 1}))
                    
                    headers = {
                        "pinata_api_key": PINATA_API_KEY,
                        "pinata_secret_api_key": PINATA_SECRET_KEY
                    }
                    
                    async with session.post(url, data=form_data, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            cid = result.get("IpfsHash")
                            
                            return {
                                "success": True,
                                "cid": cid,
                                "ipfs_hash": cid,
                                "filename": filename,
                                "size_bytes": result.get("PinSize", 0),
                                "size_mb": round(result.get("PinSize", 0) / (1024 * 1024), 2),
                                "gateway_url": f"https://gateway.pinata.cloud/ipfs/{cid}",
                                "upload_timestamp": result.get("Timestamp"),
                                "provider": "pinata",
                                "simulated": False
                            }
                        else:
                            error = await response.text()
                            print(f"❌ Pinata upload failed: {error}")
                            return {
                                "success": False,
                                "error": f"Pinata upload failed: {error}"
                            }
                            
        except Exception as e:
            print(f"❌ Pinata upload error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _upload_to_infura(self, file_path: str) -> Dict[str, Any]:
        """Upload file to Infura IPFS"""
        url = "https://ipfs.infura.io:5001/api/v0/add"
        
        filename = os.path.basename(file_path)
        
        try:
            import base64
            auth = base64.b64encode(f"{INFURA_PROJECT_ID}:{INFURA_PROJECT_SECRET}".encode()).decode()
            
            async with aiohttp.ClientSession() as session:
                with open(file_path, 'rb') as f:
                    form_data = aiohttp.FormData()
                    form_data.add_field('file', f, filename=filename)
                    
                    headers = {
                        "Authorization": f"Basic {auth}"
                    }
                    
                    async with session.post(url, data=form_data, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            cid = result.get("Hash")
                            
                            return {
                                "success": True,
                                "cid": cid,
                                "ipfs_hash": cid,
                                "filename": result.get("Name", filename),
                                "size_bytes": int(result.get("Size", 0)),
                                "size_mb": round(int(result.get("Size", 0)) / (1024 * 1024), 2),
                                "gateway_url": f"https://ipfs.infura.io/ipfs/{cid}",
                                "upload_timestamp": datetime.utcnow().isoformat(),
                                "provider": "infura",
                                "simulated": False
                            }
                        else:
                            error = await response.text()
                            return {
                                "success": False,
                                "error": f"Infura upload failed: {error}"
                            }
                            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _upload_to_local_ipfs(self, file_path: str) -> Dict[str, Any]:
        """Upload file to local IPFS node"""
        url = f"{LOCAL_IPFS_API}/api/v0/add"
        
        filename = os.path.basename(file_path)
        
        try:
            async with aiohttp.ClientSession() as session:
                with open(file_path, 'rb') as f:
                    form_data = aiohttp.FormData()
                    form_data.add_field('file', f, filename=filename)
                    
                    async with session.post(url, data=form_data) as response:
                        if response.status == 200:
                            result = await response.json()
                            cid = result.get("Hash")
                            
                            return {
                                "success": True,
                                "cid": cid,
                                "ipfs_hash": cid,
                                "filename": result.get("Name", filename),
                                "size_bytes": int(result.get("Size", 0)),
                                "size_mb": round(int(result.get("Size", 0)) / (1024 * 1024), 2),
                                "gateway_url": f"{self.gateway}{cid}",
                                "upload_timestamp": datetime.utcnow().isoformat(),
                                "provider": "local",
                                "simulated": False
                            }
                        else:
                            error = await response.text()
                            return {
                                "success": False,
                                "error": f"Local IPFS upload failed: {error}"
                            }
                            
        except aiohttp.ClientConnectorError:
            print("⚠️ Local IPFS node not running, using simulation mode")
            # Fall back to simulation
            cid = self.generate_local_cid(file_path)
            return {
                "success": True,
                "cid": cid,
                "ipfs_hash": cid,
                "filename": filename,
                "size_bytes": os.path.getsize(file_path),
                "gateway_url": f"{self.gateway}{cid}",
                "upload_timestamp": datetime.utcnow().isoformat(),
                "provider": "simulation",
                "simulated": True,
                "note": "Local IPFS node not available"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def download_file(self, cid: str, output_path: str) -> Dict[str, Any]:
        """
        Download a file from IPFS
        
        Args:
            cid: The IPFS CID (Content Identifier)
            output_path: Where to save the downloaded file
            
        Returns:
            Dict with download status and file info
        """
        # Check local cache first
        cache_check = self._check_cache(cid)
        if cache_check:
            # Copy from cache to output path
            import shutil
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.copy2(cache_check, output_path)
            return {
                "success": True,
                "cid": cid,
                "output_path": output_path,
                "source": "cache",
                "cached_path": cache_check
            }
        
        # Try downloading from gateways
        for gateway in IPFS_GATEWAYS:
            try:
                result = await self._download_from_gateway(cid, output_path, gateway)
                if result.get("success"):
                    # Cache the file
                    self._cache_file(cid, output_path)
                    return result
            except Exception as e:
                print(f"Gateway {gateway} failed: {e}")
                continue
        
        return {
            "success": False,
            "error": "Failed to download from all gateways",
            "cid": cid
        }
    
    def _check_cache(self, cid: str) -> Optional[str]:
        """Check if file exists in local cache"""
        cache_dir = IPFS_CACHE_PATH / cid
        if cache_dir.exists():
            # Return first file in cache directory
            files = list(cache_dir.iterdir())
            if files:
                return str(files[0])
        return None
    
    def _cache_file(self, cid: str, file_path: str):
        """Cache a downloaded file"""
        cache_dir = IPFS_CACHE_PATH / cid
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        import shutil
        filename = os.path.basename(file_path)
        cached_path = cache_dir / filename
        shutil.copy2(file_path, cached_path)
    
    async def _download_from_gateway(self, cid: str, output_path: str, gateway: str) -> Dict[str, Any]:
        """Download file from a specific IPFS gateway"""
        url = f"{gateway}{cid}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=300)) as response:
                    if response.status == 200:
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        
                        with open(output_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
                        return {
                            "success": True,
                            "cid": cid,
                            "output_path": output_path,
                            "source": "gateway",
                            "gateway": gateway,
                            "size_bytes": os.path.getsize(output_path)
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Gateway returned status {response.status}"
                        }
                        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Download timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def pin_file(self, cid: str) -> Dict[str, Any]:
        """Pin a file to ensure it stays available"""
        if self.provider == "pinata" and self.connected:
            return await self._pin_to_pinata(cid)
        
        return {
            "success": True,
            "cid": cid,
            "pinned": True,
            "simulated": True,
            "note": "Pinning simulated - configure Pinata for real pinning"
        }
    
    async def _pin_to_pinata(self, cid: str) -> Dict[str, Any]:
        """Pin an existing IPFS hash to Pinata"""
        url = "https://api.pinata.cloud/pinning/pinByHash"
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "pinata_api_key": PINATA_API_KEY,
                    "pinata_secret_api_key": PINATA_SECRET_KEY,
                    "Content-Type": "application/json"
                }
                
                data = {
                    "hashToPin": cid
                }
                
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "cid": cid,
                            "pinned": True,
                            "pin_id": result.get("id"),
                            "simulated": False
                        }
                    else:
                        error = await response.text()
                        return {
                            "success": False,
                            "error": f"Pinning failed: {error}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def unpin_file(self, cid: str) -> Dict[str, Any]:
        """Unpin a file (remove from pinning service)"""
        if self.provider == "pinata" and self.connected:
            url = f"https://api.pinata.cloud/pinning/unpin/{cid}"
            
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "pinata_api_key": PINATA_API_KEY,
                        "pinata_secret_api_key": PINATA_SECRET_KEY
                    }
                    
                    async with session.delete(url, headers=headers) as response:
                        if response.status == 200:
                            return {
                                "success": True,
                                "cid": cid,
                                "unpinned": True
                            }
                        else:
                            error = await response.text()
                            return {
                                "success": False,
                                "error": f"Unpinning failed: {error}"
                            }
                            
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "success": True,
            "cid": cid,
            "unpinned": True,
            "simulated": True
        }
    
    def get_gateway_url(self, cid: str, gateway_index: int = 0) -> str:
        """Get the full gateway URL for a CID"""
        gateway = IPFS_GATEWAYS[gateway_index % len(IPFS_GATEWAYS)]
        return f"{gateway}{cid}"
    
    def verify_cid(self, cid: str, file_path: str) -> bool:
        """Verify that a file matches its CID (for simulation mode)"""
        if not os.path.exists(file_path):
            return False
        
        expected_cid = self.generate_local_cid(file_path)
        return expected_cid == cid
    
    def get_status(self) -> Dict[str, Any]:
        """Get IPFS service status"""
        return {
            "connected": self.connected,
            "provider": self.provider,
            "gateway": self.gateway,
            "cache_path": str(IPFS_CACHE_PATH),
            "available_gateways": IPFS_GATEWAYS
        }


# Global instance
ipfs_service = IPFSService()
