import json
import os

# Read existing models
with open('storage/models.json', 'r') as f:
    models = json.load(f)

# PKL files in storage/models
pkl_files = {
    'Fraud_detect.pkl': {'name': 'Fraud Detection Model', 'type': 'classification', 'features': 30},
    'churn_model_xgb.pkl': {'name': 'Customer Churn Predictor', 'type': 'classification', 'features': 20},
    'creditcard_model.pkl': {'name': 'Credit Card Fraud Detector', 'type': 'classification', 'features': 28},
    'home_price_predictor.pkl': {'name': 'Home Price Predictor', 'type': 'regression', 'features': 13},
    'resume_classifier_model.pkl': {'name': 'Resume Classifier', 'type': 'classification', 'features': 1000},
}

# Check which are already linked
linked = set()
for m in models:
    fp = m.get('file_path', '')
    if fp:
        linked.add(fp.split('/')[-1])

added = 0
for filename, info in pkl_files.items():
    if filename not in linked:
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

with open('storage/models.json', 'w') as f:
    json.dump(models, f, indent=2)

print(f'Total new models added: {added}')
