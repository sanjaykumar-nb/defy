# V-Inference: Decentralized AI Inference Network

A decentralized AI inference network that uses Zero-Knowledge Proofs (ZKML) to ensure accurate computations at a lower cost than centralized cloud providers.

![V-Inference](https://img.shields.io/badge/V--Inference-DePIN-6366f1?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge)

## 🚀 Overview

V-Inference creates a marketplace where Zero-Knowledge Proofs serve as a "receipt" for correct AI inference execution. Users can:

- **Upload AI Models**: Store and manage ONNX, PyTorch, or TensorFlow models
- **Run Verified Inference**: Execute inference with ZKML proof generation
- **Trade on Marketplace**: Sell inference access while keeping model architecture private
- **Escrow Protection**: Payments released only after cryptographic proof verification

## ✨ Features

### ZKML Verification Layer
Automatically generates SNARK proofs for each inference using simulated EZKL. This ensures providers can't skip layers or falsify outputs.

### Model Privacy
List models on the marketplace without exposing architecture or weights. Buyers can only use inference, not download models.

### Automated Escrow
Smart contract simulation holds funds until ZK proof verification passes. No payment without proof of correct execution.

### Premium UI
Modern glassmorphism design with dark mode, animations, and responsive layout.

## 🛠 Tech Stack

### Frontend
- **Next.js 14** (App Router)
- **Tailwind CSS** with custom design system
- **TypeScript** for type safety

### Backend
- **FastAPI** (Python) for orchestration
- **JSON file storage** (simulating Supabase)
- **ZKML Simulator** for proof generation

### Blockchain (Simulated)
- **Base Sepolia** L2 for verification
- **Escrow contracts** for payment handling

## 📁 Project Structure

```
V-inference/
├── frontend/                 # Next.js 14 App
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Landing page
│   │   │   └── dashboard/
│   │   │       ├── page.tsx       # Dashboard overview
│   │   │       ├── models/        # Model management
│   │   │       ├── inference/     # Run inference
│   │   │       └── marketplace/   # Buy/sell inference
│   │   └── lib/
│   │       └── api.ts             # API client
│   └── package.json
│
├── backend/                  # FastAPI Server
│   ├── app/
│   │   ├── api/
│   │   │   ├── models.py          # Model endpoints
│   │   │   ├── inference.py       # Inference endpoints
│   │   │   ├── marketplace.py     # Marketplace endpoints
│   │   │   └── users.py           # User endpoints
│   │   ├── core/
│   │   │   └── database.py        # JSON storage
│   │   └── services/
│   │       └── zkml_simulator.py  # ZKML proof simulation
│   ├── main.py
│   └── requirements.txt
│
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend API will be available at `http://localhost:8000`

## 📖 Usage

### 1. Upload a Model

1. Navigate to Dashboard → My Models
2. Click "Upload Model"
3. Drag & drop your model file (ONNX, PyTorch, etc.)
4. Fill in name, description, and type
5. Click Upload

### 2. Run Inference

1. Navigate to Dashboard → Inference
2. Select a model
3. Enter or load sample JSON input
4. Toggle ZKML verification (recommended)
5. Click "Run Inference"
6. View results with ZK proof

### 3. Marketplace

#### List a Model
1. Go to My Models
2. Click the marketplace icon on a model
3. Set price per inference
4. Submit listing

#### Purchase Inference
1. Go to Marketplace
2. Browse listings
3. Click "Purchase" on desired model
4. Select number of inferences
5. Confirm (funds go to escrow)
6. Use purchased credits for inference

## 🔒 Security Model

### Model Privacy
- Model weights are never exposed to buyers
- Only inference input/output is visible
- Architecture details remain hidden

### ZKML Verification
- Every inference generates a ZK-SNARK proof
- Proofs are verified before payment release
- Tampered outputs are mathematically detectable

### Escrow System
- Funds locked on purchase
- Released after proof verification
- Automatic refund on verification failure

## 🎨 Design System

### Colors
- **Primary**: Indigo (#6366f1) - Trust & Technology
- **Secondary**: Emerald (#10b981) - Verification & Success
- **Accent**: Violet (#8b5cf6) - AI & Innovation

### Components
- Glassmorphism cards with backdrop blur
- Gradient buttons with hover animations
- Real-time status indicators

## 📡 API Endpoints

### Users
- `POST /api/users/connect` - Connect wallet
- `GET /api/users/{id}/dashboard` - Get dashboard data

### Models
- `POST /api/models/upload` - Upload model
- `GET /api/models/` - List models
- `DELETE /api/models/{id}` - Delete model

### Inference
- `POST /api/inference/run` - Run inference
- `GET /api/inference/job/{id}` - Get job status
- `POST /api/inference/verify-proof/{id}` - Verify proof

### Marketplace
- `POST /api/marketplace/list` - Create listing
- `GET /api/marketplace/listings` - Get listings
- `POST /api/marketplace/purchase` - Purchase inference

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📄 License

MIT License - see LICENSE file for details.

---

Built with ❤️ by the V-Inference Team
