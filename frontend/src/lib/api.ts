const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types
export interface User {
    id: string;
    wallet_address: string;
    username: string;
    balance: number;
    created_at: string;
}

export interface AIModel {
    id: string;
    name: string;
    description: string;
    model_type: string;
    owner_id: string;
    is_public: boolean;
    file_path?: string;
    metadata: Record<string, unknown>;
    total_inferences: number;
    average_latency_ms: number;
    created_at: string;
}

export interface InferenceJob {
    id: string;
    model_id: string;
    user_id: string;
    input_data: Record<string, unknown>;
    output_data?: Record<string, unknown>;
    status: "pending" | "processing" | "completed" | "failed" | "verified";
    proof_hash?: string;
    transaction_hash?: string;
    block_number?: number;
    verification_status?: string;
    latency_ms?: number;
    created_at: string;
    completed_at?: string;
}

export interface MarketplaceListing {
    id: string;
    model_id?: string;
    model_name: string;
    description: string;
    price_per_inference: number;
    category: string;
    tags: string[];
    rating: number;
    total_inferences: number;
    total_revenue: number;
    owner_id: string;
    is_active: boolean;
    model_type?: string;
    created_at: string;
}

export interface Purchase {
    id: string;
    user_id: string;
    listing_id: string;
    model_id: string;
    inferences_bought: number;
    inferences_remaining: number;
    total_paid: number;
    escrow_status: "locked" | "released" | "refunded";
    created_at: string;
    listing_name?: string;
    listing_price?: number;
}

export interface ZKProof {
    proof_hash: string;
    circuit_hash: string;
    verification_key: string;
    proof_type: string;
    is_valid: boolean;
    generated_at: string;
    generation_time_ms: number;
}

export interface APIResponse<T = unknown> {
    success: boolean;
    message: string;
    data: T;
}

// API Functions

// Users
export async function connectWallet(
    walletAddress: string,
    username?: string
): Promise<APIResponse<User>> {
    const params = new URLSearchParams({ wallet_address: walletAddress });
    if (username) params.append("username", username);

    const res = await fetch(`${API_BASE}/api/users/connect?${params}`, {
        method: "POST",
    });
    return res.json();
}

export async function getUserDashboard(
    userId: string
): Promise<
    APIResponse<{
        user: User;
        stats: Record<string, number>;
        recent_models: AIModel[];
        recent_jobs: InferenceJob[];
        active_listings: MarketplaceListing[];
        active_purchases: Purchase[];
    }>
> {
    const res = await fetch(`${API_BASE}/api/users/${userId}/dashboard`);
    return res.json();
}

export async function addFunds(
    userId: string,
    amount: number
): Promise<APIResponse<{ new_balance: number }>> {
    const res = await fetch(
        `${API_BASE}/api/users/${userId}/add-funds?amount=${amount}`,
        {
            method: "POST",
        }
    );
    return res.json();
}

// Models
export async function uploadModel(formData: FormData): Promise<APIResponse<AIModel>> {
    const res = await fetch(`${API_BASE}/api/models/upload`, {
        method: "POST",
        body: formData,
    });
    return res.json();
}

export async function getModels(ownerId?: string): Promise<APIResponse<AIModel[]>> {
    const params = ownerId ? `?owner_id=${ownerId}` : "";
    const res = await fetch(`${API_BASE}/api/models/${params}`);
    return res.json();
}

export async function getModel(modelId: string): Promise<APIResponse<AIModel>> {
    const res = await fetch(`${API_BASE}/api/models/${modelId}`);
    return res.json();
}

export async function deleteModel(
    modelId: string,
    ownerId: string
): Promise<APIResponse<null>> {
    const res = await fetch(
        `${API_BASE}/api/models/${modelId}?owner_id=${ownerId}`,
        {
            method: "DELETE",
        }
    );
    return res.json();
}

export async function getModelStats(
    modelId: string
): Promise<APIResponse<Record<string, number>>> {
    const res = await fetch(`${API_BASE}/api/models/${modelId}/stats`);
    return res.json();
}

