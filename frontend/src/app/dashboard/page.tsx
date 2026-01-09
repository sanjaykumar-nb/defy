"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import * as api from "@/lib/api";

// Icons
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

const ShieldIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
);

const ChartIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
);

const ArrowRightIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
    </svg>
);

const ClockIcon = () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

const CheckIcon = () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
);

const XIcon = () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
);

interface Stats {
    total_models: number;
    total_inferences: number;
    verified_inferences: number;
    active_listings: number;
    verification_rate: number;
}

interface Model {
    id: string;
    name: string;
    model_type: string;
    total_inferences: number;
    created_at: string;
}

interface Job {
    id: string;
    model_id: string;
    status: string;
    latency_ms: number;
    proof_hash?: string;
    verification_status?: string;
    created_at: string;
}

function StatCard({
    icon,
    label,
    value,
    subValue,
    color,
}: {
    icon: React.ReactNode;
    label: string;
    value: string | number;
    subValue?: string;
    color: string;
}) {
    return (
        <div className="glass-card p-6 hover-lift">
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-[var(--foreground-muted)] text-sm mb-1">{label}</p>
                    <p className={`text-3xl font-bold ${color}`}>{value}</p>
                    {subValue && (
                        <p className="text-xs text-[var(--foreground-muted)] mt-1">{subValue}</p>
                    )}
                </div>
                <div className={`p-3 rounded-xl ${color} bg-opacity-20`}>{icon}</div>
            </div>
        </div>
    );
}

function QuickAction({
    href,
    icon,
    label,
    description,
}: {
    href: string;
    icon: React.ReactNode;
    label: string;
    description: string;
}) {
    return (
        <Link href={href} className="glass-card p-6 hover-lift group">
            <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[var(--primary-500)] to-[var(--accent-500)] flex items-center justify-center text-white">
                    {icon}
                </div>
                <div className="flex-1">
                    <h3 className="font-semibold group-hover:text-[var(--primary-400)] transition-colors">
                        {label}
                    </h3>
                    <p className="text-sm text-[var(--foreground-muted)]">{description}</p>
                </div>
                <ArrowRightIcon />
            </div>
        </Link>
    );
}

