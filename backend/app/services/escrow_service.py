"""
V-Inference Backend - Escrow Service
Real ETH Escrow via VInferenceEscrow smart contract on Sepolia
Handles trustless payments between buyers and model providers
"""
import os
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from web3 import Web3

from ..core.config import (
    SEPOLIA_RPC_URL, 
    CHAIN_ID, 
    PRIVATE_KEY,
    ESCROW_CONTRACT_ADDRESS,
    SEPOLIA_EXPLORER
)

# Escrow Contract ABI (key functions only)
ESCROW_ABI = [
    {
        "inputs": [
            {"name": "jobId", "type": "bytes32"},
            {"name": "provider", "type": "address"}
        ],
        "name": "createEscrow",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "jobId", "type": "bytes32"},
            {"name": "proofHash", "type": "bytes32"}
        ],
        "name": "releaseEscrow",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "jobId", "type": "bytes32"},
            {"name": "reason", "type": "string"}
        ],
        "name": "refundEscrow",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "jobId", "type": "bytes32"}],
        "name": "getEscrow",
        "outputs": [
            {"name": "buyer", "type": "address"},
            {"name": "provider", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "createdAt", "type": "uint256"},
            {"name": "isReleased", "type": "bool"},
            {"name": "isRefunded", "type": "bool"},
            {"name": "proofHash", "type": "bytes32"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "jobId", "type": "bytes32"}],
        "name": "isPending",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "jobId", "type": "bytes32"},
            {"indexed": True, "name": "buyer", "type": "address"},
            {"indexed": True, "name": "provider", "type": "address"},
            {"indexed": False, "name": "amount", "type": "uint256"}
        ],
        "name": "EscrowCreated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "jobId", "type": "bytes32"},
            {"indexed": True, "name": "provider", "type": "address"},
            {"indexed": False, "name": "amount", "type": "uint256"},
            {"indexed": False, "name": "proofHash", "type": "bytes32"}
        ],
        "name": "EscrowReleased",
        "type": "event"
    }
]


