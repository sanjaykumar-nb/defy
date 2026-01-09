"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

// Icons as SVG components
const ShieldCheckIcon = () => (
  <svg
    className="w-6 h-6"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
    />
  </svg>
);

const CubeIcon = () => (
  <svg
    className="w-6 h-6"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
    />
  </svg>
);

const BoltIcon = () => (
  <svg
    className="w-6 h-6"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M13 10V3L4 14h7v7l9-11h-7z"
    />
  </svg>
);

const ChartIcon = () => (
  <svg
    className="w-6 h-6"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
    />
  </svg>
);

const GlobeIcon = () => (
  <svg
    className="w-6 h-6"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"
    />
  </svg>
);

const LockIcon = () => (
  <svg
    className="w-6 h-6"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
    />
  </svg>
);

const ArrowRightIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M17 8l4 4m0 0l-4 4m4-4H3"
    />
  </svg>
);

// Stats component
function Stats() {
  const [stats, setStats] = useState({
    totalInferences: 0,
    verifiedProofs: 0,
    costSavings: 0,
    activeNodes: 0,
  });

  useEffect(() => {
    // Animate counter
    const targetStats = {
      totalInferences: 1247893,
      verifiedProofs: 1247890,
      costSavings: 73,
      activeNodes: 2847,
    };

    const duration = 2000;
    const steps = 60;
    const interval = duration / steps;

    let step = 0;
    const timer = setInterval(() => {
      step++;
      const progress = step / steps;
      setStats({
        totalInferences: Math.floor(targetStats.totalInferences * progress),
        verifiedProofs: Math.floor(targetStats.verifiedProofs * progress),
        costSavings: Math.floor(targetStats.costSavings * progress),
        activeNodes: Math.floor(targetStats.activeNodes * progress),
      });

      if (step >= steps) {
        clearInterval(timer);
        setStats(targetStats);
      }
    }, interval);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
      <div className="glass-card p-6 text-center">
        <div className="text-3xl md:text-4xl font-bold text-gradient">
          {stats.totalInferences.toLocaleString()}
        </div>
        <div className="text-sm text-[var(--foreground-muted)] mt-2">
          Total Inferences
        </div>
      </div>
      <div className="glass-card p-6 text-center">
        <div className="text-3xl md:text-4xl font-bold text-[var(--secondary-400)]">
          {stats.verifiedProofs.toLocaleString()}
        </div>
        <div className="text-sm text-[var(--foreground-muted)] mt-2">
          Verified Proofs
        </div>
      </div>
      <div className="glass-card p-6 text-center">
        <div className="text-3xl md:text-4xl font-bold text-[var(--accent-400)]">
          {stats.costSavings}%
        </div>
        <div className="text-sm text-[var(--foreground-muted)] mt-2">
          Cost Savings
        </div>
      </div>
      <div className="glass-card p-6 text-center">
        <div className="text-3xl md:text-4xl font-bold text-gradient">
          {stats.activeNodes.toLocaleString()}
        </div>
        <div className="text-sm text-[var(--foreground-muted)] mt-2">
          Active Nodes
        </div>
      </div>
    </div>
  );
}

// Feature Card Component
function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="glass-card p-6 hover-lift">
      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[var(--primary-500)] to-[var(--accent-500)] flex items-center justify-center text-white mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-[var(--foreground-muted)] text-sm">{description}</p>
    </div>
  );
}