// Inference
export async function runInference(
    modelId: string,
    inputData: Record<string, unknown>,
    useZkml: boolean = true,
    simulateFailure: boolean = false
): Promise<
    APIResponse<{
        job_id: string;
        model_id: string;
        output: Record<string, unknown>;
        inference_time_ms: number;
        total_time_ms: number;
        zkml?: {
            enabled: boolean;
            proof: ZKProof;
            verification: {
                is_valid: boolean;
                message: string;
                gas_estimate: Record<string, unknown>;
            };
        };
    }>
> {
    const res = await fetch(`${API_BASE}/api/inference/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            model_id: modelId,
            input_data: inputData,
            use_zkml: useZkml,
            simulate_failure: simulateFailure,
        }),
    });
    return res.json();
}

export async function getJob(
    jobId: string
): Promise<APIResponse<InferenceJob & { proof?: ZKProof }>> {
    const res = await fetch(`${API_BASE}/api/inference/job/${jobId}`);
    return res.json();
}

export async function getJobs(
    userId?: string,
    modelId?: string
): Promise<APIResponse<InferenceJob[]>> {
    const params = new URLSearchParams();
    if (userId) params.append("user_id", userId);
    if (modelId) params.append("model_id", modelId);

    const res = await fetch(`${API_BASE}/api/inference/jobs?${params}`);
    return res.json();
}

export async function getSampleInputs(): Promise<
    APIResponse<
        Record<
            string,
            {
                description: string;
                input: Record<string, unknown>;
            }
        >
    >
> {
    const res = await fetch(`${API_BASE}/api/inference/sample-inputs`);
    return res.json();
}

// Marketplace
export async function createListing(
    modelId: string,
    pricePerInference: number,
    description: string,
    category: string,
    tags: string[],
    ownerId: string
): Promise<APIResponse<MarketplaceListing>> {
    const res = await fetch(`${API_BASE}/api/marketplace/list?owner_id=${ownerId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            model_id: modelId,
            price_per_inference: pricePerInference,
            description,
            category,
            tags,
        }),
    });
    return res.json();
}

export async function getListings(
    category?: string,
    sortBy?: string
): Promise<APIResponse<MarketplaceListing[]>> {
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (sortBy) params.append("sort_by", sortBy);

    const res = await fetch(`${API_BASE}/api/marketplace/listings?${params}`);
    return res.json();
}

export async function getListing(
    listingId: string
): Promise<APIResponse<MarketplaceListing>> {
    const res = await fetch(`${API_BASE}/api/marketplace/listing/${listingId}`);
    return res.json();
}

export async function purchaseInference(
    listingId: string,
    inferencesCount: number,
    userId: string
): Promise<
    APIResponse<{
        purchase: Purchase;
        escrow: Record<string, unknown>;
        remaining_balance: number;
    }>
> {
    const res = await fetch(
        `${API_BASE}/api/marketplace/purchase?user_id=${userId}`,
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                listing_id: listingId,
                inferences_count: inferencesCount,
            }),
        }
    );
    return res.json();
}

export async function usePurchasedInference(
    purchaseId: string,
    inputData: Record<string, unknown>
): Promise<
    APIResponse<{
        job_id: string;
        output: Record<string, unknown>;
        inference_time_ms: number;
        total_time_ms: number;
        zkml_proof: {
            proof_hash: string;
            is_verified: boolean;
            verification_message: string;
            gas_estimate: Record<string, unknown>;
        };
        credits_remaining: number;
        escrow_released: boolean;
        payment_to_provider: number;
    }>
> {
    const res = await fetch(
        `${API_BASE}/api/marketplace/use-inference/${purchaseId}`,
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(inputData),
        }
    );
    return res.json();
}

export async function getUserPurchases(
    userId: string
): Promise<APIResponse<Purchase[]>> {
    const res = await fetch(
        `${API_BASE}/api/marketplace/purchases?user_id=${userId}`
    );
    return res.json();
}

export async function getCategories(): Promise<
    APIResponse<{ id: string; name: string; icon: string }[]>
> {
    const res = await fetch(`${API_BASE}/api/marketplace/categories`);
    return res.json();
}

// Platform Stats
export async function getPlatformStats(): Promise<{
    platform: string;
    stats: Record<string, number>;
    network: Record<string, string>;
}> {
    const res = await fetch(`${API_BASE}/api/stats`);
    return res.json();
}
