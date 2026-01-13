"use client";

import { useState, useEffect } from "react";
import { IncoService } from "@/lib/incoService";

// Icons
const CPUCoreIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
    </svg>
);

const ActivityIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
);

const WalletIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
    </svg>
);

const GlobalIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
    </svg>
);

const CopyIcon = () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
);

export default function WorkerHub() {
    const [status, setStatus] = useState<"idle" | "connecting" | "active" | "offline">("offline");
    const [publicUrl, setPublicUrl] = useState("");
    const [earnings, setEarnings] = useState(0.0);
    const [nodeId, setNodeId] = useState("");
    const [activeJob, setActiveJob] = useState<any>(null);
    const [systemInfo, setSystemInfo] = useState({
        cpu: "Detecting...",
        ram: "Detecting...",
        gpu: "N/A"
    });

    const [shards, setShards] = useState<any[]>([]);
    const [showGuide, setShowGuide] = useState(false);
    const [copied, setCopied] = useState(false);

    const shareableCommand = `mkdir oblivion-worker && cd oblivion-worker && curl -O https://v-oblivion.net/setup-node.py && python setup-node.py --node-id ${nodeId || 'GLOBAL-NODE-1'}`;

    useEffect(() => {
        // Poll local worker API and Backend for shards
        const interval = setInterval(async () => {
            try {
                // 1. Worker Stats
                const statsRes = await fetch("http://localhost:9000/stats");
                if (statsRes.ok) {
                    const stats = await statsRes.json();
                    setNodeId(stats.node_id || "NODE-DISCOVERING");
                    setEarnings(stats.total_earnings_eth || 0);
                    setStatus(stats.status === "active" ? "active" : "idle");
                    setActiveJob(stats.current_shard);
                    setPublicUrl(stats.public_url || "");
                }

                // 2. Worker Capabilities
                const capRes = await fetch("http://localhost:9000/capabilities");
                if (capRes.ok) {
                    const caps = await capRes.json();
                    setSystemInfo({
                        cpu: `${caps.cpu_cores} Cores`,
                        ram: `${caps.total_ram_gb} GB`,
                        gpu: caps.zk_capable ? "ZK Ready" : "N/A"
                    });
                }

                // 3. Backend Shards (Global View)
                const jobsRes = await fetch("http://localhost:8000/api/training/jobs");
                if (jobsRes.ok) {
                    const jobs = await jobsRes.json();
                    if (jobs.length > 0) {
                        setShards(jobs[0].shards || []);
                    }
                }
            } catch (e) {
                console.log("Polling error (worker or backend may be down)");
            }
        }, 3000);

        return () => clearInterval(interval);
    }, []);

    const joinMesh = async () => {
        setStatus("connecting");
        try {
            const res = await fetch("http://localhost:9000/start", { method: "POST" });
            if (res.ok) {
                setStatus("active");
            } else {
                setStatus("offline");
            }
        } catch (e) {
            console.error("Failed to start worker", e);
            setStatus("offline");
        }
    };

    const stopMesh = async () => {
        try {
            const res = await fetch("http://localhost:9000/stop", { method: "POST" });
            if (res.ok) {
                setStatus("idle");
            }
        } catch (e) {
            console.error("Failed to stop worker", e);
        }
    };

    return (
        <div className="min-h-screen bg-[var(--dark-950)] text-white p-8 font-sans">
            <div className="max-w-6xl mx-auto space-y-8">
                {/* Global Header */}
                <div className="flex justify-between items-center bg-[var(--dark-900)] p-6 rounded-2xl border border-[var(--glass-border)] shadow-2xl">
                    <div>
                        <h1 className="text-4xl font-extrabold bg-gradient-to-r from-[var(--primary-400)] to-[var(--secondary-400)] bg-clip-text text-transparent">
                            V-OBLIVION WORKER PORTAL
                        </h1>
                        <p className="text-[var(--foreground-muted)] text-lg mt-1">
                            Contribute compute power to the global AI mesh
                        </p>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className={`px-4 py-2 rounded-full font-bold flex items-center gap-2 ${status === 'active' ? 'bg-green-500/20 text-green-400 border border-green-500/50' :
                            status === 'offline' ? 'bg-red-500/20 text-red-400 border border-red-500/50' :
                                'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50'
                            }`}>
                            <div className={`w-3 h-3 rounded-full ${status === 'active' ? 'bg-green-500 animate-pulse' : 'bg-current'}`}></div>
                            {status.toUpperCase()}
                        </div>
                    </div>
                </div>

                {/* Dashboard Grid */}
                <div className="grid md:grid-cols-3 gap-6">
                    {/* Stats Card */}
                    <div className="glass-card p-6 space-y-4">
                        <div className="flex items-center gap-3 text-[var(--primary-400)]">
                            <WalletIcon />
                            <h2 className="text-xl font-bold">Earnings</h2>
                        </div>
                        <div className="text-5xl font-black">{earnings.toFixed(4)} SHM</div>
                        <p className="text-sm text-[var(--foreground-muted)]">Unsettled rewards from 0 jobs</p>
                        <button className="w-full py-3 bg-[var(--primary-600)] hover:bg-[var(--primary-500)] rounded-xl font-bold transition-all shadow-lg hover:shadow-[var(--primary-500)]/30">
                            Withdraw to Metamask
                        </button>
                    </div>

                    {/* Node Info Card */}
                    <div className="glass-card p-6 space-y-4">
                        <div className="flex items-center gap-3 text-[var(--secondary-400)]">
                            <CPUCoreIcon />
                            <h2 className="text-xl font-bold">Node Identity</h2>
                        </div>
                        <div className="font-mono text-2xl truncate text-[var(--secondary-300)]">{nodeId || "---"}</div>
                        <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                                <span className="text-[var(--foreground-muted)]">CPU</span>
                                <span>{systemInfo.cpu}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-[var(--foreground-muted)]">RAM</span>
                                <span>{systemInfo.ram}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-[var(--foreground-muted)]">GPU</span>
                                <span>{systemInfo.gpu}</span>
                            </div>
                        </div>
                    </div>

                    {/* Quick Start Card */}
                    <div className="glass-card p-6 space-y-4 bg-gradient-to-br from-[var(--primary-900)]/20 to-[var(--dark-900)]">
                        <div className="flex items-center gap-3 text-[var(--accent-400)]">
                            <ActivityIcon />
                            <h2 className="text-xl font-bold">Quick Control</h2>
                        </div>
                        <p className="text-sm text-[var(--foreground-muted)]">
                            Click below to initialize your local compute sandbox and connect to the network.
                        </p>
                        <div className="flex gap-2">
                            {status === 'active' ? (
                                <button
                                    onClick={stopMesh}
                                    className="w-full py-4 bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/50 rounded-xl font-bold transition-all"
                                >
                                    DEACTIVATE
                                </button>
                            ) : (
                                <button
                                    onClick={joinMesh}
                                    disabled={status === 'connecting'}
                                    className="w-full py-4 bg-white text-black hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl font-black text-lg transition-all transform active:scale-95"
                                >
                                    {status === 'offline' ? 'JOIN THE MESH' : 'STARTING...'}
                                </button>
                            )}
                        </div>
                    </div>
                </div>

                {/* Shard View */}
                <div className="glass-card p-8">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-2xl font-bold flex items-center gap-3">
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping"></div>
                            Distributed Contribution Mesh
                        </h2>
                        <div className="flex gap-4 items-center">
                            <span className="text-sm px-3 py-1 bg-[var(--dark-800)] rounded-lg text-[var(--foreground-muted)] border border-[var(--glass-border)]">
                                Mesh Nodes: 10 Active
                            </span>
                        </div>
                    </div>

                    {status !== 'active' ? (
                        <div className="h-64 flex flex-col items-center justify-center text-[var(--foreground-muted)] border-2 border-dashed border-[var(--glass-border)] rounded-2xl bg-[var(--dark-900)]/50">
                            <ActivityIcon />
                            <p className="mt-4 font-medium uppercase tracking-widest text-xs opacity-50">Node must be ACTIVE to receive task shards</p>
                            <button onClick={joinMesh} className="mt-4 px-6 py-2 bg-white text-black rounded-lg font-bold text-sm hover:scale-105 transition-transform">
                                ACTIVATE NODE
                            </button>
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                            {(shards.length > 0 ? shards : [...Array(10)]).map((shard, i) => {
                                const isMyShard = shard && nodeId && shard.worker_id === nodeId;
                                const isCompleted = shard?.status === 'completed';
                                const isProcessing = shard?.status === 'processing';

                                return (
                                    <div key={i} className={`p-4 rounded-xl border transition-all duration-500 ${isMyShard ? 'bg-[var(--primary-900)]/20 border-[var(--primary-500)]/50 shadow-[0_0_20px_rgba(var(--primary-rgb),0.2)]' :
                                        isCompleted ? 'bg-green-500/10 border-green-500/30' :
                                            'bg-[var(--dark-900)] border-[var(--glass-border)] opacity-60'
                                        }`}>
                                        <div className="flex justify-between items-start mb-2">
                                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs ${isMyShard ? 'bg-[var(--primary-500)] text-white' : 'bg-gray-800 text-gray-400'}`}>
                                                N{i + 1}
                                            </div>
                                            {isMyShard && <div className="text-[10px] text-[var(--primary-400)] font-bold animate-pulse">YOU</div>}
                                        </div>
                                        <div className="text-[10px] uppercase font-bold text-[var(--foreground-muted)] mb-1">
                                            {shard?.shard_id ? `Shard ${i + 1}` : "WAITING..."}
                                        </div>
                                        <div className="h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full transition-all duration-1000 ${isMyShard ? 'bg-[var(--primary-500)]' : isCompleted ? 'bg-green-500' : 'bg-gray-600'}`}
                                                style={{ width: shard?.progress ? `${shard.progress}%` : (isCompleted ? '100%' : '5%') }}
                                            ></div>
                                        </div>
                                        <div className="mt-2 text-[10px] font-mono flex justify-between">
                                            <span>{shard?.progress ? `${shard.progress}%` : (isCompleted ? '100%' : '0%')}</span>
                                            <span className={isMyShard ? 'text-[var(--primary-400)]' : isCompleted ? 'text-green-500' : 'text-gray-500'}>
                                                {isCompleted ? 'VERIFIED' : isProcessing ? 'ACTIVE' : 'IDLE'}
                                            </span>
                                        </div>

                                        {/* Animation for processing */}
                                        {isProcessing && (
                                            <div className="absolute inset-0 pointer-events-none">
                                                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[var(--primary-400)] to-transparent animate-scan"></div>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    {/* Mesh Connectivity Visualizer */}
                    <div className="mt-8 relative h-32 bg-[var(--dark-900)]/30 rounded-2xl overflow-hidden border border-[var(--glass-border)]">
                        <div className="absolute inset-0 flex items-center justify-around opacity-20">
                            {[...Array(8)].map((_, i) => (
                                <div key={i} className="h-full w-px bg-gradient-to-b from-transparent via-[var(--primary-500)] to-transparent animate-pulse" style={{ animationDelay: `${i * 0.5}s` }}></div>
                            ))}
                        </div>
                        <div className="relative z-10 h-full flex items-center justify-center gap-8">
                            <div className="flex flex-col items-center">
                                <div className="w-12 h-12 rounded-full bg-[var(--primary-500)]/20 border-2 border-[var(--primary-500)] flex items-center justify-center animate-bounce">
                                    <CPUCoreIcon />
                                </div>
                                <span className="text-[10px] mt-1 font-bold">NODE-MASTER</span>
                            </div>
                            <div className="h-px w-24 bg-gradient-to-r from-[var(--primary-500)] to-transparent relative">
                                <div className="absolute top-1/2 left-0 w-2 h-2 bg-white rounded-full -translate-y-1/2 animate-flow"></div>
                            </div>
                            <div className="flex flex-col items-center opacity-50">
                                <div className="w-10 h-10 rounded-full bg-[var(--dark-800)] border border-[var(--glass-border)] flex items-center justify-center">
                                    <GlobalIcon />
                                </div>
                                <span className="text-[10px] mt-1">PEER-MESH</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Participation CTA */}
                <div className="glass-card p-8 border-2 border-[var(--primary-500)]/30 bg-gradient-to-r from-[var(--primary-900)]/10 to-transparent">
                    <div className="flex flex-col md:flex-row justify-between items-center gap-6">
                        <div className="space-y-2">
                            <h2 className="text-3xl font-black">EXPAND THE MESH</h2>
                            <p className="text-[var(--foreground-muted)]">
                                Share your node's external link so others can assist in verification & monitoring.
                            </p>
                            {publicUrl && (
                                <div className="text-xs font-mono text-[var(--primary-400)] truncate max-w-md">
                                    Live Link: {publicUrl}
                                </div>
                            )}
                        </div>
                        <div className="flex gap-4">
                            <button
                                onClick={() => {
                                    if (publicUrl) {
                                        navigator.clipboard.writeText(publicUrl);
                                        setCopied(true);
                                        setTimeout(() => setCopied(false), 2000);
                                    } else {
                                        setShowGuide(true);
                                    }
                                }}
                                className="px-8 py-4 bg-white text-black font-black rounded-2xl hover:scale-105 transition-transform flex items-center gap-3"
                            >
                                <GlobalIcon /> {copied ? 'COPIED LINK!' : 'COPY HUB LINK'}
                            </button>
                            <button
                                onClick={() => setShowGuide(true)}
                                className="px-8 py-4 bg-[var(--dark-800)] border border-[var(--glass-border)] text-white font-black rounded-2xl hover:scale-105 transition-transform"
                            >
                                HOW TO START
                            </button>
                        </div>
                    </div>
                </div>

                {/* Activity Feed */}
                <div className="glass-card p-6 overflow-hidden">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <svg className="w-5 h-5 text-[var(--primary-400)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                        Contribution Log
                    </h3>
                    <div className="space-y-3 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                        {(shards.filter(s => s.status === 'completed').length > 0 ? [
                            { time: new Date().toLocaleTimeString(), msg: `Node ${nodeId || 'Worker'} claimed shard successfully`, type: "success" },
                            ...shards.filter(s => s.status === 'completed').map(s => ({
                                time: new Date().toLocaleTimeString(),
                                msg: `Shard ${s.shard_id.split('-').pop()} verification proof submitted to Shardeum`,
                                type: "agg"
                            }))
                        ] : [
                            { time: "14:20:05", msg: "Shard #42 claimed by mesh consensus", type: "info" },
                            { time: "14:20:12", msg: "Data partition distributed to 10 nodes", type: "process" },
                            { time: "14:21:44", msg: "Node #2 (Local) completed shard training", type: "success" },
                            { time: "14:22:10", msg: "Verifying ZK-Proofs for computation shards...", type: "process" },
                            { time: "14:22:30", msg: "Aggregating gradients via Federated Averaging", type: "agg" },
                        ]).map((log, i) => (
                            <div key={i} className="flex gap-4 text-xs font-mono border-l-2 border-[var(--dark-800)] pl-4 py-1">
                                <span className="text-[var(--foreground-muted)] whitespace-nowrap">{log.time}</span>
                                <span className={
                                    log.type === 'success' ? 'text-green-400' :
                                        log.type === 'process' ? 'text-blue-400' :
                                            log.type === 'agg' ? 'text-purple-400' :
                                                'text-gray-300'
                                }>{log.msg}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Participation Guide Modal */}
            {showGuide && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
                    <div className="glass-card max-w-2xl w-full p-8 space-y-6 relative border-t-4 border-[var(--primary-500)]">
                        <button
                            onClick={() => setShowGuide(false)}
                            className="absolute top-4 right-4 text-[var(--foreground-muted)] hover:text-white"
                        >
                            ✕
                        </button>
                        <div className="space-y-2">
                            <h2 className="text-3xl font-black">BECOME A NODE</h2>
                            <p className="text-[var(--foreground-muted)]">
                                Follow these steps to join the mesh and start earning SHM from any system.
                            </p>
                        </div>

                        <div className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-xs font-bold uppercase tracking-widest text-[var(--primary-400)]">Quick Connect Command</label>
                                <div className="p-4 bg-black rounded-xl border border-[var(--glass-border)] font-mono text-xs flex justify-between items-center group">
                                    <span className="text-green-400 truncate mr-4">{shareableCommand}</span>
                                    <button
                                        onClick={() => {
                                            navigator.clipboard.writeText(shareableCommand);
                                            setCopied(true);
                                            setTimeout(() => setCopied(false), 2000);
                                        }}
                                        className="p-2 hover:bg-white/10 rounded-lg transition-colors flex items-center gap-2"
                                    >
                                        <CopyIcon />
                                        <span className="text-[10px] font-bold">{copied ? 'COPIED!' : 'COPY'}</span>
                                    </button>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 rounded-xl bg-[var(--dark-900)] border border-[var(--glass-border)]">
                                    <h4 className="font-bold mb-1">1. Install Python</h4>
                                    <p className="text-xs text-[var(--foreground-muted)]">Ensure Python 3.9+ is installed on your system.</p>
                                </div>
                                <div className="p-4 rounded-xl bg-[var(--dark-900)] border border-[var(--glass-border)]">
                                    <h4 className="font-bold mb-1">2. Run Setup</h4>
                                    <p className="text-xs text-[var(--foreground-muted)]">Paste the command above into your terminal.</p>
                                </div>
                            </div>
                        </div>

                        <button
                            onClick={() => setShowGuide(false)}
                            className="w-full py-4 bg-[var(--primary-600)] rounded-xl font-black hover:bg-[var(--primary-500)] transition-colors"
                        >
                            I'M READY TO CONTRIBUTE
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
