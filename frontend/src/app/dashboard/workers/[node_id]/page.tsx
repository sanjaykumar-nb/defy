"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";

// Icons
const ArrowLeft = () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
    </svg>
);

const ActivityIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
);

const StopIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H10a1 1 0 01-1-1v-4z" />
    </svg>
);

export default function WorkerDetailPage({ params }: { params: Promise<{ node_id: string }> }) {
    const { node_id } = use(params);
    const [worker, setWorker] = useState<any>(null);
    const [liveStats, setLiveStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);

    useEffect(() => {
        fetchWorkerDetails();
        const interval = setInterval(fetchLiveStats, 3000); // Poll every 3s for "real-time"
        return () => clearInterval(interval);
    }, [node_id]);

    const fetchWorkerDetails = async () => {
        try {
            const res = await fetch("http://localhost:8000/api/workers");
            if (res.ok) {
                const workers = await res.json();
                const found = workers.find((w: any) => w.node_id === node_id);
                setWorker(found);
                if (found) fetchLiveStats(found.public_url);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const fetchLiveStats = async (url?: string) => {
        const targetUrl = url || worker?.public_url;
        if (!targetUrl) return;

        try {
            const res = await fetch(`${targetUrl}/job_status`, { mode: 'cors' });
            if (res.ok) {
                const data = await res.json();
                setLiveStats(data);
            }
        } catch (e) {
            // Silently fail polling
        }
    };

    const handleControl = async (action: 'start' | 'stop') => {
        if (!worker?.public_url) return;

        setActionLoading(true);
        try {
            const res = await fetch(`${worker.public_url}/${action}`, {
                method: 'POST',
                mode: 'cors'
            });
            if (res.ok) {
                await fetchLiveStats();
            }
        } catch (e) {
            alert(`Failed to ${action} worker. Ensure tunnel is active.`);
        } finally {
            setActionLoading(false);
        }
    };

    if (loading) return <div className="p-8 text-center">Loading Worker Profile...</div>;
    if (!worker) return <div className="p-8 text-center text-red-400">Worker not found</div>;

    return (
        <div className="space-y-6 max-w-5xl mx-auto">
            <Link href="/dashboard/workers" className="flex items-center gap-2 text-zinc-500 hover:text-white transition-colors">
                <ArrowLeft /> Back to Network
            </Link>

            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        {node_id}
                        <span className={`text-xs px-2 py-1 rounded-full ${liveStats?.is_running ? 'bg-green-500/20 text-green-400 animate-pulse' : 'bg-zinc-800 text-zinc-500'}`}>
                            {liveStats?.is_running ? 'COMPUTING' : 'IDLE'}
                        </span>
                    </h1>
                    <p className="text-zinc-500 text-sm mt-1 font-mono">{worker.wallet_address || '0x...'}</p>
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={() => handleControl('start')}
                        disabled={liveStats?.is_running || actionLoading}
                        className="btn btn-primary flex items-center gap-2 disabled:opacity-50"
                    >
                        <ActivityIcon /> START WORK
                    </button>
                    <button
                        onClick={() => handleControl('stop')}
                        disabled={!liveStats?.is_running || actionLoading}
                        className="btn bg-red-500/10 text-red-500 border border-red-500/30 hover:bg-red-500/20 flex items-center gap-2 disabled:opacity-50"
                    >
                        <StopIcon /> STOP WORK
                    </button>
                </div>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
                {/* Stats Card */}
                <div className="glass-card p-6 md:col-span-2">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-indigo-400">
                        <ActivityIcon /> Real-time Performance
                    </h3>
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                        <div>
                            <p className="text-xs text-zinc-500 uppercase tracking-widest mb-1">Jobs Done</p>
                            <p className="text-3xl font-bold">{liveStats?.jobs_completed || 0}</p>
                        </div>
                        <div>
                            <p className="text-xs text-zinc-500 uppercase tracking-widest mb-1">Status</p>
                            <p className={`text-xl font-bold ${liveStats?.is_running ? 'text-green-400' : 'text-zinc-500'}`}>
                                {liveStats?.is_running ? 'Active' : 'Idle'}
                            </p>
                        </div>
                        <div className="col-span-2">
                            <p className="text-xs text-zinc-500 uppercase tracking-widest mb-1">Current Task</p>
                            <p className="text-sm font-mono truncate text-zinc-300">
                                {liveStats?.current_shard ? `Shard: ${liveStats.current_shard}` : 'Waiting for jobs...'}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Tunnel Card */}
                <div className="glass-card p-6 border-indigo-500/30">
                    <h3 className="text-lg font-bold mb-4 text-indigo-400">Global Link</h3>
                    <div className="p-3 bg-zinc-950 rounded-lg border border-zinc-800 break-all mb-4">
                        <p className="text-[10px] text-zinc-600 uppercase mb-1">Public Endpoint</p>
                        <p className="text-sm font-mono text-indigo-300">{worker.public_url}</p>
                    </div>
                    <p className="text-xs text-zinc-500">
                        This URL is automatically rotated by Serveo. Use it to remotely monitor the node's API.
                    </p>
                </div>
            </div>

            {/* Hardware Info */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-bold mb-4">Hardware Specifications</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                    <div>
                        <p className="text-xs text-zinc-500 mb-1">CUP Cores</p>
                        <p className="text-xl font-bold">{worker.hardware_info?.cpu_cores || 'N/A'}</p>
                    </div>
                    <div>
                        <p className="text-xs text-zinc-500 mb-1">Total RAM</p>
                        <p className="text-xl font-bold">{worker.hardware_info?.total_ram_gb || 'N/A'} GB</p>
                    </div>
                    <div>
                        <p className="text-xs text-zinc-500 mb-1">OS Platform</p>
                        <p className="text-xl font-bold capitalize">{worker.hardware_info?.os || 'N/A'}</p>
                    </div>
                    <div>
                        <p className="text-xs text-zinc-500 mb-1">Privacy Support</p>
                        <p className="text-xl font-bold text-emerald-400">DP ε=1.0</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
