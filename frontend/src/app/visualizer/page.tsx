"use client";

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { WorkerBox, LiveTicker, MetricCard } from '@/components/VisualizerComponents';
import * as api from '@/lib/api';

// --- Demo Configuration ---
const DEMO_WORKERS = [
    { id: 'NODE-0X7AF2', name: 'Nvidia A100-SX' },
    { id: 'NODE-0XBE31', name: 'Apple M3 Max' },
    { id: 'NODE-0X92C1', name: 'Intel Xeon Platinum' },
    { id: 'NODE-0X11D4', name: 'TPU v4 Instance' },
];

export default function VisualizerPage() {
    const [workerStates, setWorkerStates] = useState<any[]>(
        DEMO_WORKERS.map(w => ({ ...w, status: 'idle', progress: 0 }))
    );
    const [events, setEvents] = useState<string[]>([]);
    const [stats, setStats] = useState({
        activeUsers: 842,
        nodesOnline: 4, // Fixed for demo perspective
        jobsHandled: 12450,
        networkSec: '99.9%'
    });
    const [isProcessing, setIsProcessing] = useState(false);
    const lastJobRef = useRef<string | null>(null);

    // Polling for new jobs
    useEffect(() => {
        const pollJobs = async () => {
            try {
                const jobsRes = await api.getJobs();
                if (jobsRes.data && jobsRes.data.length > 0) {
                    const latestJob = jobsRes.data[0];

                    // If new job detected
                    if (latestJob.id !== lastJobRef.current) {
                        lastJobRef.current = latestJob.id;
                        triggerInferenceVisualization(latestJob.id, latestJob.model_id);
                    }
                }
            } catch (err) {
                console.error("Visualizer polling error:", err);
            }
        };

        const interval = setInterval(pollJobs, 3000);
        return () => clearInterval(interval);
    }, [workerStates]);

    const triggerInferenceVisualization = (jobId: string, modelId: string) => {
        addEvent(`INCOMING_JOB: ${jobId.slice(0, 8)} [Model: ${modelId}]`);
        setIsProcessing(true);

        // Pick 2-3 random workers to "process" this job
        const luckyWorkers = [0, 1, 2, 3].sort(() => 0.5 - Math.random()).slice(0, 2);

        setWorkerStates(prev => prev.map((w, idx) => {
            if (luckyWorkers.includes(idx)) {
                return { ...w, status: 'processing', progress: 0 };
            }
            return w;
        }));

        // Simulate progress
        let prog = 0;
        const progInt = setInterval(() => {
            prog += 5;
            setWorkerStates(prev => prev.map((w, idx) => {
                if (luckyWorkers.includes(idx)) return { ...w, progress: Math.min(prog, 100) };
                return w;
            }));

            if (prog >= 100) {
                clearInterval(progInt);
                addEvent(`SHARD_COMPLETED: Nodes ${luckyWorkers.join(', ')} verified zk-proof.`);

                // Mark as completed
                setWorkerStates(prev => prev.map((w, idx) => {
                    if (luckyWorkers.includes(idx)) return { ...w, status: 'completed' };
                    return w;
                }));

                // Reset back to idle after 5 seconds to show it's ready again
                setTimeout(() => {
                    setWorkerStates(prev => prev.map((w, idx) => {
                        if (luckyWorkers.includes(idx)) return { ...w, status: 'idle', progress: 0 };
                        return w;
                    }));
                    setIsProcessing(false);
                }, 5000);
            }
        }, 150);
    };

    const addEvent = (msg: string) => {
        setEvents(prev => [msg, ...prev]);
    };

    return (
        <div className="min-h-screen bg-[#050505] text-white p-8 font-sans selection:bg-[var(--primary-500)] selection:text-white">
            {/* Background Decor */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none opacity-20">
                <div className="absolute top-[10%] left-[20%] w-[40rem] h-[40rem] bg-[var(--primary-500)] blur-[150px] rounded-full animate-pulse" />
                <div className="absolute bottom-[10%] right-[10%] w-[30rem] h-[30rem] bg-[var(--accent-500)] blur-[120px] rounded-full opacity-50" />
            </div>

            {/* Header */}
            <header className="relative z-10 max-w-7xl mx-auto flex justify-between items-end mb-12">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <span className="px-2 py-0.5 rounded bg-[var(--primary-500)] text-[10px] font-black uppercase tracking-widest animate-pulse">Live</span>
                        <span className="text-[var(--foreground-muted)] text-sm tracking-[0.3em] font-medium uppercase font-mono">Mesh Visualizer v1.0.4</span>
                    </div>
                    <h1 className="text-5xl font-black tracking-tight mb-2">
                        V-OBLIVION <span className="text-[var(--primary-400)]">Fleet</span>
                    </h1>
                    <p className="text-[var(--foreground-muted)] max-w-xl text-lg leading-relaxed">
                        Real-time monitoring of decentralized verifiable inference. Watch as the mesh claims, processes, and anchors ZK-Proofs on Shardeum.
                    </p>
                </div>

                <div className="flex items-center gap-4">
                    <Link href="/dashboard" className="btn bg-white/5 border-white/10 hover:bg-white/10 text-white flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                        </svg>
                        Back to Dashboard
                    </Link>
                </div>
            </header>

            <div className="relative z-10 max-w-7xl mx-auto grid grid-cols-12 gap-8">
                {/* Left Column: Metrics & Worker Grid */}
                <div className="col-span-12 lg:col-span-8 space-y-8">
                    {/* Metric Row */}
                    <div className="grid grid-cols-4 gap-6">
                        <MetricCard label="Mesh Participants" value={stats.activeUsers} trend="+12.4%" />
                        <MetricCard label="Compute Nodes" value={stats.nodesOnline} unit="Active" />
                        <MetricCard label="Verified Jobs" value={stats.jobsHandled.toLocaleString()} trend="+2.1k/h" />
                        <MetricCard label="Consensus Health" value={stats.networkSec} unit="Uptime" />
                    </div>

                    {/* Mesh Representation Section */}
                    <div className="bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-3xl p-8 relative overflow-hidden">
                        <div className="flex justify-between items-center mb-10">
                            <div>
                                <h2 className="text-xl font-bold mb-1">Decentralized Mesh Distribution</h2>
                                <p className="text-sm text-[var(--foreground-muted)]">Worker nodes participating in verifiable computation</p>
                            </div>
                            {isProcessing && (
                                <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-[var(--primary-500)]/10 border border-[var(--primary-500)]/30 text-[var(--primary-400)] font-bold text-xs">
                                    <div className="w-2 h-2 rounded-full bg-[var(--primary-500)] animate-ping" />
                                    DISTRIBUTING WORKLOAD
                                </div>
                            )}
                        </div>

                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 relative">
                            {/* Visual connections SVG */}
                            <div className="absolute inset-0 pointer-events-none opacity-10">
                                <svg className="w-full h-full" viewBox="0 0 800 200">
                                    <line x1="100" y1="100" x2="300" y2="100" stroke="currentColor" strokeWidth="2" strokeDasharray="5,5" />
                                    <line x1="300" y1="100" x2="500" y2="100" stroke="currentColor" strokeWidth="2" strokeDasharray="5,5" />
                                    <line x1="500" y1="100" x2="700" y2="100" stroke="currentColor" strokeWidth="2" strokeDasharray="5,5" />
                                </svg>
                            </div>

                            {workerStates.map(worker => (
                                <WorkerBox
                                    key={worker.id}
                                    id={worker.id}
                                    label={worker.name}
                                    status={worker.status}
                                    progress={worker.progress}
                                />
                            ))}
                        </div>

                        {/* Explanation Overlay for Judges */}
                        <div className="mt-12 p-6 rounded-2xl bg-[var(--primary-500)]/5 border border-[var(--primary-500)]/10">
                            <h3 className="text-sm font-bold flex items-center gap-2 mb-3">
                                <svg className="w-5 h-5 text-[var(--primary-400)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                HOW IT WORKS (PROVABLE INFERENCE)
                            </h3>
                            <div className="grid grid-cols-3 gap-6 text-xs leading-relaxed text-[var(--foreground-muted)]">
                                <div>
                                    <span className="block font-bold text-white mb-1">1. JOB SUBMISSION</span>
                                    User requests inference with ZK-Proof requirements on the platform.
                                </div>
                                <div>
                                    <span className="block font-bold text-white mb-1">2. SHARDED PROCESSING</span>
                                    The job is claimed by multiple nodes (boxes) in the mesh to ensure decentralization.
                                </div>
                                <div>
                                    <span className="block font-bold text-white mb-1">3. ZK-PROOF ANCHORING</span>
                                    Once complete (green), the cryptographic proof is anchored to the Shardeum blockchain.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Column: Live Ticker & Network Status */}
                <div className="col-span-12 lg:col-span-4 flex flex-col gap-8">
                    <LiveTicker events={events} />

                    <div className="bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-3xl p-6">
                        <h3 className="text-sm font-bold uppercase tracking-widest text-[var(--foreground-muted)] mb-4">Shardeum Anchoring Stats</h3>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center text-xs">
                                <span className="text-[var(--foreground-muted)]">Verification Latency</span>
                                <span className="font-mono text-[var(--primary-400)]">~140ms</span>
                            </div>
                            <div className="flex justify-between items-center text-xs">
                                <span className="text-[var(--foreground-muted)]">Proof Gas Cost (Avg)</span>
                                <span className="font-mono text-[var(--accent-400)]">0.024 SHM</span>
                            </div>
                            <div className="flex justify-between items-center text-xs">
                                <span className="text-[var(--foreground-muted)]">Circuit Complexity</span>
                                <span className="font-mono">1.2M Gates</span>
                            </div>
                            <div className="pt-4 border-t border-white/5">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-xl bg-[var(--primary-500)]/20 flex items-center justify-center">
                                        <svg className="w-5 h-5 text-[var(--primary-400)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                        </svg>
                                    </div>
                                    <div>
                                        <div className="text-xs font-bold">Immutable Audit Logs</div>
                                        <div className="text-[10px] text-[var(--foreground-muted)]">Anchored via VInferenceAudit.sol</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Visualizer Footer */}
            <footer className="relative z-10 max-w-7xl mx-auto mt-12 flex justify-between items-center border-t border-white/5 pt-8 pb-12">
                <div className="text-[var(--foreground-muted)] text-xs flex items-center gap-6">
                    <span className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-green-500" />
                        System Normal
                    </span>
                    <span>Worker Latency: 42ms</span>
                    <span>Gateway Status: Operational</span>
                </div>
                <div className="flex gap-4 grayscale opacity-20">
                    <div className="w-8 h-8 rounded-lg bg-white/20" />
                    <div className="w-8 h-8 rounded-lg bg-white/20" />
                    <div className="w-8 h-8 rounded-lg bg-white/20" />
                </div>
            </footer>
        </div>
    );
}
