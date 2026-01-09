"use client";

import { useState, useEffect, useRef } from "react";
import * as api from "@/lib/api";

// Icons
const UploadIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
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

const TrashIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
);

const ShopIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
    </svg>
);

const PlusIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
    </svg>
);

const XIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
);

const MODEL_TYPES = [
    { value: "classification", label: "Classification", icon: "🖼️" },
    { value: "regression", label: "Regression", icon: "📈" },
    { value: "nlp", label: "NLP / Text", icon: "📝" },
    { value: "embedding", label: "Embedding", icon: "🧮" },
    { value: "generative", label: "Generative", icon: "✨" },
    { value: "custom", label: "Custom", icon: "📦" },
];

function ModelCard({
    model,
    onDelete,
    onListMarketplace,
}: {
    model: api.AIModel;
    onDelete: (id: string) => void;
    onListMarketplace: (model: api.AIModel) => void;
}) {
    const typeInfo = MODEL_TYPES.find((t) => t.value === model.model_type) || MODEL_TYPES[5];

    return (
        <div className="glass-card p-6 hover-lift group">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[var(--primary-500)] to-[var(--accent-500)] flex items-center justify-center text-2xl">
                        {typeInfo.icon}
                    </div>
                    <div>
                        <h3 className="font-semibold text-lg">{model.name}</h3>
                        <p className="text-sm text-[var(--foreground-muted)]">{typeInfo.label}</p>
                    </div>
                </div>
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                        onClick={() => onListMarketplace(model)}
                        className="p-2 rounded-lg bg-[var(--secondary-500)]/20 text-[var(--secondary-400)] hover:bg-[var(--secondary-500)]/30 transition-colors"
                        title="List on Marketplace"
                    >
                        <ShopIcon />
                    </button>
                    <button
                        onClick={() => onDelete(model.id)}
                        className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                        title="Delete"
                    >
                        <TrashIcon />
                    </button>
                </div>
            </div>

            {model.description && (
                <p className="text-sm text-[var(--foreground-muted)] mb-4 line-clamp-2">
                    {model.description}
                </p>
            )}

            <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-center p-3 rounded-lg bg-[var(--glass-bg)]">
                    <div className="text-xl font-bold text-[var(--primary-400)]">
                        {model.total_inferences}
                    </div>
                    <div className="text-xs text-[var(--foreground-muted)]">Inferences</div>
                </div>
                <div className="text-center p-3 rounded-lg bg-[var(--glass-bg)]">
                    <div className="text-xl font-bold text-[var(--accent-400)]">
                        {model.average_latency_ms}ms
                    </div>
                    <div className="text-xs text-[var(--foreground-muted)]">Avg Latency</div>
                </div>
            </div>

            <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                    {model.is_public ? (
                        <span className="badge badge-success">Public</span>
                    ) : (
                        <span className="badge badge-primary">Private</span>
                    )}
                </div>
                <a
                    href={`/dashboard/inference?model=${model.id}`}
                    className="text-[var(--primary-400)] hover:underline flex items-center gap-1"
                >
                    <BoltIcon /> Run
                </a>
            </div>
        </div>
    );
}

