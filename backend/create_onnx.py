"""
Create ONNX model for EZKL SNARK proofs
"""
import numpy as np
from sklearn.linear_model import LogisticRegression
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import json
import os

print('Creating ONNX model...')

# Create simple classifier
np.random.seed(42)
X = np.random.randn(100, 4).astype(np.float32)
y = np.random.randint(0, 3, 100)

model = LogisticRegression(max_iter=200)
model.fit(X, y)
print('Model trained')

# Convert to ONNX
initial_type = [('input', FloatTensorType([None, 4]))]
onnx_model = convert_sklearn(model, initial_types=initial_type)
print('Converted to ONNX')

# Save
onnx_path = 'storage/models/zkml_classifier.onnx'
with open(onnx_path, 'wb') as f:
    f.write(onnx_model.SerializeToString())
print(f'Saved: {onnx_path}')

# Add to database
with open('storage/models.json', 'r') as f:
    models = json.load(f)

models = [m for m in models if m.get('id') != 'model-onnx-zkml']

new_model = {
    'id': 'model-onnx-zkml',
    'name': '[ZKML] ONNX Classifier (REAL SNARK)',
    'description': 'ONNX model with REAL EZKL SNARK proof generation!',
    'model_type': 'classification',
    'is_public': True,
    'owner_id': 'demo-user',
    'file_path': 'storage/models/zkml_classifier.onnx',
    'metadata': {
        'format': 'onnx',
        'ezkl_enabled': True,
        'real_zkml': True,
        'input_size': 4,
        'classes': ['Class 0', 'Class 1', 'Class 2']
    },
    'total_inferences': 0,
    'average_latency_ms': 0,
    'created_at': '2026-01-08T12:00:00Z'
}
models.append(new_model)

with open('storage/models.json', 'w') as f:
    json.dump(models, f, indent=2)

print('Done!')
