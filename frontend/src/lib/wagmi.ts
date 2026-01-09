"use client";

import { createConfig, http } from "wagmi";
import { sepolia } from "wagmi/chains";
import { injected } from "wagmi/connectors";

// Sepolia configuration for V-Inference
export const config = createConfig({
    chains: [sepolia],
    connectors: [
        injected(), // MetaMask and other injected wallets
    ],
    transports: {
        [sepolia.id]: http("https://ethereum-sepolia-rpc.publicnode.com"),
    },
});

// Contract configuration
export const CONTRACT_ADDRESS = "0x93a8451B29af5c7596Ee569305e7eEe5C1e8ac52" as `0x${string}`;

export const CONTRACT_ABI = [
    {
        inputs: [
            { internalType: "bytes32", name: "proofHash", type: "bytes32" },
            { internalType: "string", name: "jobId", type: "string" },
        ],
        name: "anchorAudit",
        outputs: [{ internalType: "bool", name: "success", type: "bool" }],
        stateMutability: "nonpayable",
        type: "function",
    },
    {
        inputs: [
            { internalType: "string", name: "jobId", type: "string" },
            { internalType: "bytes32", name: "proofHash", type: "bytes32" },
        ],
        name: "verifyAudit",
        outputs: [
            { internalType: "bool", name: "valid", type: "bool" },
            { internalType: "bytes32", name: "onChainHash", type: "bytes32" },
        ],
        stateMutability: "nonpayable",
        type: "function",
    },
    {
        inputs: [{ internalType: "string", name: "jobId", type: "string" }],
        name: "auditExists",
        outputs: [{ internalType: "bool", name: "exists", type: "bool" }],
        stateMutability: "view",
        type: "function",
    },
    {
        inputs: [{ internalType: "string", name: "jobId", type: "string" }],
        name: "getAudit",
        outputs: [
            { internalType: "bytes32", name: "proofHash", type: "bytes32" },
            { internalType: "address", name: "auditor", type: "address" },
            { internalType: "uint256", name: "timestamp", type: "uint256" },
            { internalType: "uint256", name: "blockNumber", type: "uint256" },
            { internalType: "bool", name: "exists", type: "bool" },
        ],
        stateMutability: "view",
        type: "function",
    },
    {
        inputs: [],
        name: "totalAudits",
        outputs: [{ internalType: "uint256", name: "", type: "uint256" }],
        stateMutability: "view",
        type: "function",
    },
] as const;

// Sepolia chain info
export const SEPOLIA_CHAIN_ID = 11155111;
export const SEPOLIA_EXPLORER = "https://sepolia.etherscan.io";

// Helper to get explorer link
export function getExplorerTxLink(txHash: string): string {
    return `${SEPOLIA_EXPLORER}/tx/${txHash}`;
}

export function getExplorerAddressLink(address: string): string {
    return `${SEPOLIA_EXPLORER}/address/${address}`;
}