class EscrowService:
    """
    Real ETH Escrow Service for V-Inference Marketplace
    
    DECENTRALIZED PAYMENT FLOW:
    1. Buyer purchases inference → ETH locked in smart contract
    2. Provider runs inference → Generates ZK proof
    3. Proof anchored on-chain → Verification
    4. On successful verification → ETH released to provider
    5. On failed verification → ETH refunded to buyer
    
    This removes the need to trust any centralized party!
    """
    
    def __init__(self):
        self.connected = False
        self.w3 = None
        self.account = None
        self.contract = None
        self.contract_address = ESCROW_CONTRACT_ADDRESS
        
        self._connect()
    
    def _connect(self):
        """Connect to Sepolia and initialize escrow contract"""
        try:
            if not SEPOLIA_RPC_URL:
                print("⚠️ Escrow: No RPC URL configured")
                return
            
            self.w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
            
            if not self.w3.is_connected():
                print("⚠️ Escrow: Failed to connect to Sepolia")
                return
            
            # Setup account
            if PRIVATE_KEY:
                self.account = self.w3.eth.account.from_key(PRIVATE_KEY)
                balance = self.w3.eth.get_balance(self.account.address)
                balance_eth = float(self.w3.from_wei(balance, 'ether'))
                print(f"💰 Escrow account: {self.account.address} ({balance_eth:.4f} ETH)")
            
            # Setup contract if address is configured
            if self.contract_address:
                self.contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(self.contract_address),
                    abi=ESCROW_ABI
                )
                print(f"✅ Escrow contract connected: {self.contract_address}")
                self.connected = True
            else:
                print("⚠️ Escrow: Contract address not set")
                self.connected = False
            
        except Exception as e:
            print(f"❌ Escrow connection error: {e}")
            self.connected = False
    
    def job_id_to_bytes32(self, job_id: str) -> bytes:
        """Convert job ID string to bytes32"""
        # Pad or hash the job_id to get exactly 32 bytes
        if job_id.startswith("0x"):
            job_id = job_id[2:]
        
        # If it's already a valid hex, use it
        if len(job_id) == 64:
            return bytes.fromhex(job_id)
        
        # Otherwise, hash the job_id
        import hashlib
        return hashlib.sha256(job_id.encode()).digest()
    
    async def create_escrow(
        self,
        job_id: str,
        provider_address: str,
        amount_eth: float
    ) -> Dict[str, Any]:
        """
        Create escrow for an inference job
        Locks ETH in the contract until proof is verified
        """
        if not self.connected or not self.contract:
            return self._simulated_escrow_create(job_id, provider_address, amount_eth)
        
        try:
            job_bytes = self.job_id_to_bytes32(job_id)
            amount_wei = self.w3.to_wei(amount_eth, 'ether')
            
            # Build transaction
            tx = self.contract.functions.createEscrow(
                job_bytes,
                Web3.to_checksum_address(provider_address)
            ).build_transaction({
                'from': self.account.address,
                'value': amount_wei,
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': CHAIN_ID
            })
            
            # Sign and send
            signed = self.w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            
            return {
                "success": True,
                "job_id": job_id,
                "amount_eth": amount_eth,
                "transaction_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "status": "locked",
                "simulated": False
            }
            
        except Exception as e:
            print(f"❌ Create escrow failed: {e}")
            return self._simulated_escrow_create(job_id, provider_address, amount_eth)
    
    async def release_escrow(
        self,
        job_id: str,
        proof_hash: str
    ) -> Dict[str, Any]:
        """
        Release escrow to provider after proof verification
        """
        if not self.connected or not self.contract:
            return self._simulated_escrow_release(job_id, proof_hash)
        
        try:
            job_bytes = self.job_id_to_bytes32(job_id)
            
            # Convert proof_hash to bytes32
            if proof_hash.startswith("0x"):
                proof_bytes = bytes.fromhex(proof_hash[2:])
            else:
                proof_bytes = bytes.fromhex(proof_hash)
            
            # Build transaction
            tx = self.contract.functions.releaseEscrow(
                job_bytes,
                proof_bytes
            ).build_transaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': CHAIN_ID
            })
            
            # Sign and send
            signed = self.w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            
            return {
                "success": True,
                "job_id": job_id,
                "transaction_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "status": "released",
                "simulated": False
            }
            
        except Exception as e:
            print(f"❌ Release escrow failed: {e}")
            return self._simulated_escrow_release(job_id, proof_hash)
    
    async def refund_escrow(
        self,
        job_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Refund escrow to buyer (proof failed or timeout)
        """
        if not self.connected or not self.contract:
            return self._simulated_escrow_refund(job_id, reason)
        
        try:
            job_bytes = self.job_id_to_bytes32(job_id)
            
            # Build transaction
            tx = self.contract.functions.refundEscrow(
                job_bytes,
                reason
            ).build_transaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'chainId': CHAIN_ID
            })
            
            # Sign and send
            signed = self.w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            
            return {
                "success": True,
                "job_id": job_id,
                "reason": reason,
                "transaction_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "status": "refunded",
                "simulated": False
            }
            
        except Exception as e:
            print(f"❌ Refund escrow failed: {e}")
            return self._simulated_escrow_refund(job_id, reason)
    
    async def get_escrow(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get escrow details for a job"""
        if not self.connected or not self.contract:
            return None
        
        try:
            job_bytes = self.job_id_to_bytes32(job_id)
            result = self.contract.functions.getEscrow(job_bytes).call()
            
            return {
                "buyer": result[0],
                "provider": result[1],
                "amount_wei": result[2],
                "amount_eth": self.w3.from_wei(result[2], 'ether'),
                "created_at": datetime.fromtimestamp(result[3]).isoformat(),
                "is_released": result[4],
                "is_refunded": result[5],
                "proof_hash": result[6].hex()
            }
            
        except Exception as e:
            print(f"❌ Get escrow failed: {e}")
            return None
    
    # ============ Simulated Functions (Fallback) ============
    
    def _simulated_escrow_create(
        self, 
        job_id: str, 
        provider: str, 
        amount: float
    ) -> Dict[str, Any]:
        """Simulated escrow creation when contract not available"""
        return {
            "success": True,
            "job_id": job_id,
            "amount_eth": amount,
            "status": "locked",
            "simulated": True,
            "note": "Escrow contract not deployed - simulating lock"
        }
    
    def _simulated_escrow_release(
        self, 
        job_id: str, 
        proof_hash: str
    ) -> Dict[str, Any]:
        """Simulated escrow release"""
        return {
            "success": True,
            "job_id": job_id,
            "proof_hash": proof_hash,
            "status": "released",
            "simulated": True,
            "note": "Escrow contract not deployed - simulating release"
        }
    
    def _simulated_escrow_refund(
        self, 
        job_id: str, 
        reason: str
    ) -> Dict[str, Any]:
        """Simulated escrow refund"""
        return {
            "success": True,
            "job_id": job_id,
            "reason": reason,
            "status": "refunded",
            "simulated": True,
            "note": "Escrow contract not deployed - simulating refund"
        }


# Global instance
escrow_service = EscrowService()
