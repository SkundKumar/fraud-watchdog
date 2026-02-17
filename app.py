import os
import subprocess
import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)
CORS(app)

MODEL_PATH = 'backend/model/fraud_v2.pkl'
mlops_stats = {"version": 1.0, "maturity": 45, "threats_caught": 0}

# Global buffer to store patterns for retraining
last_threat_pattern = None

@app.route('/predict', methods=['POST'])
def predict():
    try:
        global last_threat_pattern
        data = request.json
        model = joblib.load(MODEL_PATH)
        
        # 1. Feature Names setup to match the model
        col_names = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
        features = [0.0] * 30 
        features[0], features[1], features[2], features[29] = float(data['Time'])/1000, float(data['V1']), float(data['V2']), float(data['Amount'])
        
        # Use Gaussian Noise for V3-V28
        for i in range(3, 29): features[i] = np.random.normal(0, 1.2)
            
        # Convert to DataFrame with names to STOP THE PINK WARNINGS
        df = pd.DataFrame([features], columns=col_names)
        last_threat_pattern = features 
        
        # 2. AI Inference
        proba = model.predict_proba(df)[0][1]
        
        # Decision Logic
        status = "Safe"
        if proba > 0.55: # Slightly raised threshold for less "paranoia"
            status = "FRAUD"
            mlops_stats["threats_caught"] += 1
        elif 0.20 <= proba <= 0.55: 
            status = "REQUIRES_HUMAN_REVIEW"
        
        print(f"📊 INFERENCE: {status} | Prob: {proba}")
        return jsonify({
            'id': f"TXN-{int(datetime.now().timestamp())}",
            'status': status,
            'probability': str(round(proba, 4)),
            'amount': str(data['Amount']),
            'stats': mlops_stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/trigger-mlops', methods=['POST'])
def trigger_mlops():
    try:
        global last_threat_pattern
        if last_threat_pattern is None:
            return jsonify({"error": "No pattern to learn"}), 400

        print("🧠 [AI] Stabilizing Brain with Baseline Retraining...")
        
        # 3. BALANCED RETRAINING
        # To prevent the 'flag everything' bug, we need a large 'Safe' baseline
        X_train = []
        y_train = []
        col_names = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
        
        # Add 30 examples of the Fraudulent Pattern
        for _ in range(30):
            X_train.append([f + np.random.normal(0, 0.02) for f in last_threat_pattern])
            y_train.append(1) 
            
        # Add 200 examples of 'Safe' data to maintain balance
        for _ in range(200):
            safe_sample = [np.random.normal(0, 1.5) for _ in range(30)]
            X_train.append(safe_sample)
            y_train.append(0)

        # Convert to DataFrame BEFORE fitting to bake feature names into the model
        df_train = pd.DataFrame(X_train, columns=col_names)
        
        # Create a fresh model and fit (prevents additive weight corruption)
        model = RandomForestClassifier(n_estimators=100, max_depth=10)
        model.fit(df_train, y_train) 
        joblib.dump(model, MODEL_PATH)
        
        mlops_stats["maturity"] = min(99, mlops_stats["maturity"] + 10)
        mlops_stats["version"] = round(mlops_stats["version"] + 0.1, 1)
        
        # 4. Atomic Git Sync
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', f"MLOps: Model Balanced & Retrained v{mlops_stats['version']}"], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        return jsonify({"status": "success", "message": "AI Brain Stabilized!", "stats": mlops_stats})
    except Exception as e:
        print(f"❌ Retraining Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)