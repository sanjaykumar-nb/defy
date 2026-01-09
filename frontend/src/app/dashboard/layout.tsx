"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAccount, useBalance, useConnect, useDisconnect } from "wagmi";
import { formatEther } from "viem";
import { SEPOLIA_CHAIN_ID, getExplorerAddressLink } from "@/lib/wagmi";

// Icons
const HomeIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
    </svg>
);

const CubeIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
    </svg>
);

const BoltIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
);

const ShopIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
    </svg>
);

const ShieldIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
);

const ArrowLeftIcon = () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
    </svg>
);

const WalletIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
    </svg>
);

const ExternalLinkIcon = () => (
    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
    </svg>
);

const navItems = [
    { href: "/dashboard", icon: HomeIcon, label: "Overview" },
    { href: "/dashboard/models", icon: CubeIcon, label: "My Models" },
    { href: "/dashboard/inference", icon: BoltIcon, label: "Inference" },
    { href: "/dashboard/marketplace", icon: ShopIcon, label: "Marketplace" },
];

function WalletButton() {
    const [mounted, setMounted] = useState(false);
    const { address, isConnected, chain } = useAccount();
    const { connect, connectors, isPending } = useConnect();
    const { disconnect } = useDisconnect();
    const { data: balance } = useBalance({ address });

    // Prevent hydration mismatch by only rendering wallet state after mount
    useEffect(() => {
        setMounted(true);
    }, []);

    const isWrongNetwork = chain && chain.id !== SEPOLIA_CHAIN_ID;

    // Show loading state until mounted (prevents SSR mismatch)
    if (!mounted) {
        return (
            <div className="p-4 rounded-2xl bg-[var(--glass-bg)] border border-[var(--glass-border)]">
                <div className="flex items-center justify-center py-2">
                    <div className="animate-pulse w-24 h-4 bg-[var(--glass-border)] rounded"></div>
                </div>
            </div>
        );
    }

    if (isConnected && address) {
        const shortAddress = `${address.slice(0, 6)}...${address.slice(-4)}`;
        const ethBalance = balance ? parseFloat(formatEther(balance.value)).toFixed(4) : "0.0000";

        return (
            <div className="p-4 rounded-2xl bg-[var(--glass-bg)] border border-[var(--glass-border)]">
                {/* Wallet Info */}
                <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--primary-500)] to-[var(--accent-500)] flex items-center justify-center text-lg font-bold">
                        {address.slice(2, 4).toUpperCase()}
                    </div>
                    <div>
                        <div className="font-medium">Connected</div>
                        <a
                            href={getExplorerAddressLink(address)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-[var(--foreground-muted)] hover:text-[var(--primary-400)] flex items-center gap-1"
                        >
                            {shortAddress}
                            <ExternalLinkIcon />
                        </a>
                    </div>
                </div>

                {/* Network Warning */}
                {isWrongNetwork && (
                    <div className="p-2 mb-3 rounded-lg bg-yellow-500/20 text-yellow-400 text-xs">
                        ⚠️ Switch to Sepolia network
                    </div>
                )}

                {/* Balance */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <WalletIcon />
                        <span className="text-[var(--secondary-400)] font-semibold">
                            {ethBalance} ETH
                        </span>
                    </div>
                    <span className="text-xs text-[var(--foreground-muted)]">
                        Sepolia
                    </span>
                </div>

                {/* Disconnect */}
                <button
                    onClick={() => disconnect()}
                    className="mt-3 w-full text-xs text-[var(--foreground-muted)] hover:text-red-400 transition-colors"
                >
                    Disconnect
                </button>
            </div>
        );
    }

    return (
        <div className="p-4 rounded-2xl bg-[var(--glass-bg)] border border-[var(--glass-border)]">
            <button
                onClick={() => connect({ connector: connectors[0] })}
                disabled={isPending}
                className="w-full btn btn-primary text-sm"
            >
                {isPending ? (
                    <>
                        <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
                        Connecting...
                    </>
                ) : (
                    <>
                        <WalletIcon />
                        Connect MetaMask
                    </>
                )}
            </button>
            <p className="text-xs text-[var(--foreground-muted)] text-center mt-2">
                Connect to Sepolia testnet
            </p>
        </div>
    );
}

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();

    return (
        <div className="min-h-screen flex">
            {/* Sidebar */}
            <aside className="w-72 border-r border-[var(--glass-border)] bg-[var(--glass-bg)]/50 backdrop-blur-xl flex flex-col">
                {/* Logo */}
                <div className="p-6 border-b border-[var(--glass-border)]">
                    <Link href="/" className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--primary-500)] to-[var(--accent-500)] flex items-center justify-center">
                            <ShieldIcon />
                        </div>
                        <span className="text-xl font-bold">V-Inference</span>
                    </Link>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-4 space-y-2">
                    {navItems.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${isActive
                                    ? "bg-[var(--primary-500)] text-white"
                                    : "text-[var(--foreground-muted)] hover:bg-[var(--glass-bg)] hover:text-white"
                                    }`}
                            >
                                <item.icon />
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>

                {/* Wallet Section - Now Real MetaMask! */}
                <div className="p-4 border-t border-[var(--glass-border)]">
                    <WalletButton />

                    {/* Back to Home */}
                    <Link
                        href="/"
                        className="flex items-center gap-2 mt-4 text-sm text-[var(--foreground-muted)] hover:text-white transition-colors"
                    >
                        <ArrowLeftIcon />
                        Back to Home
                    </Link>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <div className="container mx-auto max-w-6xl p-8">{children}</div>
            </main>
        </div>
    );
}
