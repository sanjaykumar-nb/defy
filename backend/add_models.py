import json
import os

# Create/Clear models.json
models = []

# Actual files in storage/models
pkl_files = {
    'fraud_detection_v2.pkl': {'name': 'Fraud Detection Model', 'type': 'classification', 'features': 30},
    'churn_predictor_v2.pkl': {'name': 'Customer Churn Predictor', 'type': 'classification', 'features': 20},
    'creditcard_v2.pkl': {'name': 'Credit Card Fraud Detector', 'type': 'classification', 'features': 28},
    'home_price_v2.pkl': {'name': 'Home Price Predictor', 'type': 'regression', 'features': 13},
    'resume_classifier_v2.pkl': {'name': 'Resume Classifier', 'type': 'classification', 'features': 50},
    'sentiment_v2.pkl': {'name': 'Sentiment Classifier', 'type': 'classification', 'features': 100},
    'iris_compatible.pkl': {'name': 'Iris Classifier', 'type': 'classification', 'features': 4},
}

onnx_files = {
    'mnist.onnx': {'name': 'MNIST Digit Classifier', 'type': 'classification', 'features': 784},
    'simple_zkml.onnx': {'name': 'ZKML Circuit Model', 'type': 'classification', 'features': 4},
}

added = 0
for filename, info in pkl_files.items():
    model_id = 'model-' + filename.replace('.pkl', '').replace('_', '-')
    new_model = {
        'id': model_id,
        'name': info['name'],
        'description': f"{info['name']} - Machine Learning model",
        'model_type': info['type'],
        'is_public': True,
        'owner_id': 'demo-user',
        'file_path': f'storage/models/{filename}',
        'metadata': {'features': info['features'], 'file': filename},
        'total_inferences': 0,
        'average_latency_ms': 0,
        'created_at': '2026-01-08T00:00:00Z'
    }
    models.append(new_model)
    added += 1
    print(f'Added: {info["name"]}')

for filename, info in onnx_files.items():
    model_id = 'model-' + filename.replace('.onnx', '').replace('_', '-')
    new_model = {
        'id': model_id,
        'name': info['name'],
        'description': f"{info['name']} - ONNX model",
        'model_type': info['type'],
        'is_public': True,
        'owner_id': 'demo-user',
        'file_path': f'storage/models/{filename}',
        'metadata': {'features': info['features'], 'file': filename},
        'total_inferences': 0,
        'average_latency_ms': 0,
        'created_at': '2026-01-08T00:00:00Z'
    }
    models.append(new_model)
    added += 1
    print(f'Added: {info["name"]}')

with open('storage/models.json', 'w') as f:
    json.dump(models, f, indent=2)

print(f'Total new models added: {added}')
