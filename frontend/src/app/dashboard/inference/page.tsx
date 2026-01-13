"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import * as api from "@/lib/api";

// Icons
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

const CubeIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
    </svg>
);

const ClockIcon = () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

const PlayIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

const CheckCircleIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

const CopyIcon = () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
);

const ExternalLinkIcon = () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
    </svg>
);

interface InferenceResult {
    job_id: string;
    model_id: string;
    output: Record<string, unknown>;
    inference_time_ms: number;
    total_time_ms: number;
    zkml?: {
        enabled: boolean;
        proof: {
            proof_hash: string;
            circuit_hash: string;
            on_chain?: {
                anchored: boolean;
                transaction_hash?: string;
                block_number?: number;
                explorer_url?: string;
                gas_cost_SHM?: number;
                gas_cost_usd?: number;
            };
        };
        verification: {
            is_valid: boolean;
            message: string;
            gas_estimate: {
                cost_usd: number;
                chain: string;
            };
        };
    };
}

const SAMPLE_INPUTS: Record<string, { description: string; input: Record<string, unknown> }> = {
    classification: {
        description: "Classification model input (MNIST - 784 features)",
        input: {
            features: [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.9, 0.9, 0.9, 0.9, 0.9, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.9, 0.9, 0.99, 0.9, 0.9, 0.9, 0.9, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.5, 0.5, 0.5, 0.5, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.9, 0.9, 0.5, 0.0, 0.0, 0.5, 0.9, 0.9, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.9, 0.5, 0.5, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            ],
        },
    },
    regression: {
        description: "Regression model input (13 features for Home Price)",
        input: {
            features: [0.5, 0.3, 0.8, 0.2, 0.9, 0.1, 0.4, 0.6, 0.7, 0.5, 0.3, 0.2, 0.8],
        },
    },
    nlp: {
        description: "NLP/Text model input",
        input: {
            text: "This is a sample text for sentiment analysis.",
            max_length: 512,
            return_embeddings: false,
        },
    },
    embedding: {
        description: "Embedding model input",
        input: {
            text: "Generate embedding for this text",
            pooling: "mean",
        },
    },
    iris: {
        description: "Iris Classifier (4 features)",
        input: {
            features: [5.1, 3.5, 1.4, 0.2],
        },
    },
};

// Model-specific sample inputs by model ID or name pattern
const MODEL_SAMPLES: Record<string, { features: number[] }> = {
    // Iris models (4 features)
    "iris-compatible-001": { features: [5.1, 3.5, 1.4, 0.2] },

    // Fraud Detection (30 features)
    "model-fraud-detection-v2": { features: [0.5, 0.8, 0.3, 0.7, 0.2, 0.9, 0.4, 0.6, 0.1, 0.8, 0.5, 0.3, 0.7, 0.2, 0.9, 0.4, 0.6, 0.1, 0.8, 0.5, 0.3, 0.7, 0.5, 0.2, 0.9, 0.4, 0.6, 0.1, 0.8, 0.3] },
    // Customer Churn (20 features)
    "model-churn-predictor-v2": { features: [0.5, 0.8, 0.3, 0.7, 0.2, 0.9, 0.4, 0.6, 0.1, 0.8, 0.5, 0.3, 0.7, 0.2, 0.9, 0.4, 0.6, 0.1, 0.8, 0.5] },
    // Credit Card Fraud (28 features)
    "model-creditcard-v2": { features: [0.5, 0.8, 0.3, 0.7, 0.2, 0.9, 0.4, 0.6, 0.1, 0.8, 0.5, 0.3, 0.7, 0.2, 0.9, 0.4, 0.6, 0.1, 0.8, 0.5, 0.3, 0.7, 0.5, 0.2, 0.9, 0.4, 0.6, 0.1] },
    // Home Price (13 features)
    "model-home-price-v2": { features: [0.5, 0.3, 0.8, 0.2, 0.9, 0.1, 0.4, 0.6, 0.7, 0.5, 0.3, 0.2, 0.8] },
    // Sentiment (100 features)
    "model-sentiment-v2": { features: Array(100).fill(0).map(() => Math.random().toFixed(2)).map(Number) },
};