function RecentJobRow({ job, modelName }: { job: Job; modelName: string }) {
    const isVerified = job.status === "verified" || job.proof_hash;
    const isFailed = job.status === "failed";
    const isProcessing = job.status === "processing" || job.status === "pending";

    return (
        <div className="flex items-center gap-4 p-4 rounded-xl bg-[var(--glass-bg)] hover:bg-[var(--glass-border)] transition-colors">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isVerified ? "bg-[var(--secondary-500)]/20 text-[var(--secondary-400)]" :
                    isFailed ? "bg-red-500/20 text-red-400" :
                        "bg-[var(--primary-500)]/20 text-[var(--primary-400)]"
                }`}>
                {isVerified ? <CheckIcon /> : isFailed ? <XIcon /> : <BoltIcon />}
            </div>
            <div className="flex-1 min-w-0">
                <div className="font-medium truncate">{modelName}</div>
                <div className="text-xs text-[var(--foreground-muted)] flex items-center gap-2">
                    <ClockIcon />
                    {job.latency_ms ? `${job.latency_ms}ms` : "Processing..."}
                </div>
            </div>
            <div className="flex items-center gap-2">
                {isVerified ? (
                    <span className="badge badge-success flex items-center gap-1">
                        <ShieldIcon /> Verified
                    </span>
                ) : isFailed ? (
                    <span className="badge bg-red-500/20 text-red-400">Failed</span>
                ) : isProcessing ? (
                    <span className="badge badge-primary">Processing</span>
                ) : (
                    <span className="badge bg-yellow-500/20 text-yellow-400">Not Verified</span>
                )}
            </div>
        </div>
    );
}

export default function DashboardPage() {
    const [stats, setStats] = useState<Stats>({
        total_models: 0,
        total_inferences: 0,
        verified_inferences: 0,
        active_listings: 0,
        verification_rate: 0,
    });
    const [recentModels, setRecentModels] = useState<Model[]>([]);
    const [recentJobs, setRecentJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch platform stats from backend
                const statsRes = await api.getPlatformStats();
                if (statsRes.stats) {
                    setStats({
                        total_models: statsRes.stats.total_models || 0,
                        total_inferences: statsRes.stats.total_inferences || 0,
                        verified_inferences: statsRes.stats.verified_inferences || 0,
                        active_listings: statsRes.stats.active_listings || 0,
                        verification_rate: statsRes.stats.verification_rate || 0,
                    });
                }

                // Fetch models from backend
                const modelsRes = await api.getModels();
                if (modelsRes.success && modelsRes.data) {
                    setRecentModels(modelsRes.data.slice(0, 4));
                }

                // Fetch jobs from backend
                const jobsRes = await api.getJobs();
                if (jobsRes.success && jobsRes.data) {
                    setRecentJobs(jobsRes.data.slice(0, 6));
                }

            } catch (err) {
                console.error("Error fetching dashboard data:", err);
                setError("Failed to connect to backend");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    // Get model name by ID
    const getModelName = (modelId: string) => {
        const model = recentModels.find(m => m.id === modelId);
        return model?.name || modelId.slice(0, 12) + "...";
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[var(--primary-500)]"></div>
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
                <p className="text-[var(--foreground-muted)]">
                    Welcome to V-Inference. Manage your models and run verified inference.
                </p>
            </div>

            {/* Error Banner */}
            {error && (
                <div className="p-4 rounded-xl bg-red-500/20 border border-red-500/50 text-red-400">
                    ⚠️ {error}
                </div>
            )}

            {/* Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    icon={<CubeIcon />}
                    label="Total Models"
                    value={stats.total_models}
                    subValue="Uploaded models"
                    color="text-[var(--primary-400)]"
                />
                <StatCard
                    icon={<BoltIcon />}
                    label="Total Inferences"
                    value={stats.total_inferences}
                    subValue="All time"
                    color="text-[var(--accent-400)]"
                />
                <StatCard
                    icon={<ShieldIcon />}
                    label="Verified"
                    value={stats.verified_inferences}
                    subValue={`${stats.verification_rate}% verification rate`}
                    color="text-[var(--secondary-400)]"
                />
                <StatCard
                    icon={<ChartIcon />}
                    label="Marketplace"
                    value={stats.active_listings}
                    subValue="Active listings"
                    color="text-[var(--foreground)]"
                />
            </div>

            {/* Quick Actions */}
            <div>
                <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
                <div className="grid md:grid-cols-3 gap-4">
                    <QuickAction
                        href="/dashboard/models"
                        icon={<CubeIcon />}
                        label="Upload Model"
                        description="Add a new AI model to the network"
                    />
                    <QuickAction
                        href="/dashboard/inference"
                        icon={<BoltIcon />}
                        label="Run Inference"
                        description="Test your models with sample data"
                    />
                    <QuickAction
                        href="/dashboard/marketplace"
                        icon={<ShieldIcon />}
                        label="Marketplace"
                        description="Buy or sell verified inference"
                    />
                </div>
            </div>

            {/* Recent Activity */}
            <div className="grid lg:grid-cols-2 gap-6">
                {/* Recent Models */}
                <div className="glass-card p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold">Recent Models</h2>
                        <Link
                            href="/dashboard/models"
                            className="text-sm text-[var(--primary-400)] hover:underline"
                        >
                            View all
                        </Link>
                    </div>
                    {recentModels.length === 0 ? (
                        <div className="text-center py-8 text-[var(--foreground-muted)]">
                            <CubeIcon />
                            <p className="mt-2">No models yet</p>
                            <Link
                                href="/dashboard/models"
                                className="text-[var(--primary-400)] hover:underline text-sm"
                            >
                                Upload your first model
                            </Link>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {recentModels.map((model) => (
                                <div
                                    key={model.id}
                                    className="flex items-center gap-4 p-4 rounded-xl bg-[var(--glass-bg)]"
                                >
                                    <div className="w-10 h-10 rounded-lg bg-[var(--accent-500)]/20 flex items-center justify-center">
                                        <CubeIcon />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="font-medium truncate">{model.name}</div>
                                        <div className="text-xs text-[var(--foreground-muted)]">
                                            {model.model_type} • {model.total_inferences || 0} inferences
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Recent Jobs - With Verified/Not Verified Status */}
                <div className="glass-card p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold">Recent Jobs</h2>
                        <Link
                            href="/dashboard/inference"
                            className="text-sm text-[var(--primary-400)] hover:underline"
                        >
                            View all
                        </Link>
                    </div>
                    {recentJobs.length === 0 ? (
                        <div className="text-center py-8 text-[var(--foreground-muted)]">
                            <BoltIcon />
                            <p className="mt-2">No inference jobs yet</p>
                            <Link
                                href="/dashboard/inference"
                                className="text-[var(--primary-400)] hover:underline text-sm"
                            >
                                Run your first inference
                            </Link>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {recentJobs.map((job) => (
                                <RecentJobRow
                                    key={job.id}
                                    job={job}
                                    modelName={getModelName(job.model_id)}
                                />
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Network Status */}
            <div className="glass-card p-6">
                <h2 className="text-xl font-semibold mb-4">Network Status</h2>
                <div className="grid sm:grid-cols-3 gap-6">
                    <div className="flex items-center gap-3">
                        <div className="w-3 h-3 rounded-full bg-[var(--secondary-500)] animate-pulse"></div>
                        <div>
                            <div className="font-medium">Sepolia Testnet</div>
                            <div className="text-xs text-[var(--foreground-muted)]">
                                On-Chain Verification Active
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="w-3 h-3 rounded-full bg-[var(--secondary-500)] animate-pulse"></div>
                        <div>
                            <div className="font-medium">ZKML Engine</div>
                            <div className="text-xs text-[var(--foreground-muted)]">
                                Proof Generation Ready
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="w-3 h-3 rounded-full bg-[var(--secondary-500)] animate-pulse"></div>
                        <div>
                            <div className="font-medium">{stats.verification_rate}% Verified</div>
                            <div className="text-xs text-[var(--foreground-muted)]">
                                On-chain proofs anchored
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
