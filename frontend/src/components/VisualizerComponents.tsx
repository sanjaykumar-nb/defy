"use client";

import React, { useState, useEffect } from 'react';

// --- Types ---
export interface NodeData {
    id: string;
    name: string;
    status: 'idle' | 'processing' | 'completed' | 'failed';
    type: 'worker' | 'relay' | 'validator';
    load: number;
    lastActive: string;
}

export interface MeshStats {
    activeNodes: number;
    totalJobs: number;
    activeJobs: number;
    meshHealth: number;
    throughput: number;
}

// --- Components ---

/**
 * WorkerBox: Represents a single worker in the grid
 * Turns green on completion, pulses on processing
 */
export const WorkerBox = ({
    id,
    status,
    label,
    progress = 0
}: {
    id: string;
    status: string;
    label: string;
    progress?: number;
}) => {
    const getStatusColor = () => {
        switch (status) {
            case 'processing': return 'border-[var(--primary-400)] bg-[var(--primary-900)]/20 shadow-[0_0_20px_rgba(var(--primary-rgb),0.3)]';
            case 'completed': return 'border-green-500/50 bg-green-500/10 shadow-[0_0_20px_rgba(34,197,94,0.3)]';
            case 'failed': return 'border-red-500/50 bg-red-500/10';
            default: return 'border-[var(--glass-border)] bg-[var(--glass-bg)]';
        }
    };

    const getStatusIcon = () => {
        switch (status) {
            case 'processing': return (
                <div className="flex gap-1 items-center">
                    <span className="w-1.5 h-1.5 rounded-full bg-[var(--primary-400)] animate-pulse" />
                    <span className="text-[10px] uppercase tracking-tighter text-[var(--primary-400)]">Active</span>
                </div>
            );
            case 'completed': return (
                <div className="flex gap-1 items-center">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                    <span className="text-[10px] uppercase tracking-tighter text-green-500">Done</span>
                </div>
            );
            default: return (
                <div className="flex gap-1 items-center">
                    <span className="w-1.5 h-1.5 rounded-full bg-[var(--foreground-muted)] opacity-50" />
                    <span className="text-[10px] uppercase tracking-tighter text-[var(--foreground-muted)]">Standby</span>
                </div>
            );
        }
    };

    return (
        <div className={`relative p-5 rounded-2xl border transition-all duration-700 ${getStatusColor()}`}>
            <div className="flex justify-between items-start mb-4">
                <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                    <svg className="w-5 h-5 text-[var(--foreground-muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                    </svg>
                </div>
                {getStatusIcon()}
            </div>

            <div>
                <div className="text-sm font-semibold mb-1 truncate">{label}</div>
                <div className="text-[10px] text-[var(--foreground-muted)] font-mono">{id}</div>
            </div>

            {status === 'processing' && (
                <div className="mt-4 h-1 w-full bg-white/5 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-[var(--primary-500)] transition-all duration-300"
                        style={{ width: `${progress}%` }}
                    />
                </div>
            )}

            {status === 'completed' && (
                <div className="absolute top-2 right-2">
                    <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                </div>
            )}
        </div>
    );
};

/**
 * LiveTicker: Shows recent job events
 */
export const LiveTicker = ({ events }: { events: string[] }) => {
    return (
        <div className="bg-[var(--glass-bg)] border border-[var(--glass-border)] rounded-2xl p-6 h-full flex flex-col">
            <h3 className="text-sm font-bold uppercase tracking-widest text-[var(--foreground-muted)] mb-4 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                Mesh Event Log
            </h3>
            <div className="flex-1 space-y-3 font-mono text-xs overflow-hidden">
                {events.slice(0, 10).map((event, i) => (
                    <div key={i} className="flex gap-3 text-[var(--foreground-muted)] animate-in fade-in slide-in-from-left duration-500">
                        <span className="text-[var(--primary-400)]">[{new Date().toLocaleTimeString([], { hour12: false })}]</span>
                        <span className="text-white">MESH_MSG</span>
                        <span className="truncate">{event}</span>
                    </div>
                ))}
                {events.length === 0 && (
                    <div className="text-[var(--foreground-muted)] italic opacity-50">Monitoring network traffic...</div>
                )}
            </div>
        </div>
    );
};

/**
 * MetricCard: Displays key stats with glitzy animation
 */
export const MetricCard = ({ label, value, unit, trend }: { label: string; value: string | number; unit?: string; trend?: string }) => {
    return (
        <div className="bg-[var(--glass-bg)] border border-[var(--glass-border)] p-5 rounded-2xl relative overflow-hidden group">
            <div className="absolute -right-4 -top-4 w-24 h-24 bg-[var(--primary-500)]/5 blur-3xl rounded-full group-hover:bg-[var(--primary-500)]/10 transition-all" />
            <div className="text-[10px] uppercase tracking-[0.2em] text-[var(--foreground-muted)] mb-1 font-bold">{label}</div>
            <div className="flex items-baseline gap-2">
                <div className="text-3xl font-black bg-gradient-to-r from-white to-[var(--foreground-muted)] bg-clip-text text-transparent">{value}</div>
                {unit && <div className="text-xs text-[var(--foreground-muted)] font-medium uppercase tracking-tighter">{unit}</div>}
            </div>
            {trend && (
                <div className="mt-2 text-[10px] font-bold text-green-400 flex items-center gap-1">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    {trend}
                </div>
            )}
        </div>
    );
};