// Helper to get sample for a model
function getSampleForModel(modelId: string, modelName: string, modelType: string): Record<string, unknown> {
    // Check by ID first
    if (MODEL_SAMPLES[modelId]) {
        return { features: MODEL_SAMPLES[modelId].features };
    }
    // Check by name pattern - ORDER MATTERS! More specific patterns first
    const lowerName = modelName.toLowerCase();
    if (lowerName.includes('iris')) {
        return { features: [5.1, 3.5, 1.4, 0.2] };
    }
    // Credit Card Fraud = 28 features (check BEFORE generic fraud)
    if (lowerName.includes('credit') || lowerName.includes('creditcard')) {
        return { features: Array(28).fill(0).map((_, i) => Number((0.1 + (i * 0.03)).toFixed(2))) };
    }
    // Generic Fraud Detection = 30 features
    if (lowerName.includes('fraud')) {
        return { features: Array(30).fill(0).map((_, i) => Number((0.1 + (i * 0.03)).toFixed(2))) };
    }
    if (lowerName.includes('churn')) {
        return { features: Array(20).fill(0).map((_, i) => Number((0.1 + (i * 0.04)).toFixed(2))) };
    }
    if (lowerName.includes('home') || lowerName.includes('price')) {
        return { features: Array(13).fill(0).map((_, i) => Number((0.1 + (i * 0.07)).toFixed(2))) };
    }
    // Resume Classifier = 50 features
    if (lowerName.includes('resume')) {
        return { features: Array(50).fill(0).map((_, i) => Number((0.1 + (i * 0.02)).toFixed(2))) };
    }
    if (lowerName.includes('sentiment')) {
        return { features: Array(100).fill(0).map((_, i) => Number((0.01 * i).toFixed(2))) };
    }
    // Fallback to model type
    return SAMPLE_INPUTS[modelType]?.input || { features: [0.5, 0.3, 0.8, 0.2, 0.9] };
}

