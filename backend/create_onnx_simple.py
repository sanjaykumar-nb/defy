"""
Create a simple ONNX model for EZKL using onnx.helper
No PyTorch or skl2onnx needed!
"""
import numpy as np
import onnx
from onnx import helper, TensorProto
import json

print("Creating simple ONNX model for EZKL...")

# Create a simple linear model: y = Wx + b
# Input: 4 features, Output: 3 classes (like Iris)

# Random weights
np.random.seed(42)
W = np.random.randn(4, 3).astype(np.float32)
b = np.random.randn(3).astype(np.float32)

# Create weight initializers
W_init = helper.make_tensor('W', TensorProto.FLOAT, [4, 3], W.flatten().tolist())
b_init = helper.make_tensor('b', TensorProto.FLOAT, [3], b.flatten().tolist())

# Create nodes
# MatMul: input @ W
matmul_node = helper.make_node('MatMul', ['input', 'W'], ['matmul_out'])
# Add bias
add_node = helper.make_node('Add', ['matmul_out', 'b'], ['output'])

# Create graph
input_tensor = helper.make_tensor_value_info('input', TensorProto.FLOAT, [1, 4])
output_tensor = helper.make_tensor_value_info('output', TensorProto.FLOAT, [1, 3])

graph = helper.make_graph(
    [matmul_node, add_node],
    'simple_classifier',
    [input_tensor],
    [output_tensor],
    [W_init, b_init]
)

# Create model
model = helper.make_model(graph, opset_imports=[helper.make_opsetid('', 11)])
model.ir_version = 7

# Check model
onnx.checker.check_model(model)
print("Model validation passed!")

# Save
onnx_path = 'storage/models/zkml_simple.onnx'
onnx.save(model, onnx_path)
print(f"Saved: {onnx_path}")

# Test with onnxruntime
import onnxruntime as ort
session = ort.InferenceSession(onnx_path)
test_input = np.array([[5.1, 3.5, 1.4, 0.2]], dtype=np.float32)
result = session.run(None, {'input': test_input})
print(f"Test output: {result[0]}")
print(f"Predicted class: {np.argmax(result[0])}")

# Add to database
with open('storage/models.json', 'r') as f:
    models = json.load(f)

models = [m for m in models if m.get('id') != 'model-onnx-zkml']

new_model = {
    'id': 'model-onnx-zkml',
    'name': '[ZKML] ONNX Model (REAL SNARK)',
    'description': 'ONNX model with REAL EZKL SNARK proof generation! Uses ZK circuits for verifiable inference.',
    'model_type': 'classification',
    'is_public': True,
    'owner_id': 'demo-user',
    'file_path': 'storage/models/zkml_simple.onnx',
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

print("\nDone! ONNX model ready for EZKL SNARK proofs!")
