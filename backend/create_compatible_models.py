"""
Create compatible demo models for V-Inference
These models are trained with the current sklearn version and will load correctly
"""
import os
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib

# Create storage directory
os.makedirs('storage/models', exist_ok=True)

models_created = []

# 1. Fraud Detection Model (Binary Classification)
print("Creating Fraud Detection Model...")
np.random.seed(42)
X_fraud = np.random.randn(1000, 30)  # 30 features like credit card dataset
y_fraud = (np.random.rand(1000) > 0.5).astype(int)  # 0 or 1
fraud_model = RandomForestClassifier(n_estimators=50, random_state=42)
fraud_model.fit(X_fraud, y_fraud)
joblib.dump(fraud_model, 'storage/models/fraud_detection_v2.pkl')
models_created.append(('fraud_detection_v2.pkl', 'Fraud Detection v2', 'classification'))
print("  ✅ Created")

# 2. Customer Churn Model (Binary Classification)
print("Creating Customer Churn Model...")
X_churn = np.random.randn(1000, 20)
y_churn = (np.random.rand(1000) > 0.5).astype(int)
churn_model = RandomForestClassifier(n_estimators=50, random_state=42)
churn_model.fit(X_churn, y_churn)
joblib.dump(churn_model, 'storage/models/churn_predictor_v2.pkl')
models_created.append(('churn_predictor_v2.pkl', 'Customer Churn v2', 'classification'))
print("  ✅ Created")

# 3. Credit Card Fraud (Binary Classification)
print("Creating Credit Card Fraud Model...")
X_cc = np.random.randn(1000, 28)
y_cc = (np.random.rand(1000) > 0.5).astype(int)
cc_model = LogisticRegression(random_state=42)
cc_model.fit(X_cc, y_cc)
joblib.dump(cc_model, 'storage/models/creditcard_v2.pkl')
models_created.append(('creditcard_v2.pkl', 'Credit Card Fraud v2', 'classification'))
print("  ✅ Created")

# 4. Home Price Predictor (Regression)
print("Creating Home Price Model...")
X_home = np.random.randn(1000, 13)  # Like Boston housing
y_home = np.random.rand(1000) * 500000 + 100000  # Price range 100k-600k
home_model = RandomForestRegressor(n_estimators=50, random_state=42)
home_model.fit(X_home, y_home)
joblib.dump(home_model, 'storage/models/home_price_v2.pkl')
models_created.append(('home_price_v2.pkl', 'Home Price Predictor v2', 'regression'))
print("  ✅ Created")

# 5. Sentiment Classifier (Multi-class)
print("Creating Sentiment Model...")
X_sent = np.random.randn(1000, 100)
y_sent = np.random.randint(0, 3, 1000)  # 0=negative, 1=neutral, 2=positive
sent_model = RandomForestClassifier(n_estimators=50, random_state=42)
sent_model.fit(X_sent, y_sent)
joblib.dump(sent_model, 'storage/models/sentiment_v2.pkl')
models_created.append(('sentiment_v2.pkl', 'Sentiment Classifier v2', 'classification'))
print("  ✅ Created")

print(f"\n✅ Created {len(models_created)} compatible models!")

# Now add them to the database
import json
with open('storage/models.json', 'r') as f:
    models = json.load(f)

# Remove old entries for v2 models if they exist
models = [m for m in models if not m.get('name', '').endswith(' v2')]

# Add new models
for filename, name, model_type in models_created:
    model_id = f"model-{filename.replace('.pkl', '').replace('_', '-')}"
    new_model = {
        'id': model_id,
        'name': name,
        'description': f'{name} - Compatible with current sklearn version',
        'model_type': model_type,
        'is_public': True,
        'owner_id': 'demo-user',
        'file_path': f'storage/models/{filename}',
        'metadata': {
            'sklearn_version': '1.4.2',
            'compatible': True
        },
        'total_inferences': 0,
        'average_latency_ms': 0,
        'created_at': '2026-01-08T12:00:00Z'
    }
    models.append(new_model)
    print(f"Added to DB: {name}")

with open('storage/models.json', 'w') as f:
    json.dump(models, f, indent=2)

print("\n🎉 All models ready! Restart backend to use them.")