// Navigation
function Navigation() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? "glass-card !rounded-none py-3" : "py-6"
        }`}
    >
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--primary-500)] to-[var(--accent-500)] flex items-center justify-center">
            <ShieldCheckIcon />
          </div>
          <span className="text-xl font-bold">V-Inference</span>
        </Link>

        <div className="hidden md:flex items-center gap-8">
          <a
            href="#features"
            className="text-[var(--foreground-muted)] hover:text-white transition-colors"
          >
            Features
          </a>
          <a
            href="#how-it-works"
            className="text-[var(--foreground-muted)] hover:text-white transition-colors"
          >
            How it Works
          </a>
          <a
            href="#pricing"
            className="text-[var(--foreground-muted)] hover:text-white transition-colors"
          >
            Pricing
          </a>
        </div>

        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="btn btn-primary">
            Launch App
            <ArrowRightIcon />
          </Link>
        </div>
      </div>
    </nav>
  );
}

// How It Works Section
function HowItWorks() {
  const steps = [
    {
      number: "01",
      title: "Upload Your Model",
      description:
        "Upload your ONNX, PyTorch, or TensorFlow model to the network. Your model weights remain encrypted and private.",
    },
    {
      number: "02",
      title: "Run Inference",
      description:
        "Submit inference requests with your data. Decentralized nodes process requests and generate ZK proofs.",
    },
    {
      number: "03",
      title: "Verify On-Chain",
      description:
        "Zero-Knowledge proofs are verified on Base L2. Payment is released only after cryptographic verification.",
    },
    {
      number: "04",
      title: "Trade & Earn",
      description:
        "List your models on the marketplace. Earn from every verified inference without exposing your model.",
    },
  ];

  return (
    <section id="how-it-works" className="py-24">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">How It Works</h2>
          <p className="text-[var(--foreground-muted)] max-w-2xl mx-auto">
            V-Inference combines decentralized compute with Zero-Knowledge
            proofs to create a trustless AI inference marketplace.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <div className="glass-card p-6 h-full">
                <div className="text-5xl font-bold text-gradient opacity-30 mb-4">
                  {step.number}
                </div>
                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                <p className="text-[var(--foreground-muted)] text-sm">
                  {step.description}
                </p>
              </div>
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-3 transform -translate-y-1/2 text-[var(--primary-500)]">
                  <ArrowRightIcon />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// Main Page Component
export default function Home() {
  return (
    <main className="min-h-screen">
      <Navigation />

      {/* Hero Section */}
      <section className="pt-32 pb-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto animate-fade-in">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--glass-bg)] border border-[var(--glass-border)] mb-8">
              <span className="w-2 h-2 rounded-full bg-[var(--secondary-500)] animate-pulse"></span>
              <span className="text-sm text-[var(--foreground-muted)]">
                Powered by ZKML on Base L2
              </span>
            </div>

            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
              Verifiable AI Inference
              <br />
              <span className="text-[var(--foreground)]">
                Without the Trust Tax
              </span>
            </h1>

            <p className="text-lg md:text-xl text-[var(--foreground-muted)] mb-10 max-w-2xl mx-auto">
              A decentralized AI inference network that uses Zero-Knowledge
              Proofs to ensure accurate computations at 60-80% lower cost than
              centralized cloud providers.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
              <Link href="/dashboard" className="btn btn-primary text-lg px-8 py-4">
                Start Building
                <ArrowRightIcon />
              </Link>
              <Link
                href="/dashboard/marketplace"
                className="btn btn-secondary text-lg px-8 py-4"
              >
                Explore Marketplace
              </Link>
            </div>

            <Stats />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-[var(--background-secondary)]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Why V-Inference?
            </h2>
            <p className="text-[var(--foreground-muted)] max-w-2xl mx-auto">
              We don&apos;t just provide decentralized compute. We provide a
              protocol for trust.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={<ShieldCheckIcon />}
              title="ZKML Verification"
              description="Every inference generates a SNARK proof using EZKL. Mathematically verify that providers ran your model correctly."
            />
            <FeatureCard
              icon={<CubeIcon />}
              title="Hardware Agnostic"
              description="From MacBooks to H100s, our lightweight Docker client lets any GPU join the network with a single command."
            />
            <FeatureCard
              icon={<BoltIcon />}
              title="Low Latency"
              description="Real-time job orchestrator pairs requests with optimal nodes based on hardware specs and geographic location."
            />
            <FeatureCard
              icon={<LockIcon />}
              title="Model Privacy"
              description="List models on the marketplace without exposing architecture or weights. Buyers use inference, not download models."
            />
            <FeatureCard
              icon={<ChartIcon />}
              title="Automated Escrow"
              description="Smart contracts hold funds until ZK proof verification passes. No payment without proof of correct execution."
            />
            <FeatureCard
              icon={<GlobeIcon />}
              title="Global Network"
              description="Access idle GPU capacity worldwide. Lower costs by leveraging distributed compute resources."
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <HowItWorks />

      {/* CTA Section */}
      <section className="py-24 bg-[var(--background-secondary)]">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <div className="glass-card p-12 relative overflow-hidden">
            {/* Decorative elements */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-[var(--primary-500)] opacity-10 rounded-full blur-3xl"></div>
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-[var(--accent-500)] opacity-10 rounded-full blur-3xl"></div>

            <h2 className="text-3xl md:text-4xl font-bold mb-4 relative z-10">
              Ready to Build on Verifiable AI?
            </h2>
            <p className="text-[var(--foreground-muted)] mb-8 max-w-xl mx-auto relative z-10">
              Join the network of developers and enterprises using V-Inference
              for trustless, cost-effective AI inference.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 relative z-10">
              <Link href="/dashboard" className="btn btn-primary text-lg px-8 py-4">
                Launch Dashboard
                <ArrowRightIcon />
              </Link>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-secondary text-lg px-8 py-4"
              >
                View Documentation
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-[var(--glass-border)]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--primary-500)] to-[var(--accent-500)] flex items-center justify-center">
                <ShieldCheckIcon />
              </div>
              <span className="font-semibold">V-Inference</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-[var(--foreground-muted)]">
              <a href="#" className="hover:text-white transition-colors">
                Documentation
              </a>
              <a href="#" className="hover:text-white transition-colors">
                GitHub
              </a>
              <a href="#" className="hover:text-white transition-colors">
                Discord
              </a>
              <a href="#" className="hover:text-white transition-colors">
                Twitter
              </a>
            </div>
            <div className="text-sm text-[var(--foreground-muted)]">
              © 2024 V-Inference. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}