function UploadModal({
    isOpen,
    onClose,
    onUpload,
}: {
    isOpen: boolean;
    onClose: () => void;
    onUpload: (formData: FormData) => Promise<void>;
}) {
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [modelType, setModelType] = useState("classification");
    const [isPublic, setIsPublic] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            setFile(droppedFile);
            if (!name) {
                setName(droppedFile.name.replace(/\.[^/.]+$/, ""));
            }
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
            if (!name) {
                setName(selectedFile.name.replace(/\.[^/.]+$/, ""));
            }
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!name) return;

        setUploading(true);

        const formData = new FormData();
        formData.append("name", name);
        formData.append("description", description);
        formData.append("model_type", modelType);
        formData.append("is_public", String(isPublic));
        formData.append("owner_id", "demo-user");

        if (file) {
            formData.append("file", file);
        }

        await onUpload(formData);

        // Reset form
        setName("");
        setDescription("");
        setModelType("classification");
        setIsPublic(false);
        setFile(null);
        setUploading(false);
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
            <div className="glass-card w-full max-w-lg p-6 relative z-10 animate-fade-in max-h-[90vh] overflow-y-auto">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold">Upload Model</h2>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-[var(--glass-bg)] transition-colors"
                    >
                        <XIcon />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Drop Zone */}
                    <div
                        onDragOver={(e) => {
                            e.preventDefault();
                            setIsDragging(true);
                        }}
                        onDragLeave={() => setIsDragging(false)}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current?.click()}
                        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${isDragging
                                ? "border-[var(--primary-500)] bg-[var(--primary-500)]/10"
                                : "border-[var(--glass-border)] hover:border-[var(--primary-500)]/50"
                            }`}
                    >
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".onnx,.pt,.pth,.h5,.pb,.tflite,.pkl"
                            onChange={handleFileSelect}
                            className="hidden"
                        />
                        <UploadIcon />
                        <p className="mt-2 font-medium">
                            {file ? file.name : "Drop your model file here"}
                        </p>
                        <p className="text-sm text-[var(--foreground-muted)] mt-1">
                            Supports ONNX, PyTorch, TensorFlow, and pickle files
                        </p>
                        {file && (
                            <p className="text-sm text-[var(--secondary-400)] mt-2">
                                {(file.size / (1024 * 1024)).toFixed(2)} MB
                            </p>
                        )}
                    </div>

                    {/* Model Name */}
                    <div>
                        <label className="block text-sm font-medium mb-2">Model Name *</label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="My Awesome Model"
                            className="input"
                            required
                        />
                    </div>

                    {/* Description */}
                    <div>
                        <label className="block text-sm font-medium mb-2">Description</label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Describe what your model does..."
                            className="input min-h-[100px] resize-none"
                        />
                    </div>

                    {/* Model Type */}
                    <div>
                        <label className="block text-sm font-medium mb-2">Model Type</label>
                        <div className="grid grid-cols-3 gap-2">
                            {MODEL_TYPES.map((type) => (
                                <button
                                    key={type.value}
                                    type="button"
                                    onClick={() => setModelType(type.value)}
                                    className={`p-3 rounded-xl text-center transition-all ${modelType === type.value
                                            ? "bg-[var(--primary-500)]/20 border border-[var(--primary-500)]"
                                            : "bg-[var(--glass-bg)] border border-transparent hover:border-[var(--glass-border)]"
                                        }`}
                                >
                                    <div className="text-2xl mb-1">{type.icon}</div>
                                    <div className="text-xs">{type.label}</div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Public Toggle */}
                    <div className="flex items-center justify-between p-4 rounded-xl bg-[var(--glass-bg)]">
                        <div>
                            <div className="font-medium">Make model public</div>
                            <div className="text-sm text-[var(--foreground-muted)]">
                                Allow others to use your model on the marketplace
                            </div>
                        </div>
                        <button
                            type="button"
                            onClick={() => setIsPublic(!isPublic)}
                            className={`w-12 h-6 rounded-full transition-colors ${isPublic ? "bg-[var(--primary-500)]" : "bg-[var(--dark-600)]"
                                }`}
                        >
                            <div
                                className={`w-5 h-5 rounded-full bg-white transition-transform ${isPublic ? "translate-x-6" : "translate-x-0.5"
                                    }`}
                            />
                        </button>
                    </div>

                    {/* Submit */}
                    <button
                        type="submit"
                        className="btn btn-primary w-full"
                        disabled={uploading}
                    >
                        {uploading ? (
                            <>
                                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                                Uploading...
                            </>
                        ) : (
                            <>
                                <UploadIcon />
                                Upload Model
                            </>
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
}

function ListMarketplaceModal({
    isOpen,
    onClose,
    model,
    onList,
}: {
    isOpen: boolean;
    onClose: () => void;
    model: api.AIModel | null;
    onList: (modelId: string, price: number, description: string) => Promise<void>;
}) {
    const [price, setPrice] = useState("0.05");
    const [description, setDescription] = useState("");
    const [listing, setListing] = useState(false);

    useEffect(() => {
        if (model) {
            setDescription(model.description || "");
        }
    }, [model]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (model) {
            setListing(true);
            await onList(model.id, parseFloat(price), description);
            setListing(false);
            onClose();
        }
    };

    if (!isOpen || !model) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
            <div className="glass-card w-full max-w-md p-6 relative z-10 animate-fade-in">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold">List on Marketplace</h2>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-[var(--glass-bg)] transition-colors"
                    >
                        <XIcon />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="p-4 rounded-xl bg-[var(--glass-bg)]">
                        <div className="flex items-center gap-3">
                            <CubeIcon />
                            <div>
                                <div className="font-semibold">{model.name}</div>
                                <div className="text-sm text-[var(--foreground-muted)]">
                                    {model.model_type}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">
                            Price per Inference ($)
                        </label>
                        <input
                            type="number"
                            step="0.01"
                            min="0.01"
                            value={price}
                            onChange={(e) => setPrice(e.target.value)}
                            className="input"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">
                            Marketplace Description
                        </label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Describe what your model can do for buyers..."
                            className="input min-h-[100px] resize-none"
                        />
                    </div>

                    <div className="p-4 rounded-xl bg-[var(--secondary-500)]/10 border border-[var(--secondary-500)]/30">
                        <p className="text-sm text-[var(--secondary-400)]">
                            ✨ Your model architecture will remain private. Buyers can only
                            use inference, not download or view your model.
                        </p>
                    </div>

                    <button
                        type="submit"
                        className="btn btn-success w-full"
                        disabled={listing}
                    >
                        {listing ? (
                            "Listing..."
                        ) : (
                            <>
                                <ShopIcon />
                                List for ${price} per inference
                            </>
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
}

export default function ModelsPage() {
    const [models, setModels] = useState<api.AIModel[]>([]);
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [showMarketplaceModal, setShowMarketplaceModal] = useState(false);
    const [selectedModel, setSelectedModel] = useState<api.AIModel | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch models from backend
    const fetchModels = async () => {
        try {
            setLoading(true);
            const res = await api.getModels();
            if (res.success && res.data) {
                setModels(res.data);
            }
        } catch (err) {
            console.error("Error fetching models:", err);
            setError("Failed to connect to backend");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchModels();
    }, []);

    const handleUpload = async (formData: FormData) => {
        try {
            const res = await api.uploadModel(formData);
            if (res.success) {
                await fetchModels(); // Refresh list
            } else {
                setError(res.message);
            }
        } catch (err) {
            console.error("Upload error:", err);
            setError("Failed to upload model");
        }
    };

    const handleDelete = async (id: string) => {
        if (confirm("Are you sure you want to delete this model?")) {
            try {
                const res = await api.deleteModel(id, "demo-user");
                if (res.success) {
                    await fetchModels(); // Refresh list
                }
            } catch (err) {
                console.error("Delete error:", err);
            }
        }
    };

    const handleListMarketplace = (model: api.AIModel) => {
        setSelectedModel(model);
        setShowMarketplaceModal(true);
    };

    const handleList = async (modelId: string, price: number, description: string) => {
        try {
            const model = models.find((m) => m.id === modelId);
            if (!model) return;

            await api.createListing(
                modelId,
                price,
                description,
                model.model_type,
                [],
                "demo-user"
            );

            await fetchModels(); // Refresh
        } catch (err) {
            console.error("Listing error:", err);
        }
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
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold mb-2">My Models</h1>
                    <p className="text-[var(--foreground-muted)]">
                        Upload and manage your AI models (stored in backend)
                    </p>
                </div>
                <button
                    onClick={() => setShowUploadModal(true)}
                    className="btn btn-primary"
                >
                    <PlusIcon />
                    Upload Model
                </button>
            </div>

            {/* Error Banner */}
            {error && (
                <div className="p-4 rounded-xl bg-red-500/20 border border-red-500/50 text-red-400">
                    ⚠️ {error}
                </div>
            )}

            {/* Models Grid */}
            {models.length === 0 ? (
                <div className="glass-card p-12 text-center">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-[var(--primary-500)]/20 flex items-center justify-center">
                        <CubeIcon />
                    </div>
                    <h2 className="text-xl font-semibold mb-2">No models yet</h2>
                    <p className="text-[var(--foreground-muted)] mb-6 max-w-md mx-auto">
                        Upload your first AI model to start running verified inference on
                        the decentralized network.
                    </p>
                    <button
                        onClick={() => setShowUploadModal(true)}
                        className="btn btn-primary"
                    >
                        <UploadIcon />
                        Upload Your First Model
                    </button>
                </div>
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {models.map((model) => (
                        <ModelCard
                            key={model.id}
                            model={model}
                            onDelete={handleDelete}
                            onListMarketplace={handleListMarketplace}
                        />
                    ))}
                </div>
            )}

            {/* Modals */}
            <UploadModal
                isOpen={showUploadModal}
                onClose={() => setShowUploadModal(false)}
                onUpload={handleUpload}
            />
            <ListMarketplaceModal
                isOpen={showMarketplaceModal}
                onClose={() => {
                    setShowMarketplaceModal(false);
                    setSelectedModel(null);
                }}
                model={selectedModel}
                onList={handleList}
            />
        </div>
    );
}
