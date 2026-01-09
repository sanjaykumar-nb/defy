"use client";

import { useState } from "react";
import { useReadContract, useWriteContract, useWaitForTransactionReceipt } from "wagmi";
import { CONTRACT_ADDRESS, CONTRACT_ABI, getExplorerTxLink } from "@/lib/wagmi";

// Icons
const ShieldIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
);

const CheckIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
);

const XIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
);

const ExternalLinkIcon = () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
    </svg>
);

interface ProofVerifierProps {
    jobId: string;
    proofHash?: string;
    txHash?: string;
}

export function ProofVerifier({ jobId, proofHash, txHash }: ProofVerifierProps) {
    const [verifying, setVerifying] = useState(false);

    // Read audit from contract
    const { data: auditExists, isLoading: checkingExists } = useReadContract({
        address: CONTRACT_ADDRESS,
        abi: CONTRACT_ABI,
        functionName: "auditExists",
        args: [jobId],
    });

    // Get audit details
    const { data: auditData, isLoading: loadingAudit } = useReadContract({
        address: CONTRACT_ADDRESS,
        abi: CONTRACT_ABI,
        functionName: "getAudit",
        args: [jobId],
    });

    const isLoading = checkingExists || loadingAudit;

    if (isLoading) {
        return (
            <div className="p-4 rounded-xl bg-[var(--glass-bg)] flex items-center gap-3">
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-[var(--primary-500)]"></div>
                <span className="text-sm">Checking on-chain...</span>
            </div>
        );
    }

    if (!auditExists) {
        return (
            <div className="p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/30">
                <div className="flex items-center gap-2 text-yellow-400">
                    <ShieldIcon />
                    <span className="font-medium">Not on-chain</span>
                </div>
                <p className="text-sm text-[var(--foreground-muted)] mt-1">
                    This proof has not been anchored to Sepolia yet.
                </p>
            </div>
        );
    }

    // Parse audit data
    const [onChainHash, auditor, timestamp, blockNumber, exists] = auditData || [];

    const onChainHashHex = onChainHash ? `0x${Buffer.from(onChainHash as Uint8Array).toString("hex")}` : "";
    const proofMatches = proofHash && onChainHashHex.toLowerCase() === proofHash.toLowerCase();

    return (
        <div className={`p-4 rounded-xl ${proofMatches ? "bg-[var(--secondary-500)]/10 border border-[var(--secondary-500)]/30" : "bg-red-500/10 border border-red-500/30"}`}>
            <div className="flex items-center gap-2 mb-3">
                {proofMatches ? (
                    <>
                        <CheckIcon />
                        <span className="font-semibold text-[var(--secondary-400)]">Verified On-Chain ✓</span>
                    </>
                ) : (
                    <>
                        <XIcon />
                        <span className="font-semibold text-red-400">Hash Mismatch</span>
                    </>
                )}
            </div>

            <div className="space-y-2 text-sm">
                <div className="flex items-start justify-between">
                    <span className="text-[var(--foreground-muted)]">On-Chain Hash</span>
                    <span className="font-mono text-xs max-w-[180px] truncate">
                        {onChainHashHex.slice(0, 20)}...
                    </span>
                </div>

                <div className="flex items-center justify-between">
                    <span className="text-[var(--foreground-muted)]">Block #</span>
                    <span>{blockNumber?.toString()}</span>
                </div>

                <div className="flex items-center justify-between">
                    <span className="text-[var(--foreground-muted)]">Auditor</span>
                    <span className="font-mono text-xs">
                        {auditor ? `${(auditor as string).slice(0, 8)}...${(auditor as string).slice(-6)}` : "-"}
                    </span>
                </div>

                <div className="flex items-center justify-between">
                    <span className="text-[var(--foreground-muted)]">Timestamp</span>
                    <span>{timestamp ? new Date(Number(timestamp) * 1000).toLocaleString() : "-"}</span>
                </div>

                {txHash && (
                    <a
                        href={getExplorerTxLink(txHash)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-[var(--primary-400)] hover:underline mt-2"
                    >
                        View on Etherscan
                        <ExternalLinkIcon />
                    </a>
                )}
            </div>
        </div>
    );
}

// Component to verify a TX hash directly
export function TxHashVerifier({ txHash }: { txHash: string }) {
    const [verificationResult, setVerificationResult] = useState<{
        status: "pending" | "success" | "failed";
        blockNumber?: number;
    } | null>(null);

    // This would query the blockchain for the TX
    // For now, show link to Etherscan
    return (
        <div className="p-4 rounded-xl bg-[var(--glass-bg)]">
            <div className="flex items-center justify-between">
                <span className="text-sm text-[var(--foreground-muted)]">Transaction</span>
                <a
                    href={getExplorerTxLink(txHash)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-[var(--primary-400)] hover:underline text-sm"
                >
                    {txHash.slice(0, 12)}...{txHash.slice(-8)}
                    <ExternalLinkIcon />
                </a>
            </div>
            <p className="text-xs text-[var(--foreground-muted)] mt-2">
                Click to verify on Sepolia Etherscan
            </p>
        </div>
    );
}

// Hook to anchor proof on-chain using user's wallet
export function useAnchorProof() {
    const { writeContract, data: hash, isPending, error } = useWriteContract();
    const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({ hash });

    const anchorProof = async (jobId: string, proofHash: string) => {
        // Convert proof hash to bytes32
        const proofBytes = proofHash.startsWith("0x") ? proofHash : `0x${proofHash}`;

        writeContract({
            address: CONTRACT_ADDRESS,
            abi: CONTRACT_ABI,
            functionName: "anchorAudit",
            args: [proofBytes as `0x${string}`, jobId],
        });
    };

    return {
        anchorProof,
        hash,
        isPending,
        isConfirming,
        isSuccess,
        error,
    };
}
