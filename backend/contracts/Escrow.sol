// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title V-Inference Escrow Contract
 * @notice Manages escrow payments for AI inference marketplace
 * @dev Funds are locked until ZK proof is verified, then released to provider
 */
contract VInferenceEscrow {
    
    // ============ State Variables ============
    
    address public owner;
    address public verifierContract;
    
    // Escrow record for each job
    struct EscrowRecord {
        address buyer;
        address provider;
        uint256 amount;
        uint256 createdAt;
        bool isReleased;
        bool isRefunded;
        bytes32 proofHash;
    }
    
    // Job ID => Escrow Record
    mapping(bytes32 => EscrowRecord) public escrows;
    
    // User => Total locked amount
    mapping(address => uint256) public lockedBalance;
    
    // Provider => Total earnings
    mapping(address => uint256) public providerEarnings;
    
    // ============ Events ============
    
    event EscrowCreated(
        bytes32 indexed jobId,
        address indexed buyer,
        address indexed provider,
        uint256 amount
    );
    
    event EscrowReleased(
        bytes32 indexed jobId,
        address indexed provider,
        uint256 amount,
        bytes32 proofHash
    );
    
    event EscrowRefunded(
        bytes32 indexed jobId,
        address indexed buyer,
        uint256 amount,
        string reason
    );
    
    event VerifierUpdated(address indexed oldVerifier, address indexed newVerifier);
    
    // ============ Modifiers ============
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }
    
    modifier escrowExists(bytes32 jobId) {
        require(escrows[jobId].amount > 0, "Escrow does not exist");
        _;
    }
    
    modifier escrowNotSettled(bytes32 jobId) {
        require(!escrows[jobId].isReleased, "Already released");
        require(!escrows[jobId].isRefunded, "Already refunded");
        _;
    }
    
    // ============ Constructor ============
    
    constructor() {
        owner = msg.sender;
    }
    
    // ============ Main Functions ============
    
    /**
     * @notice Create escrow for an inference job
     * @param jobId Unique job identifier
     * @param provider Address of the model provider
     */
    function createEscrow(
        bytes32 jobId,
        address provider
    ) external payable {
        require(msg.value > 0, "Must send ETH");
        require(provider != address(0), "Invalid provider");
        require(provider != msg.sender, "Cannot escrow to self");
        require(escrows[jobId].amount == 0, "Escrow already exists");
        
        escrows[jobId] = EscrowRecord({
            buyer: msg.sender,
            provider: provider,
            amount: msg.value,
            createdAt: block.timestamp,
            isReleased: false,
            isRefunded: false,
            proofHash: bytes32(0)
        });
        
        lockedBalance[msg.sender] += msg.value;
        
        emit EscrowCreated(jobId, msg.sender, provider, msg.value);
    }
    
    /**
     * @notice Release escrow to provider after ZK proof verification
     * @param jobId The job ID
     * @param proofHash Hash of the verified ZK proof
     */
    function releaseEscrow(
        bytes32 jobId,
        bytes32 proofHash
    ) external 
        escrowExists(jobId) 
        escrowNotSettled(jobId) 
    {
        EscrowRecord storage escrow = escrows[jobId];
        
        // Only buyer or owner can release
        require(
            msg.sender == escrow.buyer || msg.sender == owner,
            "Not authorized"
        );
        
        // Mark as released
        escrow.isReleased = true;
        escrow.proofHash = proofHash;
        
        // Update balances
        lockedBalance[escrow.buyer] -= escrow.amount;
        providerEarnings[escrow.provider] += escrow.amount;
        
        // Transfer to provider
        (bool success, ) = payable(escrow.provider).call{value: escrow.amount}("");
        require(success, "Transfer failed");
        
        emit EscrowReleased(jobId, escrow.provider, escrow.amount, proofHash);
    }
    
    /**
     * @notice Release escrow with on-chain proof verification
     * @param jobId The job ID
     * @param proof The ZK proof data
     * @param publicInputs The public inputs for verification
     */
    function releaseWithProof(
        bytes32 jobId,
        bytes calldata proof,
        uint256[] calldata publicInputs
    ) external 
        escrowExists(jobId) 
        escrowNotSettled(jobId) 
    {
        require(verifierContract != address(0), "Verifier not set");
        
        // Call the verifier contract
        (bool verified, ) = verifierContract.call(
            abi.encodeWithSignature("verify(bytes,uint256[])", proof, publicInputs)
        );
        require(verified, "Proof verification failed");
        
        EscrowRecord storage escrow = escrows[jobId];
        
        // Mark as released
        escrow.isReleased = true;
        escrow.proofHash = keccak256(proof);
        
        // Update balances
        lockedBalance[escrow.buyer] -= escrow.amount;
        providerEarnings[escrow.provider] += escrow.amount;
        
        // Transfer to provider
        (bool success, ) = payable(escrow.provider).call{value: escrow.amount}("");
        require(success, "Transfer failed");
        
        emit EscrowReleased(jobId, escrow.provider, escrow.amount, escrow.proofHash);
    }
    
    /**
     * @notice Refund escrow to buyer (proof failed or timeout)
     * @param jobId The job ID
     * @param reason Reason for refund
     */
    function refundEscrow(
        bytes32 jobId,
        string calldata reason
    ) external 
        escrowExists(jobId) 
        escrowNotSettled(jobId) 
    {
        EscrowRecord storage escrow = escrows[jobId];
        
        // Only buyer or owner can refund
        require(
            msg.sender == escrow.buyer || msg.sender == owner,
            "Not authorized"
        );
        
        // Auto-refund after 24 hours if proof not submitted
        if (msg.sender == escrow.buyer) {
            require(
                block.timestamp > escrow.createdAt + 24 hours || msg.sender == owner,
                "Cannot refund yet"
            );
        }
        
        // Mark as refunded
        escrow.isRefunded = true;
        
        // Update balance
        lockedBalance[escrow.buyer] -= escrow.amount;
        
        // Transfer back to buyer
        (bool success, ) = payable(escrow.buyer).call{value: escrow.amount}("");
        require(success, "Transfer failed");
        
        emit EscrowRefunded(jobId, escrow.buyer, escrow.amount, reason);
    }
    
    // ============ View Functions ============
    
    /**
     * @notice Get escrow details
     */
    function getEscrow(bytes32 jobId) external view returns (
        address buyer,
        address provider,
        uint256 amount,
        uint256 createdAt,
        bool isReleased,
        bool isRefunded,
        bytes32 proofHash
    ) {
        EscrowRecord storage e = escrows[jobId];
        return (
            e.buyer,
            e.provider,
            e.amount,
            e.createdAt,
            e.isReleased,
            e.isRefunded,
            e.proofHash
        );
    }
    
    /**
     * @notice Check if escrow exists and is pending
     */
    function isPending(bytes32 jobId) external view returns (bool) {
        EscrowRecord storage e = escrows[jobId];
        return e.amount > 0 && !e.isReleased && !e.isRefunded;
    }
    
    // ============ Admin Functions ============
    
    /**
     * @notice Update the verifier contract address
     */
    function setVerifier(address _verifier) external onlyOwner {
        address old = verifierContract;
        verifierContract = _verifier;
        emit VerifierUpdated(old, _verifier);
    }
    
    /**
     * @notice Transfer ownership
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid address");
        owner = newOwner;
    }
    
    /**
     * @notice Emergency withdraw (only for stuck funds)
     */
    function emergencyWithdraw() external onlyOwner {
        (bool success, ) = payable(owner).call{value: address(this).balance}("");
        require(success, "Transfer failed");
    }
    
    // ============ Receive ETH ============
    
    receive() external payable {}
}
