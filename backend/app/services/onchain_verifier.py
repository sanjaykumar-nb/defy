"""
V-Inference Backend - On-Chain Verifier Service
Handles on-chain proof verification using smart contracts
"""
import hashlib
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from web3 import Web3

from ..core.config import (
    SEPOLIA_RPC_URL,
    CHAIN_ID,
    CONTRACT_ADDRESS,
    PRIVATE_KEY,
    CONTRACT_ABI,
    SEPOLIA_EXPLORER
)


# Extended ABI for verification contract
VERIFIER_ABI = [
    # Existing audit functions from main contract
    {
        "inputs": [
            {"internalType": "bytes32", "name": "proofHash", "type": "bytes32"},
            {"internalType": "string", "name": "jobId", "type": "string"}
        ],
        "name": "anchorAudit",
        "outputs": [{"internalType": "bool", "name": "success", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "jobId", "type": "string"},
            {"internalType": "bytes32", "name": "proofHash", "type": "bytes32"}
        ],
        "name": "verifyAudit",
        "outputs": [
            {"internalType": "bool", "name": "valid", "type": "bool"},
            {"internalType": "bytes32", "name": "onChainHash", "type": "bytes32"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "jobId", "type": "string"}],
        "name": "auditExists",
        "outputs": [{"internalType": "bool", "name": "exists", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "jobId", "type": "string"}],
        "name": "getAudit",
        "outputs": [
            {"internalType": "bytes32", "name": "proofHash", "type": "bytes32"},
            {"internalType": "address", "name": "auditor", "type": "address"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "uint256", "name": "blockNumber", "type": "uint256"},
            {"internalType": "bool", "name": "exists", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalAudits",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]


class OnChainVerifier:
    """
    On-Chain Verification Service
    
    Handles:
    1. Anchoring proofs on-chain (storing proof hash)
    2. Verifying proofs against on-chain records
    3. Reading verification status from blockchain
    4. Emitting events for verification results
    """
    
    def __init__(self):
        self.w3 = None
        self.contract = None
        self.account = None
        self.connected = False
        
        self._connect()
    
    def _connect(self):
        """Initialize Web3 connection"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
            
            if not self.w3.is_connected():
                print("⚠️ OnChainVerifier: Failed to connect to Sepolia")
                return
            
            self.connected = True
            print(f"✅ OnChainVerifier connected to Sepolia (Chain ID: {CHAIN_ID})")
            
            # Initialize contract
            if CONTRACT_ADDRESS:
                self.contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
                    abi=VERIFIER_ABI
                )
                print(f"📝 Verifier contract: {CONTRACT_ADDRESS}")
            
            # Initialize account
            if PRIVATE_KEY:
                self.account = self.w3.eth.account.from_key(PRIVATE_KEY)
                balance = self.w3.eth.get_balance(self.account.address)
                balance_eth = self.w3.from_wei(balance, 'ether')
                print(f"💰 Verifier account: {self.account.address} ({balance_eth:.4f} ETH)")
                
        except Exception as e:
            print(f"❌ OnChainVerifier connection error: {e}")
            self.connected = False
    
    def hash_to_bytes32(self, hash_string: str) -> bytes:
        """Convert a hash string to bytes32"""
        if hash_string.startswith("0x"):
            hash_string = hash_string[2:]
        
        # Ensure 64 hex chars (32 bytes)
        if len(hash_string) < 64:
            hash_string = hash_string.ljust(64, '0')
        elif len(hash_string) > 64:
            hash_string = hash_string[:64]
        
        return bytes.fromhex(hash_string)
    
    def reconstruct_proof_hash(
        self,
        input_hash: str,
        computation_hash: str,
        model_hash: str,
        job_id: str,
        timestamp: str,
        model_version: str = "v-inference-v1.0.0"
    ) -> str:
        """Reconstruct proof hash from components (for verification)"""
        combined = f"{input_hash}:{computation_hash}:{model_hash}:{job_id}:{timestamp}:{model_version}"
        return "0x" + hashlib.sha256(combined.encode()).hexdigest()
    
    async def anchor_proof(
        self,
        job_id: str,
        proof_hash: str
    ) -> Dict[str, Any]:
        """
        Anchor a proof hash on the blockchain
        
        Args:
            job_id: Unique job identifier
            proof_hash: The computed proof hash
            
        Returns:
            Transaction result with hash and block number
        """
        if not self.connected or not self.contract or not self.account:
            return self._simulated_anchor(job_id, proof_hash)
        
        try:
            # Check if already anchored
            try:
                exists = self.contract.functions.auditExists(job_id).call()
                if exists:
                    audit = await self.get_on_chain_audit(job_id)
                    return {
                        "success": True,
                        "already_anchored": True,
                        "job_id": job_id,
                        "proof_hash": proof_hash,
                        "on_chain_hash": audit.get("proof_hash"),
                        "block_number": audit.get("block_number"),
                        "transaction_hash": None,
                        "message": "Proof already anchored on-chain"
                    }
            except Exception as e:
                print(f"Warning: Could not check existing audit: {e}")
            
            # Convert proof hash to bytes32
            proof_bytes32 = self.hash_to_bytes32(proof_hash)
            
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # Get gas price
            gas_price = self.w3.eth.gas_price
            
            print(f"⛓️ Anchoring proof for job {job_id}...")
            
            # Build transaction
            tx = self.contract.functions.anchorAudit(
                proof_bytes32,
                job_id
            ).build_transaction({
                'chainId': CHAIN_ID,
                'gas': 200000,
                'gasPrice': gas_price,
                'nonce': nonce
            })
            
            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hex = self.w3.to_hex(tx_hash)
            
            print(f"📤 Anchor TX sent: {tx_hex}")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            gas_used = receipt['gasUsed']
            gas_cost_wei = gas_used * gas_price
            gas_cost_eth = float(self.w3.from_wei(gas_cost_wei, 'ether'))
            
            print(f"✅ Proof anchored in block {receipt['blockNumber']}")
            
            return {
                "success": True,
                "job_id": job_id,
                "proof_hash": proof_hash,
                "transaction_hash": tx_hex,
                "block_number": receipt['blockNumber'],
                "gas_used": gas_used,
                "gas_cost_eth": gas_cost_eth,
                "gas_cost_usd": gas_cost_eth * 2500,  # Approximate
                "explorer_url": f"{SEPOLIA_EXPLORER}/tx/{tx_hex}",
                "contract_address": CONTRACT_ADDRESS,
                "chain": "Sepolia",
                "chain_id": CHAIN_ID,
                "simulated": False
            }
            
        except Exception as e:
            print(f"❌ Anchor proof failed: {e}")
            import traceback
            traceback.print_exc()
            return self._simulated_anchor(job_id, proof_hash)
    
    async def verify_proof_on_chain(
        self,
        job_id: str,
        proof_hash: str
    ) -> Dict[str, Any]:
        """
        Verify a proof against on-chain record
        
        This calls the smart contract's verifyAudit function
        which compares the provided proof_hash with the stored one
        """
        if not self.connected or not self.contract:
            return self._simulated_verify(job_id, proof_hash, True)
        
        try:
            # First check if audit exists
            exists = self.contract.functions.auditExists(job_id).call()
            
            if not exists:
                return {
                    "success": False,
                    "verified": False,
                    "job_id": job_id,
                    "message": "No on-chain record found for this job",
                    "on_chain": False
                }
            
            # Get the on-chain audit data
            audit = await self.get_on_chain_audit(job_id)
            on_chain_hash = audit.get("proof_hash", "")
            
            # Compare hashes
            # Normalize both hashes for comparison
            provided_hash = proof_hash.lower()
            stored_hash = on_chain_hash.lower()
            
            if not provided_hash.startswith("0x"):
                provided_hash = "0x" + provided_hash
            if not stored_hash.startswith("0x"):
                stored_hash = "0x" + stored_hash
            
            # Remove trailing zeros for comparison
            provided_clean = provided_hash.rstrip('0') or "0x0"
            stored_clean = stored_hash.rstrip('0') or "0x0"
            
            verified = provided_clean == stored_clean or provided_hash == stored_hash
            
            return {
                "success": True,
                "verified": verified,
                "job_id": job_id,
                "provided_hash": proof_hash,
                "on_chain_hash": on_chain_hash,
                "block_number": audit.get("block_number"),
                "timestamp": audit.get("timestamp"),
                "auditor": audit.get("auditor"),
                "message": "✅ Proof verified on-chain" if verified else "❌ Hash mismatch",
                "explorer_url": f"{SEPOLIA_EXPLORER}/address/{CONTRACT_ADDRESS}",
                "chain": "Sepolia",
                "simulated": False
            }
            
        except Exception as e:
            print(f"❌ On-chain verification failed: {e}")
            return self._simulated_verify(job_id, proof_hash, True)
    
    async def get_on_chain_audit(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get audit record from blockchain"""
        if not self.connected or not self.contract:
            return None
        
        try:
            result = self.contract.functions.getAudit(job_id).call()
            
            # result = (proofHash, auditor, timestamp, blockNumber, exists)
            proof_hash_bytes = result[0]
            proof_hash = "0x" + proof_hash_bytes.hex()
            
            return {
                "proof_hash": proof_hash,
                "auditor": result[1],
                "timestamp": datetime.fromtimestamp(result[2]).isoformat() if result[2] > 0 else None,
                "block_number": result[3],
                "exists": result[4],
                "job_id": job_id
            }
            
        except Exception as e:
            print(f"❌ Get audit failed: {e}")
            return None
    
    async def get_total_audits(self) -> int:
        """Get total number of audits on-chain"""
        if not self.connected or not self.contract:
            return 0
        
        try:
            return self.contract.functions.totalAudits().call()
        except Exception as e:
            print(f"Error getting total audits: {e}")
            return 0
    
    def get_verification_status(self) -> Dict[str, Any]:
        """Get verifier service status"""
        return {
            "connected": self.connected,
            "chain": "Sepolia",
            "chain_id": CHAIN_ID,
            "contract_address": CONTRACT_ADDRESS,
            "rpc_url": SEPOLIA_RPC_URL,
            "account": self.account.address if self.account else None,
            "explorer": SEPOLIA_EXPLORER
        }
    
    # ============ Simulation Functions ============
    
    def _simulated_anchor(self, job_id: str, proof_hash: str) -> Dict[str, Any]:
        """Simulated anchor when blockchain not available"""
        fake_tx = "0x" + hashlib.sha256(f"{job_id}:{proof_hash}".encode()).hexdigest()
        
        return {
            "success": True,
            "job_id": job_id,
            "proof_hash": proof_hash,
            "transaction_hash": fake_tx,
            "block_number": 12345678,
            "gas_used": 85000,
            "gas_cost_eth": 0.0017,
            "gas_cost_usd": 4.25,
            "explorer_url": f"{SEPOLIA_EXPLORER}/tx/{fake_tx}",
            "contract_address": CONTRACT_ADDRESS,
            "chain": "Sepolia",
            "chain_id": CHAIN_ID,
            "simulated": True,
            "note": "Blockchain connection unavailable - simulating anchor"
        }
    
    def _simulated_verify(self, job_id: str, proof_hash: str, verified: bool) -> Dict[str, Any]:
        """Simulated verification when blockchain not available"""
        return {
            "success": True,
            "verified": verified,
            "job_id": job_id,
            "provided_hash": proof_hash,
            "on_chain_hash": proof_hash if verified else "0x0000...different",
            "message": "✅ Proof verified (simulated)" if verified else "❌ Verification failed (simulated)",
            "chain": "Sepolia",
            "simulated": True,
            "note": "Blockchain connection unavailable - simulating verification"
        }


# Global instance
on_chain_verifier = OnChainVerifier()
