"""
Create an ONNX model for EZKL SNARK proof generation
This creates a simple neural network in PyTorch and exports to ONNX
"""
import os
import json
import numpy as np

# Check for required libraries
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    print("PyTorch not installed. Installing...")
    os.system("pip install torch --index-url https://download.pytorch.org/whl/cpu")
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True

print("Creating ONNX model for EZKL...")

# Simple neural network for classification
class SimpleClassifier(nn.Module):
    def __init__(self, input_size=4, hidden_size=8, output_size=3):
        super(SimpleClassifier, self).__init__()
        self.layer1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        x = self.layer1(x)
        x = self.relu(x)
        x = self.layer2(x)
        return x

# Create model
model = SimpleClassifier(input_size=4, hidden_size=8, output_size=3)

# Train with random data (just to have weights)
torch.manual_seed(42)
X_train = torch.randn(100, 4)
y_train = torch.randint(0, 3, (100,))

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

for epoch in range(100):
    optimizer.zero_grad()
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()

print(f"Training complete. Final loss: {loss.item():.4f}")

# Export to ONNX
model.eval()
dummy_input = torch.randn(1, 4)
onnx_path = "storage/models/simple_classifier.onnx"

torch.onnx.export(
    model,
    dummy_input,
    onnx_path,
    export_params=True,
    opset_version=11,
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
)

print(f"ONNX model saved to: {onnx_path}")

# Test prediction
with torch.no_grad():
    test_input = torch.tensor([[5.1, 3.5, 1.4, 0.2]])  # Iris-like input
    output = model(test_input)
    pred = torch.argmax(output, dim=1).item()
    print(f"Test prediction: class {pred}")

# Add to database
with open('storage/models.json', 'r') as f:
    models = json.load(f)

# Remove old if exists
models = [m for m in models if m.get('id') != 'model-onnx-zkml']

new_model = {
    'id': 'model-onnx-zkml',
    'name': '[ZKML] Simple Classifier (REAL SNARK)',
    'description': 'ONNX neural network with REAL EZKL SNARK proof generation. This model generates actual ZK proofs!',
    'model_type': 'classification',
    'is_public': True,
    'owner_id': 'demo-user',
    'file_path': 'storage/models/simple_classifier.onnx',
    'metadata': {
        'format': 'onnx',
        'ezkl_enabled': True,
        'real_zkml': True,
        'input_size': 4,
        'output_size': 3,
        'classes': ['Class 0', 'Class 1', 'Class 2']
    },
    'total_inferences': 0,
    'average_latency_ms': 0,
    'created_at': '2026-01-08T12:00:00Z'
}
models.append(new_model)

with open('storage/models.json', 'w') as f:
    json.dump(models, f, indent=2)

print("Added ONNX model to database!")
print("\n✅ ONNX model ready for EZKL SNARK proofs!")
