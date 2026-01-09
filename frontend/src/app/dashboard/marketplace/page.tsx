"use client";

import { useState, useEffect } from "react";
import * as api from "@/lib/api";

// Icons
const ShopIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
    </svg>
);

const StarIcon = () => (
    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
    </svg>
);

const BoltIcon = () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
);

const ShieldIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
);

const WalletIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
    </svg>
);

const XIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
);

const SearchIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
);

const PlayIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

const CheckIcon = () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
);

interface Listing {
    id: string;
    model_id: string;
    model_name: string;
    description: string;
    price_per_inference: number;
    category: string;
    tags: string[];
    rating: number;
    total_inferences: number;
    owner_id: string;
    model_type: string;
    is_active: boolean;
    created_at: string;
}

interface Purchase {
    id: string;
    listing_id: string;
    inferences_bought: number;
    inferences_remaining: number;
    total_paid: number;
    listing_name: string;
}

const CATEGORIES = [
    { id: "all", name: "All Categories", icon: "📦" },
    { id: "classification", name: "Classification", icon: "🖼️" },
    { id: "nlp", name: "NLP / Text", icon: "📝" },
    { id: "regression", name: "Regression", icon: "📈" },
    { id: "embedding", name: "Embeddings", icon: "🧮" },
    { id: "generative", name: "Generative", icon: "✨" },
];

function ListingCard({
    listing,
    onPurchase,
    purchased,
}: {
    listing: Listing;
    onPurchase: (listing: Listing) => void;
    purchased?: Purchase;
}) {
    const category = CATEGORIES.find((c) => c.id === listing.category);

    return (
        <div className="glass-card p-6 hover-lift group">
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[var(--primary-500)] to-[var(--accent-500)] flex items-center justify-center text-2xl">
                        {category?.icon || "📦"}
                    </div>
                    <div>
                        <h3 className="font-semibold text-lg line-clamp-1">{listing.model_name}</h3>
                        <div className="flex items-center gap-2 text-sm text-[var(--foreground-muted)]">
                            <span className="flex items-center gap-1 text-[var(--accent-400)]">
                                <StarIcon />
                                {listing.rating?.toFixed(1) || "4.5"}
                            </span>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                                <BoltIcon />
                                {(listing.total_inferences || 0).toLocaleString()} runs
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Description */}
            <p className="text-sm text-[var(--foreground-muted)] mb-4 line-clamp-2">
                {listing.description}
            </p>

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mb-4">
                {(listing.tags || []).slice(0, 3).map((tag) => (
                    <span key={tag} className="badge badge-primary text-xs">
                        {tag}
                    </span>
                ))}
            </div>

            {/* ZKML Verified Badge */}
            <div className="flex items-center gap-2 p-3 rounded-lg bg-[var(--secondary-500)]/10 mb-4">
                <ShieldIcon />
                <span className="text-xs text-[var(--secondary-400)]">
                    ZKML Verified • Proof anchored on Sepolia
                </span>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between">
                <div>
                    <div className="text-2xl font-bold text-gradient">
                        ${(listing.price_per_inference || 0.05).toFixed(2)}
                    </div>
                    <div className="text-xs text-[var(--foreground-muted)]">per inference</div>
                </div>
                {purchased && purchased.inferences_remaining > 0 ? (
                    <a
                        href={`/dashboard/inference?model=${listing.model_id}`}
                        className="btn btn-success"
                    >
                        <PlayIcon />
                        Use ({purchased.inferences_remaining} left)
                    </a>
                ) : (
                    <button onClick={() => onPurchase(listing)} className="btn btn-primary">
                        <WalletIcon />
                        Purchase
                    </button>
                )}
            </div>
        </div>
    );
}

