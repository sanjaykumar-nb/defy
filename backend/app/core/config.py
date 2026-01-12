"""
V-Inference Backend - Configuration
Real Sepolia Testnet Integration with IPFS Decentralized Storage
"""
import os

# Flask/FastAPI Configuration
DEBUG = True
HOST = "0.0.0.0"
PORT = 8000

# Database (JSON for simplicity)
STORAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "storage")

# ============ IPFS Configuration (Decentralized Storage) ============
# Provider options: "pinata", "infura", "local", "web3storage"
IPFS_PROVIDER = os.getenv("IPFS_PROVIDER", "local")

# Pinata (recommended for production) - https://pinata.cloud
PINATA_API_KEY = os.getenv("PINATA_API_KEY", "")
PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY", "")

# Infura IPFS - https://infura.io
INFURA_IPFS_PROJECT_ID = os.getenv("INFURA_IPFS_PROJECT_ID", "")
INFURA_IPFS_PROJECT_SECRET = os.getenv("INFURA_IPFS_PROJECT_SECRET", "")

# Local IPFS node
LOCAL_IPFS_API = os.getenv("LOCAL_IPFS_API", "http://127.0.0.1:5001")

# IPFS Gateways for retrieval
IPFS_GATEWAYS = [
    "https://ipfs.io/ipfs/",
    "https://gateway.pinata.cloud/ipfs/",
    "https://cloudflare-ipfs.com/ipfs/",
    "https://dweb.link/ipfs/"
]

# Blockchain Configuration (Sepolia Testnet)
SEPOLIA_RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
CHAIN_ID = 11155111  # Sepolia Chain ID

# Contract Address - Deployed on Sepolia
CONTRACT_ADDRESS = "0x93a8451B29af5c7596Ee569305e7eEe5C1e8ac52"

# Escrow Contract Address - Deployed on Sepolia (VInferenceEscrow)
ESCROW_CONTRACT_ADDRESS = "0x705a74473F52024dCF54c1F6d78B4D4B4d8A2F73"

# Private Key - For signing transactions
# WARNING: In production, use environment variables!
PRIVATE_KEY = "e94eeecc753a37660a42995832aa9bfd283d8abe44446dfe6bd798a879aecff8"

# AI Model Configuration
MODEL_VERSION = "v-inference-v1.0.0"
MODEL_NAME = "V-Inference-ZKML-Model"

# Proof Generation
PROOF_VERSION = "zkml-v1"

# Contract ABI
CONTRACT_ABI = [
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
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "string", "name": "jobId", "type": "string"},
            {"indexed": False, "internalType": "bytes32", "name": "proofHash", "type": "bytes32"},
            {"indexed": True, "internalType": "address", "name": "auditor", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"}
        ],
        "name": "AuditAnchored",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "string", "name": "jobId", "type": "string"},
            {"indexed": False, "internalType": "bytes32", "name": "proofHash", "type": "bytes32"},
            {"indexed": False, "internalType": "bool", "name": "valid", "type": "bool"},
            {"indexed": True, "internalType": "address", "name": "verifier", "type": "address"}
        ],
        "name": "AuditVerified",
        "type": "event"
    },
    {
        "inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}],
        "name": "transferOwnership",
        "outputs": [],
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
        "inputs": [{"internalType": "string", "name": "", "type": "string"}],
        "name": "audits",
        "outputs": [
            {"internalType": "bytes32", "name": "proofHash", "type": "bytes32"},
            {"internalType": "string", "name": "jobId", "type": "string"},
            {"internalType": "address", "name": "auditor", "type": "address"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "uint256", "name": "blockNumber", "type": "uint256"},
            {"internalType": "bool", "name": "exists", "type": "bool"}
        ],
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
        "name": "getAuditCount",
        "outputs": [{"internalType": "uint256", "name": "count", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "index", "type": "uint256"}],
        "name": "getJobIdByIndex",
        "outputs": [{"internalType": "string", "name": "jobId", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "count", "type": "uint256"}],
        "name": "getRecentAudits",
        "outputs": [{"internalType": "string[]", "name": "recentJobIds", "type": "string[]"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "jobIds",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "NAME",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalAudits",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "VERSION",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Sepolia Block Explorer
SEPOLIA_EXPLORER = "https://sepolia.etherscan.io"