function InferenceContent() {
    const searchParams = useSearchParams();
    const preselectedModel = searchParams.get("model");

    const [models, setModels] = useState<api.AIModel[]>([]);
    const [selectedModel, setSelectedModel] = useState<string>("");
    const [inputData, setInputData] = useState<string>("");
    const [useZkml, setUseZkml] = useState(true);
    const [loading, setLoading] = useState(false);
    const [loadingModels, setLoadingModels] = useState(true);
    const [result, setResult] = useState<InferenceResult | null>(null);
    const [jobs, setJobs] = useState<api.InferenceJob[]>([]);
    const [selectedJob, setSelectedJob] = useState<api.InferenceJob | null>(null);
    const [copied, setCopied] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [simulateFailure, setSimulateFailure] = useState(false); // Demo mode: simulate failed verification

    // Fetch models from backend
    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoadingModels(true);

                // Get models from backend
                const modelsRes = await api.getModels();
                if (modelsRes.success && modelsRes.data) {
                    setModels(modelsRes.data);

                    if (preselectedModel) {
                        setSelectedModel(preselectedModel);
                        const model = modelsRes.data.find((m) => m.id === preselectedModel);
                        if (model && SAMPLE_INPUTS[model.model_type]) {
                            setInputData(JSON.stringify(SAMPLE_INPUTS[model.model_type].input, null, 2));
                        }
                    }
                }

                // Get recent jobs from backend
                const jobsRes = await api.getJobs();
                if (jobsRes.success && jobsRes.data) {
                    setJobs(jobsRes.data);
                }
            } catch (err) {
                console.error("Error fetching data:", err);
                setError("Failed to connect to backend. Make sure it's running on http://localhost:8000");
            } finally {
                setLoadingModels(false);
            }
        };

        fetchData();
    }, [preselectedModel]);

    const handleModelChange = (modelId: string) => {
        setSelectedModel(modelId);
        const model = models.find((m) => m.id === modelId);
        if (model) {
            const sample = getSampleForModel(model.id, model.name, model.model_type);
            setInputData(JSON.stringify(sample, null, 2));
        }
        setResult(null);
        setError(null);
    };

    const handleLoadSample = () => {
        const model = models.find((m) => m.id === selectedModel);
        if (model) {
            const sample = getSampleForModel(model.id, model.name, model.model_type);
            setInputData(JSON.stringify(sample, null, 2));
        }
    };

    const handleRunInference = async () => {
        if (!selectedModel || !inputData) return;

        setLoading(true);
        setResult(null);
        setError(null);

        try {
            // Parse input data
            const parsedInput = JSON.parse(inputData);

            // Call real backend API
            const response = await api.runInference(selectedModel, parsedInput, useZkml, simulateFailure);

            if (response.success && response.data) {
                setResult(response.data as InferenceResult);

                // Refresh jobs list
                const jobsRes = await api.getJobs();
                if (jobsRes.success && jobsRes.data) {
                    setJobs(jobsRes.data);
                }
            } else {
                setError(response.message || "Inference failed");
            }
        } catch (err) {
            console.error("Inference error:", err);
            setError(err instanceof Error ? err.message : "Failed to run inference");
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (loadingModels) {
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
                <h1 className="text-3xl font-bold mb-2">Run Inference</h1>
                <p className="text-[var(--foreground-muted)]">
                    Test your models with sample data and generate ZK proofs (anchored on Shardeum!)
                </p>
            </div>

            {/* Error Banner */}
            {error && (
                <div className="p-4 rounded-xl bg-red-500/20 border border-red-500/50 text-red-400">
                    ⚠️ {error}
                </div>
            )}

            <div className="grid lg:grid-cols-2 gap-6">
                {/* Input Panel */}
                <div className="glass-card p-6 space-y-6">
                    <h2 className="text-xl font-semibold flex items-center gap-2">
                        <BoltIcon /> Inference Request
                    </h2>

                    {/* Model Selection */}
                    <div>
                        <label className="block text-sm font-medium mb-2">Select Model</label>
                        {models.length === 0 ? (
                            <div className="p-4 rounded-xl bg-[var(--glass-bg)] text-center">
                                <CubeIcon />
                                <p className="text-sm text-[var(--foreground-muted)] mt-2">
                                    No models found.{" "}
                                    <a href="/dashboard/models" className="text-[var(--primary-400)] hover:underline">
                                        Upload a model
                                    </a>
                                </p>
                            </div>
                        ) : (
                            <select
                                value={selectedModel}
                                onChange={(e) => handleModelChange(e.target.value)}
                                className="input"
                            >
                                <option value="">Choose a model...</option>
                                {models.map((model) => (
                                    <option key={model.id} value={model.id}>
                                        {model.name} ({model.model_type})
                                    </option>
                                ))}
                            </select>
                        )}
                    </div>

                    {/* Input Data */}
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <label className="block text-sm font-medium">Input Data (JSON)</label>
                            {selectedModel && (
                                <button
                                    onClick={handleLoadSample}
                                    className="text-xs text-[var(--primary-400)] hover:underline"
                                >
                                    Load sample
                                </button>
                            )}
                        </div>
                        <textarea
                            value={inputData}
                            onChange={(e) => setInputData(e.target.value)}
                            placeholder='{"key": "value"}'
                            className="input font-mono text-sm min-h-[200px] resize-none"
                        />
                    </div>

                    {/* ZKML Toggle */}
                    <div className="flex items-center justify-between p-4 rounded-xl bg-[var(--glass-bg)]">
                        <div className="flex items-center gap-3">
                            <ShieldIcon />
                            <div>
                                <div className="font-medium">Enable ZKML Verification</div>
                                <div className="text-sm text-[var(--foreground-muted)]">
                                    Generate ZK proof & anchor on Shardeum
                                </div>
                            </div>
                        </div>
                        <button
                            onClick={() => setUseZkml(!useZkml)}
                            className={`w-12 h-6 rounded-full transition-colors ${useZkml ? "bg-[var(--secondary-500)]" : "bg-[var(--dark-600)]"
                                }`}
                        >
                            <div
                                className={`w-5 h-5 rounded-full bg-white transition-transform ${useZkml ? "translate-x-6" : "translate-x-0.5"
                                    }`}
                            />
                        </button>
                    </div>

                    {/* Simulate Failure Toggle - Demo Mode */}
                    <div className="flex items-center justify-between p-4 rounded-xl bg-red-500/10 border border-red-500/30">
                        <div className="flex items-center gap-3">
                            <span className="text-xl">⚠️</span>
                            <div>
                                <div className="font-medium text-red-400">Simulate Failure (Demo)</div>
                                <div className="text-sm text-[var(--foreground-muted)]">
                                    Demo: Show failed verification scenario
                                </div>
                            </div>
                        </div>
                        <button
                            onClick={() => setSimulateFailure(!simulateFailure)}
                            className={`w-12 h-6 rounded-full transition-colors ${simulateFailure ? "bg-red-500" : "bg-[var(--dark-600)]"
                                }`}
                        >
                            <div
                                className={`w-5 h-5 rounded-full bg-white transition-transform ${simulateFailure ? "translate-x-6" : "translate-x-0.5"
                                    }`}
                            />
                        </button>
                    </div>

                    {/* Run Button */}
                    <button
                        onClick={handleRunInference}
                        disabled={!selectedModel || !inputData || loading}
                        className="btn btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <>
                                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                                Processing on Shardeum...
                            </>
                        ) : (
                            <>
                                <PlayIcon />
                                Run Inference
                            </>
                        )}
                    </button>
                </div>

                {/* Output Panel */}
                <div className="glass-card p-6 space-y-6">
                    <h2 className="text-xl font-semibold flex items-center gap-2">
                        <CheckCircleIcon /> Results
                    </h2>

                    {!result ? (
                        <div className="flex flex-col items-center justify-center py-16 text-[var(--foreground-muted)]">
                            <BoltIcon />
                            <p className="mt-2">Run inference to see results</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {/* Timing Stats */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 rounded-xl bg-[var(--glass-bg)] text-center">
                                    <div className="text-2xl font-bold text-[var(--primary-400)]">
                                        {result.inference_time_ms}ms
                                    </div>
                                    <div className="text-xs text-[var(--foreground-muted)]">Inference Time</div>
                                </div>
                                <div className="p-4 rounded-xl bg-[var(--glass-bg)] text-center">
                                    <div className="text-2xl font-bold text-[var(--accent-400)]">
                                        {result.total_time_ms}ms
                                    </div>
                                    <div className="text-xs text-[var(--foreground-muted)]">Total Time</div>
                                </div>
                            </div>

                            {/* Output */}
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm font-medium">Output</span>
                                    <button
                                        onClick={() => copyToClipboard(JSON.stringify(result.output, null, 2))}
                                        className="text-xs text-[var(--primary-400)] hover:underline flex items-center gap-1"
                                    >
                                        <CopyIcon />
                                        {copied ? "Copied!" : "Copy"}
                                    </button>
                                </div>
                                <pre className="p-4 rounded-xl bg-[var(--dark-900)] text-sm font-mono overflow-auto max-h-[200px]">
                                    {JSON.stringify(result.output, null, 2)}
                                </pre>
                            </div>

                            {/* ZK Proof with Real Shardeum TX */}
                            {result.zkml && (
                                <div className="p-4 rounded-xl bg-[var(--secondary-500)]/10 border border-[var(--secondary-500)]/30">
                                    <div className="flex items-center gap-2 mb-3">
                                        <ShieldIcon />
                                        <span className="font-semibold text-[var(--secondary-400)]">
                                            ZK Proof {result.zkml.verification?.is_valid ? "Verified" : "Generated"}
                                        </span>
                                    </div>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex items-center justify-between">
                                            <span className="text-[var(--foreground-muted)]">Status</span>
                                            <span className="badge badge-success">
                                                {result.zkml.verification?.is_valid ? "Valid" : "Pending"}
                                            </span>
                                        </div>
                                        <div className="flex items-start justify-between">
                                            <span className="text-[var(--foreground-muted)]">Proof Hash</span>
                                            <span className="font-mono text-xs max-w-[200px] truncate">
                                                {result.zkml.proof?.proof_hash}
                                            </span>
                                        </div>

                                        {/* Real Shardeum Transaction */}
                                        {result.zkml.proof?.on_chain?.anchored && (
                                            <>
                                                <div className="border-t border-[var(--glass-border)] pt-2 mt-2">
                                                    <div className="text-xs font-semibold text-[var(--secondary-400)] mb-2">
                                                        ⛓️ REAL Shardeum TRANSACTION
                                                    </div>
                                                </div>
                                                <div className="flex items-center justify-between">
                                                    <span className="text-[var(--foreground-muted)]">TX Hash</span>
                                                    <a
                                                        href={result.zkml.proof.on_chain.explorer_url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="font-mono text-xs text-[var(--primary-400)] hover:underline flex items-center gap-1"
                                                    >
                                                        {result.zkml.proof.on_chain.transaction_hash?.slice(0, 20)}...
                                                        <ExternalLinkIcon />
                                                    </a>
                                                </div>
                                                <div className="flex items-center justify-between">
                                                    <span className="text-[var(--foreground-muted)]">Block</span>
                                                    <span>{result.zkml.proof.on_chain.block_number}</span>
                                                </div>
                                                <div className="flex items-center justify-between">
                                                    <span className="text-[var(--foreground-muted)]">Gas Cost</span>
                                                    <span>
                                                        {result.zkml.proof.on_chain.gas_cost_SHM?.toFixed(6)} SHM
                                                        (~${result.zkml.proof.on_chain.gas_cost_usd?.toFixed(4)})
                                                    </span>
                                                </div>
                                            </>
                                        )}

                                        {!result.zkml.proof?.on_chain?.anchored && (
                                            <div className="text-xs text-yellow-400">
                                                ⚠️ Not anchored on chain (blockchain may be disconnected)
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Job ID */}
                            <div className="flex items-center justify-between p-3 rounded-lg bg-[var(--glass-bg)] text-sm">
                                <span className="text-[var(--foreground-muted)]">Job ID</span>
                                <span className="font-mono">{result.job_id}</span>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Recent Jobs */}
            <div className="glass-card p-6">
                <h2 className="text-xl font-semibold mb-4">Recent Jobs (from Backend)</h2>
                {jobs.length === 0 ? (
                    <div className="text-center py-8 text-[var(--foreground-muted)]">
                        <ClockIcon />
                        <p className="mt-2">No inference jobs yet</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="text-left text-sm text-[var(--foreground-muted)] border-b border-[var(--glass-border)]">
                                    <th className="pb-3 font-medium">Job ID</th>
                                    <th className="pb-3 font-medium">Model</th>
                                    <th className="pb-3 font-medium">Status</th>
                                    <th className="pb-3 font-medium">Latency</th>
                                    <th className="pb-3 font-medium">ZK Proof</th>
                                    <th className="pb-3 font-medium">Time</th>
                                </tr>
                            </thead>
                            <tbody className="text-sm">
                                {jobs.slice(0, 10).map((job) => {
                                    const model = models.find((m) => m.id === job.model_id);
                                    return (
                                        <tr
                                            key={job.id}
                                            className="border-b border-[var(--glass-border)]/50 cursor-pointer hover:bg-[var(--glass-bg)] transition-colors"
                                            onClick={() => setSelectedJob(job)}
                                        >
                                            <td className="py-3 font-mono">{job.id?.slice(0, 12)}...</td>
                                            <td className="py-3">{model?.name || job.model_id?.slice(0, 8) || "Unknown"}</td>
                                            <td className="py-3">
                                                <span
                                                    className={`badge ${job.status === "verified" || job.status === "completed"
                                                        ? "badge-success"
                                                        : job.status === "failed"
                                                            ? "bg-red-500/20 text-red-400"
                                                            : "badge-primary"
                                                        }`}
                                                >
                                                    {job.status}
                                                </span>
                                            </td>
                                            <td className="py-3">{job.latency_ms || 0}ms</td>
                                            <td className="py-3">
                                                {job.proof_hash ? (
                                                    <span className="badge badge-success">
                                                        <ShieldIcon /> Anchored
                                                    </span>
                                                ) : (
                                                    <span className="text-[var(--foreground-muted)]">-</span>
                                                )}
                                            </td>
                                            <td className="py-3 text-[var(--foreground-muted)]">
                                                {new Date(job.created_at).toLocaleTimeString()}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Job Details Modal */}
            {selectedJob && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div
                        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                        onClick={() => setSelectedJob(null)}
                    />
                    <div className="glass-card w-full max-w-md p-6 relative z-10 animate-fade-in">
                        {/* Header */}
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center gap-2">
                                <ShieldIcon />
                                <h2 className="text-xl font-bold text-[var(--secondary-400)]">
                                    ZK Proof {selectedJob.proof_hash ? "Verified" : "Not Available"}
                                </h2>
                            </div>
                            <button
                                onClick={() => setSelectedJob(null)}
                                className="p-2 rounded-lg hover:bg-[var(--glass-bg)] transition-colors text-[var(--foreground-muted)]"
                            >
                                ✕
                            </button>
                        </div>

                        <div className="space-y-4">
                            {/* Status */}
                            <div className="flex items-center justify-between p-3 rounded-lg bg-[var(--glass-bg)]">
                                <span className="text-[var(--foreground-muted)]">Status</span>
                                {selectedJob.proof_hash ? (
                                    <span className="badge badge-success">Valid</span>
                                ) : (
                                    <span className="badge bg-yellow-500/20 text-yellow-400">Not Verified</span>
                                )}
                            </div>

                            {/* Proof Hash */}
                            {selectedJob.proof_hash && (
                                <div className="flex items-center justify-between p-3 rounded-lg bg-[var(--glass-bg)]">
                                    <span className="text-[var(--foreground-muted)]">Proof Hash</span>
                                    <span className="font-mono text-xs max-w-[200px] truncate">
                                        {selectedJob.proof_hash}
                                    </span>
                                </div>
                            )}

                            {/* Shardeum Transaction Section */}
                            {selectedJob.proof_hash && (
                                <>
                                    <div className="border-t border-[var(--glass-border)] pt-4">
                                        <div className="text-sm font-semibold text-[var(--secondary-400)] mb-3 flex items-center gap-2">
                                            ⛓️ REAL Shardeum TRANSACTION
                                        </div>
                                    </div>

                                    {/* TX Hash */}
                                    <div className="flex items-center justify-between p-3 rounded-lg bg-[var(--glass-bg)]">
                                        <span className="text-[var(--foreground-muted)]">TX Hash</span>
                                        {selectedJob.transaction_hash ? (
                                            <a
                                                href={`https://explorer-mezame.shardeum.org/tx/${selectedJob.transaction_hash}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="font-mono text-xs text-[var(--primary-400)] hover:underline flex items-center gap-1"
                                            >
                                                {selectedJob.transaction_hash.slice(0, 20)}...
                                                <ExternalLinkIcon />
                                            </a>
                                        ) : (
                                            <span className="text-[var(--foreground-muted)] text-xs">Not anchored on-chain</span>
                                        )}
                                    </div>

                                    {/* Block */}
                                    <div className="flex items-center justify-between p-3 rounded-lg bg-[var(--glass-bg)]">
                                        <span className="text-[var(--foreground-muted)]">Block</span>
                                        <span>{selectedJob.block_number || "Pending"}</span>
                                    </div>

                                    {/* Gas Cost */}
                                    <div className="flex items-center justify-between p-3 rounded-lg bg-[var(--glass-bg)]">
                                        <span className="text-[var(--foreground-muted)]">Gas Cost</span>
                                        <span>~0.0001 SHM (~$0.25)</span>
                                    </div>
                                </>
                            )}

                            {/* No Proof Message */}
                            {!selectedJob.proof_hash && (
                                <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 text-sm">
                                    ⚠️ This job does not have a ZK proof. Run inference with ZKML enabled to generate verifiable proofs.
                                </div>
                            )}

                            {/* Job ID */}
                            <div className="flex items-center justify-between p-3 rounded-lg bg-[var(--glass-bg)] border-t border-[var(--glass-border)]">
                                <span className="text-[var(--foreground-muted)]">Job ID</span>
                                <span className="font-mono text-xs">{selectedJob.id}</span>
                            </div>

                            {/* Output Data */}
                            {selectedJob.output_data && (
                                <div className="p-3 rounded-lg bg-[var(--glass-bg)] max-h-48 overflow-y-auto">
                                    <span className="text-[var(--foreground-muted)] text-sm block mb-2">Output</span>
                                    <pre className="text-xs font-mono overflow-x-auto whitespace-pre-wrap">
                                        {JSON.stringify(selectedJob.output_data, null, 2)}
                                    </pre>
                                </div>
                            )}

                            {/* Close Button */}
                            <button
                                onClick={() => setSelectedJob(null)}
                                className="btn btn-primary w-full mt-4"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default function InferencePage() {
    return (
        <Suspense
            fallback={
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[var(--primary-500)]"></div>
                </div>
            }
        >
            <InferenceContent />
        </Suspense>
    );
}
