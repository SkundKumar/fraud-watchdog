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

# Temporary storage for the last "Approved" threat to use for training
last_threat_pattern = None

@app.route('/predict', methods=['POST'])
def predict():
    try:
        global last_threat_pattern
        data = request.json
        model = joblib.load(MODEL_PATH)
        
        # Prepare 30 features
        col_names = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
        features = [0.0] * 30 
        features[0], features[1], features[2], features[29] = float(data['Time'])/1000, float(data['V1']), float(data['V2']), float(data['Amount'])
        for i in range(3, 29): features[i] = np.random.normal(0, 1.5)
            
        df = pd.DataFrame([features], columns=col_names)
        
        # Save this pattern in case the user approves it as fraud
        last_threat_pattern = features 
        
        proba = model.predict_proba(df)[0][1]
        
        status = "Safe"
        if proba > 0.45: 
            status = "FRAUD"
            mlops_stats["threats_caught"] += 1
        elif 0.15 <= proba <= 0.45: 
            status = "REQUIRES_HUMAN_REVIEW"
        
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

        print("🧠 [AI] Starting Real-Time Model Retraining...")
        
        # 1. ACTUAL MACHINE LEARNING: Micro-Retraining
        # We create a small training set: some 'Safe' noise and the 'New Fraud'
        X_new = []
        y_new = []
        
        # Add 20 examples of the NEW Fraud pattern (Velocity Attack)
        for _ in range(20):
            # Add slight jitter so the AI learns the *area*, not just one number
            jittered = [f + np.random.normal(0, 0.05) for f in last_threat_pattern]
            X_new.append(jittered)
            y_new.append(1) # Label as FRAUD
            
        # Add 20 examples of 'Safe' noise so the model stays balanced
        for _ in range(20):
            X_new.append([np.random.normal(0, 1) for _ in range(30)])
            y_new.append(0) # Label as SAFE

        # Load, Retrain, and Save the .pkl file
        model = joblib.load(MODEL_PATH)
        model.fit(X_new, y_new) 
        joblib.dump(model, MODEL_PATH)
        
        # Update MLOps Stats
        mlops_stats["maturity"] = min(99, mlops_stats["maturity"] + 12)
        mlops_stats["version"] = round(mlops_stats["version"] + 0.1, 1)
        
        # 2. GIT SYNC (Pushes the actual updated .pkl file!)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', f"MLOps: Model Retrained on New Threat v{mlops_stats['version']}"], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        return jsonify({"status": "success", "message": "AI Brain Updated!", "stats": mlops_stats})
    except Exception as e:
        print(f"❌ Retraining Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)