function PurchaseModal({
    isOpen,
    onClose,
    listing,
    onConfirm,
    userBalance,
}: {
    isOpen: boolean;
    onClose: () => void;
    listing: Listing | null;
    onConfirm: (listing: Listing, count: number) => void;
    userBalance: number;
}) {
    const [count, setCount] = useState(10);
    const [purchasing, setPurchasing] = useState(false);

    if (!isOpen || !listing) return null;

    const totalCost = (listing.price_per_inference || 0.05) * count;
    const canAfford = userBalance >= totalCost;

    const handleConfirm = async () => {
        if (canAfford && !purchasing) {
            setPurchasing(true);
            try {
                await onConfirm(listing, count);
                onClose();
            } finally {
                setPurchasing(false);
            }
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
            <div className="glass-card w-full max-w-md p-6 relative z-10 animate-fade-in">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold">Purchase Inference</h2>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-[var(--glass-bg)] transition-colors"
                    >
                        <XIcon />
                    </button>
                </div>

                <div className="space-y-6">
                    {/* Model Info */}
                    <div className="p-4 rounded-xl bg-[var(--glass-bg)]">
                        <h3 className="font-semibold">{listing.model_name}</h3>
                        <p className="text-sm text-[var(--foreground-muted)] mt-1">
                            ${(listing.price_per_inference || 0.05).toFixed(2)} per inference
                        </p>
                    </div>

                    {/* Quantity */}
                    <div>
                        <label className="block text-sm font-medium mb-2">
                            Number of Inferences
                        </label>
                        <div className="flex items-center gap-4">
                            <input
                                type="range"
                                min="1"
                                max="100"
                                value={count}
                                onChange={(e) => setCount(parseInt(e.target.value))}
                                className="flex-1"
                            />
                            <input
                                type="number"
                                min="1"
                                value={count}
                                onChange={(e) => setCount(Math.max(1, parseInt(e.target.value) || 1))}
                                className="input w-20 text-center"
                            />
                        </div>
                    </div>

                    {/* Cost Breakdown */}
                    <div className="p-4 rounded-xl bg-[var(--glass-bg)] space-y-2">
                        <div className="flex items-center justify-between">
                            <span className="text-[var(--foreground-muted)]">Price per inference</span>
                            <span>${(listing.price_per_inference || 0.05).toFixed(2)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-[var(--foreground-muted)]">Quantity</span>
                            <span>×{count}</span>
                        </div>
                        <div className="border-t border-[var(--glass-border)] pt-2 mt-2">
                            <div className="flex items-center justify-between font-semibold">
                                <span>Total</span>
                                <span className="text-gradient text-xl">${totalCost.toFixed(2)}</span>
                            </div>
                        </div>
                    </div>

                    {/* Balance Check */}
                    <div
                        className={`p-4 rounded-xl ${canAfford
                            ? "bg-[var(--secondary-500)]/10 border border-[var(--secondary-500)]/30"
                            : "bg-red-500/10 border border-red-500/30"
                            }`}
                    >
                        <div className="flex items-center justify-between">
                            <span className={canAfford ? "text-[var(--secondary-400)]" : "text-red-400"}>
                                Your Balance
                            </span>
                            <span className={`font-semibold ${canAfford ? "text-[var(--secondary-400)]" : "text-red-400"}`}>
                                ${userBalance.toFixed(2)}
                            </span>
                        </div>
                        {!canAfford && (
                            <p className="text-sm text-red-400 mt-2">
                                Insufficient balance. Add funds to continue.
                            </p>
                        )}
                    </div>

                    {/* Escrow Notice */}
                    <div className="flex items-start gap-3 p-3 rounded-lg bg-[var(--glass-bg)]">
                        <ShieldIcon />
                        <div className="text-sm">
                            <p className="font-medium">ZKML Verified</p>
                            <p className="text-[var(--foreground-muted)]">
                                All inferences are verified with ZK proofs anchored on Sepolia.
                            </p>
                        </div>
                    </div>

                    {/* Confirm Button */}
                    <button
                        onClick={handleConfirm}
                        disabled={!canAfford || purchasing}
                        className="btn btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {purchasing ? (
                            <>
                                <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
                                Processing...
                            </>
                        ) : (
                            <>
                                <ShopIcon />
                                Confirm Purchase
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}

function MyPurchasesSection({ purchases }: { purchases: Purchase[] }) {
    if (purchases.length === 0) return null;

    return (
        <div className="glass-card p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">My Purchases</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {purchases.map((purchase) => (
                    <div
                        key={purchase.id}
                        className="p-4 rounded-xl bg-[var(--glass-bg)] flex items-center justify-between"
                    >
                        <div>
                            <h3 className="font-medium">{purchase.listing_name}</h3>
                            <p className="text-sm text-[var(--foreground-muted)]">
                                {purchase.inferences_remaining} / {purchase.inferences_bought} remaining
                            </p>
                        </div>
                        {purchase.inferences_remaining > 0 && (
                            <a
                                href={`/dashboard/inference?purchase=${purchase.id}`}
                                className="btn btn-success btn-sm"
                            >
                                <PlayIcon />
                                Use
                            </a>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function MarketplacePage() {
    const [listings, setListings] = useState<Listing[]>([]);
    const [purchases, setPurchases] = useState<Purchase[]>([]);
    const [selectedCategory, setSelectedCategory] = useState("all");
    const [searchQuery, setSearchQuery] = useState("");
    const [sortBy, setSortBy] = useState("popular");
    const [selectedListing, setSelectedListing] = useState<Listing | null>(null);
    const [showPurchaseModal, setShowPurchaseModal] = useState(false);
    const [userBalance, setUserBalance] = useState(1000);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch listings from backend API
                const listingsRes = await api.getMarketplaceListings();
                if (listingsRes.success && listingsRes.data) {
                    setListings(listingsRes.data);
                }

                // Load purchases from localStorage (still simulated)
                const storedPurchases = localStorage.getItem("v-inference-purchases");
                if (storedPurchases) {
                    setPurchases(JSON.parse(storedPurchases));
                }

                // Load user balance from localStorage
                const storedUser = localStorage.getItem("v-inference-user");
                if (storedUser) {
                    const user = JSON.parse(storedUser);
                    setUserBalance(user.balance || 1000);
                }
            } catch (err) {
                console.error("Error fetching marketplace data:", err);
                setError("Failed to load marketplace listings");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const handlePurchase = (listing: Listing) => {
        setSelectedListing(listing);
        setShowPurchaseModal(true);
    };

    const confirmPurchase = async (listing: Listing, count: number) => {
        const totalCost = (listing.price_per_inference || 0.05) * count;

        // Update user balance
        const newBalance = userBalance - totalCost;
        setUserBalance(newBalance);

        // Save to localStorage
        const storedUser = localStorage.getItem("v-inference-user");
        const user = storedUser ? JSON.parse(storedUser) : { balance: 1000 };
        user.balance = newBalance;
        localStorage.setItem("v-inference-user", JSON.stringify(user));

        // Create purchase
        const newPurchase: Purchase = {
            id: "purchase-" + Math.random().toString(36).substr(2, 9),
            listing_id: listing.id,
            inferences_bought: count,
            inferences_remaining: count,
            total_paid: totalCost,
            listing_name: listing.model_name,
        };

        const updatedPurchases = [...purchases, newPurchase];
        setPurchases(updatedPurchases);
        localStorage.setItem("v-inference-purchases", JSON.stringify(updatedPurchases));
    };

    // Filter and sort listings
    let filteredListings = listings.filter(l => l.is_active !== false);

    if (selectedCategory !== "all") {
        filteredListings = filteredListings.filter((l) => l.category === selectedCategory || l.model_type === selectedCategory);
    }

    if (searchQuery) {
        const query = searchQuery.toLowerCase();
        filteredListings = filteredListings.filter(
            (l) =>
                l.model_name.toLowerCase().includes(query) ||
                l.description.toLowerCase().includes(query) ||
                (l.tags || []).some((t) => t.toLowerCase().includes(query))
        );
    }

    // Sort
    switch (sortBy) {
        case "popular":
            filteredListings = [...filteredListings].sort((a, b) => (b.total_inferences || 0) - (a.total_inferences || 0));
            break;
        case "rating":
            filteredListings = [...filteredListings].sort((a, b) => (b.rating || 0) - (a.rating || 0));
            break;
        case "price_low":
            filteredListings = [...filteredListings].sort((a, b) => (a.price_per_inference || 0) - (b.price_per_inference || 0));
            break;
        case "price_high":
            filteredListings = [...filteredListings].sort((a, b) => (b.price_per_inference || 0) - (a.price_per_inference || 0));
            break;
        case "newest":
            filteredListings = [...filteredListings].sort(
                (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            );
            break;
    }

    const getPurchaseForListing = (listingId: string) => {
        return purchases.find((p) => p.listing_id === listingId);
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
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Marketplace</h1>
                    <p className="text-[var(--foreground-muted)]">
                        Buy verified AI inference from trusted providers • All proofs anchored on Sepolia
                    </p>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[var(--glass-bg)]">
                    <WalletIcon />
                    <span className="text-sm text-[var(--foreground-muted)]">Balance:</span>
                    <span className="font-semibold text-[var(--secondary-400)]">
                        ${userBalance.toFixed(2)}
                    </span>
                </div>
            </div>

            {/* Error Banner */}
            {error && (
                <div className="p-4 rounded-xl bg-red-500/20 border border-red-500/50 text-red-400">
                    ⚠️ {error}
                </div>
            )}

            {/* My Purchases */}
            <MyPurchasesSection purchases={purchases.filter((p) => p.inferences_remaining > 0)} />

            {/* Search and Filters */}
            <div className="flex flex-col lg:flex-row gap-4">
                {/* Search */}
                <div className="relative flex-1">
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--foreground-muted)]">
                        <SearchIcon />
                    </div>
                    <input
                        type="text"
                        placeholder="Search models..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="input pl-10"
                    />
                </div>

                {/* Sort */}
                <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="input w-full lg:w-48"
                >
                    <option value="popular">Most Popular</option>
                    <option value="rating">Highest Rated</option>
                    <option value="price_low">Price: Low to High</option>
                    <option value="price_high">Price: High to Low</option>
                    <option value="newest">Newest</option>
                </select>
            </div>

            {/* Categories */}
            <div className="flex flex-wrap gap-2">
                {CATEGORIES.map((category) => (
                    <button
                        key={category.id}
                        onClick={() => setSelectedCategory(category.id)}
                        className={`px-4 py-2 rounded-xl transition-all ${selectedCategory === category.id
                            ? "bg-[var(--primary-500)] text-white"
                            : "bg-[var(--glass-bg)] text-[var(--foreground-muted)] hover:bg-[var(--glass-border)]"
                            }`}
                    >
                        <span className="mr-2">{category.icon}</span>
                        {category.name}
                    </button>
                ))}
            </div>

            {/* Listings Grid */}
            {filteredListings.length === 0 ? (
                <div className="glass-card p-12 text-center">
                    <div className="flex justify-center mb-4">
                        <ShopIcon />
                    </div>
                    <h2 className="text-xl font-semibold mt-4 mb-2">No listings found</h2>
                    <p className="text-[var(--foreground-muted)]">
                        Try adjusting your filters or search query
                    </p>
                </div>
            ) : (
                <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {filteredListings.map((listing) => (
                        <ListingCard
                            key={listing.id}
                            listing={listing}
                            onPurchase={handlePurchase}
                            purchased={getPurchaseForListing(listing.id)}
                        />
                    ))}
                </div>
            )}

            {/* Purchase Modal */}
            <PurchaseModal
                isOpen={showPurchaseModal}
                onClose={() => {
                    setShowPurchaseModal(false);
                    setSelectedListing(null);
                }}
                listing={selectedListing}
                onConfirm={confirmPurchase}
                userBalance={userBalance}
            />
        </div>
    );
}
