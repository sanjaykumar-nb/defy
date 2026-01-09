"""
V-Inference Backend - Blockchain Integration
Based on NeuralLex BlockchainConnector implementation
Handles interaction with the Sepolia testnet smart contract
"""
from web3 import Web3
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib

from .config import (
    SEPOLIA_RPC_URL,
    CHAIN_ID,
    CONTRACT_ADDRESS,
    PRIVATE_KEY,
    CONTRACT_ABI,
    SEPOLIA_EXPLORER
)


class BlockchainService:
    """
    Connects to Sepolia testnet and interacts with V-Inference smart contract
    
    Functions:
    - anchor_proof: Store proof hash on-chain
    - get_audit: Retrieve audit from contract
    - verify_on_chain: Verify proof matches on-chain record
    """
    
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
        self.chain_id = CHAIN_ID
        self.contract_address = CONTRACT_ADDRESS
        self.contract = None
        self.account = None
        self.connected = False
        
        # Initialize connection
        self._init_connection()
    
    def _init_connection(self):
        """Initialize Web3 connection and contract"""
        if self.w3.is_connected():
            self.connected = True
            print(f"✅ Connected to Sepolia (Chain ID: {self.chain_id})")
            
            # Initialize contract
            if self.contract_address:
                self.contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(self.contract_address),
                    abi=CONTRACT_ABI
                )
            
            # Initialize account if private key available
            if PRIVATE_KEY:
                self.account = self.w3.eth.account.from_key(PRIVATE_KEY)
                print(f"📝 Using account: {self.account.address}")
                
                # Show balance
                balance = self.get_balance()
                print(f"💰 Account balance: {balance:.4f} ETH")
        else:
            print("❌ Failed to connect to Sepolia")
            self.connected = False
    
    def get_balance(self) -> float:
        """Get wallet ETH balance"""
        if self.account:
            balance_wei = self.w3.eth.get_balance(self.account.address)
            return float(self.w3.from_wei(balance_wei, 'ether'))
        return 0.0
    
    def generate_proof_hash(self, job_id: str, input_data: Dict, output_data: Dict) -> str:
        """Generate a proof hash from inference data"""
        import json
        proof_input = json.dumps({
            "job_id": job_id,
            "input": input_data,
            "output": output_data,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "zkml-v1"
        }, sort_keys=True)
        
        hash_bytes = hashlib.sha256(proof_input.encode()).digest()
        return "0x" + hash_bytes.hex()
    
    def anchor_proof(self, job_id: str, proof_hash: str) -> Dict[str, Any]:
        """
        Anchor a proof hash on the blockchain using anchorAudit function
        
        Args:
            job_id: Unique job identifier
            proof_hash: The proof hash (hex string starting with 0x)
            
        Returns:
            Transaction result with tx_hash and status
        """
        if not self.contract or not self.account:
            return {
                "success": False,
                "error": "Blockchain not configured (no contract or wallet)",
                "simulated": True,
                "transaction_hash": self._simulate_tx_hash(job_id)
            }
        
        try:
            # Check if audit already exists on-chain to avoid revert
            try:
                exists = self.contract.functions.auditExists(job_id).call()
                if exists:
                    print(f"⚠️ Audit {job_id} already exists on-chain, skipping anchor")
                    # Get existing audit info
                    audit = self.get_audit(job_id)
                    return {
                        "success": True,
                        "already_anchored": True,
                        "job_id": job_id,
                        "message": "Audit already exists on-chain",
                        "block_number": audit.get("block_number") if audit else None,
                        "simulated": False
                    }
            except Exception as check_error:
                print(f"Warning: Could not check if audit exists: {check_error}")
            
            # Get current nonce
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # Ensure proof_hash is properly formatted
            if not proof_hash.startswith("0x"):
                proof_hash = "0x" + proof_hash
            
            # Ensure 64 hex chars (32 bytes) after 0x
            clean_hash = proof_hash[2:]
            if len(clean_hash) < 64:
                clean_hash = clean_hash.ljust(64, '0')
            elif len(clean_hash) > 64:
                clean_hash = clean_hash[:64]
            
            # Convert to bytes32 for contract call
            proof_bytes32 = bytes.fromhex(clean_hash)
            
            print(f"⛓️ Anchoring proof for job {job_id}...")
            print(f"   Proof: 0x{clean_hash[:16]}...")
            
            # Get gas price
            gas_price = self.w3.eth.gas_price
            
            # Build transaction using anchorAudit(proofHash, jobId)
            tx = self.contract.functions.anchorAudit(
                proof_bytes32,   # proofHash (bytes32)
                job_id           # jobId (string)
            ).build_transaction({
                'chainId': self.chain_id,
                'gas': 500000,
                'gasPrice': gas_price,
                'nonce': nonce
            })
            
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hex = self.w3.to_hex(tx_hash)
            
            print(f"📤 Transaction sent: {tx_hex}")
            
            # Wait for receipt (with timeout)
            try:
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
                
                gas_used = receipt['gasUsed']
                gas_cost_wei = gas_used * gas_price
                gas_cost_eth = float(self.w3.from_wei(gas_cost_wei, 'ether'))
                
                print(f"✅ Transaction confirmed in block {receipt['blockNumber']}")
                
                return {
                    "success": True,
                    "transaction_hash": tx_hex,
                    "block_number": receipt['blockNumber'],
                    "gas_used": gas_used,
                    "gas_cost_eth": gas_cost_eth,
                    "gas_cost_usd": gas_cost_eth * 2500,  # Approximate ETH price
                    "explorer_url": f"{SEPOLIA_EXPLORER}/tx/{tx_hex}",
                    "contract_address": self.contract_address,
                    "chain": "Sepolia",
                    "chain_id": self.chain_id,
                    "status": "CONFIRMED",
                    "simulated": False
                }
                
            except Exception as wait_error:
                # Transaction sent but not yet confirmed
                print(f"⏳ Transaction pending: {wait_error}")
                return {
                    "success": True,
                    "transaction_hash": tx_hex,
                    "explorer_url": f"{SEPOLIA_EXPLORER}/tx/{tx_hex}",
                    "status": "PENDING",
                    "simulated": False
                }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Blockchain error: {error_msg}")
            
            # Return error with simulated fallback
            return {
                "success": False,
                "error": error_msg,
                "simulated": True,
                "transaction_hash": self._simulate_tx_hash(job_id)
            }
    
    def get_audit(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an audit record from the blockchain
        
        Args:
            job_id: The job ID to look up
            
        Returns:
            Audit record or None if not found
        """
        if not self.contract:
            return None
        
        try:
            # Call getAudit function
            result = self.contract.functions.getAudit(job_id).call()
            proof_hash, auditor, timestamp, block_num, exists = result
            
            if not exists:
                return None
            
            # Convert bytes32 proof hash to hex string
            proof_hex = "0x" + proof_hash.hex()
            
            return {
                "job_id": job_id,
                "proof_hash": proof_hex,
                "auditor": auditor,
                "timestamp": timestamp,
                "block_number": block_num,
                "exists": exists
            }
        except Exception as e:
            print(f"Error reading from chain: {e}")
            return None
    
    def check_audit_exists(self, job_id: str) -> bool:
        """Check if an audit already exists on-chain"""
        if not self.contract:
            return False
        
        try:
            return self.contract.functions.auditExists(job_id).call()
        except Exception as e:
            print(f"Error checking audit exists: {e}")
            return False
    
    def verify_on_chain(self, job_id: str, proof_hash: str) -> Dict[str, Any]:
        """
        Verify a proof matches the on-chain record
        
        Args:
            job_id: The job ID to verify
            proof_hash: The proof hash to verify
            
        Returns:
            Verification result
        """
        on_chain_audit = self.get_audit(job_id)
        
        if not on_chain_audit:
            return {
                "verified": False,
                "reason": "Audit not found on chain",
                "job_id": job_id
            }
        
        on_chain_hash = on_chain_audit.get("proof_hash", "")
        
        # Normalize hashes for comparison
        if not proof_hash.startswith("0x"):
            proof_hash = "0x" + proof_hash
        
        matches = on_chain_hash.lower() == proof_hash.lower()
        
        return {
            "verified": matches,
            "job_id": job_id,
            "submitted_hash": proof_hash,
            "on_chain_hash": on_chain_hash,
            "auditor": on_chain_audit.get("auditor"),
            "timestamp": on_chain_audit.get("timestamp"),
            "block_number": on_chain_audit.get("block_number")
        }
    
    def get_total_audits(self) -> int:
        """Get total number of audits on-chain"""
        if not self.contract:
            return 0
        try:
            return self.contract.functions.totalAudits().call()
        except:
            return 0
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get current network information"""
        if not self.connected:
            return {
                "connected": False,
                "chain": "Sepolia",
                "status": "Disconnected"
            }
        
        try:
            return {
                "connected": True,
                "chain": "Sepolia",
                "chain_id": self.chain_id,
                "rpc_url": SEPOLIA_RPC_URL,
                "contract_address": self.contract_address,
                "account_address": self.account.address if self.account else None,
                "balance_eth": self.get_balance(),
                "total_audits": self.get_total_audits(),
                "explorer": SEPOLIA_EXPLORER,
                "status": "Connected"
            }
        except Exception as e:
            return {
                "connected": False,
                "chain": "Sepolia",
                "status": f"Error: {e}"
            }
    
    def _simulate_tx_hash(self, job_id: str) -> str:
        """Generate a simulated transaction hash for demo purposes"""
        data = f"{job_id}{datetime.now().isoformat()}"
        return "0x" + hashlib.sha256(data.encode()).hexdigest()


# Global blockchain service instance
blockchain_service = BlockchainService()
