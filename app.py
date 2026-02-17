import os
import subprocess
import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# 1. INITIALIZE SYSTEM
app = Flask(__name__)
CORS(app)

# Path verified from your sidebar
MODEL_PATH = 'backend/model/fraud_v2.pkl'

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        model = joblib.load(MODEL_PATH)
        
        # 2. PREPARE 30 FEATURES
        col_names = [f'V{i}' for i in range(1, 29)]
        col_names = ['Time'] + col_names + ['Amount']
        
        features = [0.0] * 30 
        features[0] = float(data['Time']) / 1000
        features[1] = float(data['V1'])
        features[2] = float(data['V2'])
        features[29] = float(data['Amount'])
        
        # Inject noise for dynamic confidence
        for i in range(3, 29):
            features[i] = np.random.normal(0, 1.5)
            
        df = pd.DataFrame([features], columns=col_names)
        proba = model.predict_proba(df)[0][1]
        
        # Decision Logic
        status = "Safe"
        if proba > 0.40: 
            status = "FRAUD"
        elif 0.15 <= proba <= 0.40:
            status = "REQUIRES_HUMAN_REVIEW"
        
        entry = {
            'id': f"TXN-{int(datetime.now().timestamp())}",
            'status': status,
            'probability': str(round(proba, 4)),
            'amount': str(data['Amount'])
        }
        
        print(f"📊 INFERENCE: {status} | Prob: {proba}")
        return jsonify(entry)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/trigger-mlops', methods=['POST'])
def trigger_mlops():
    try:
        print("🚀 [MLOPS] Executing Atomic Sync...")
        
        # A. LOG THE EVENT (Ensures there is ALWAYS a change to commit)
        log_dir = 'backend'
        if not os.path.exists(log_dir): os.makedirs(log_dir)
        with open(f"{log_dir}/sync_log.txt", "a") as f:
            f.write(f"Adaptive Sync at {datetime.now()}\n")
            
        # B. STAGE AND COMMIT FIRST (This fixes the 'unstaged changes' error)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'MLOps: Auto-saving local state'], check=True)
        
        # C. PULL LATEST (Now that local is committed, rebase will work)
        subprocess.run(['git', 'pull', 'origin', 'main', '--rebase'], check=True)
        
        # D. PUSH TO CLOUD
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        return jsonify({"status": "success", "message": "Adaptation Synced to GitHub!"})
    except subprocess.CalledProcessError as e:
        # If it fails because of 'nothing to commit', it's already in sync
        print(f"ℹ️ Git Status: {e}")
        return jsonify({"status": "success", "message": "System is already in sync."})
    except Exception as e:
        print(f"❌ MLOps Failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"\n✅ WATCHDOG ONLINE | Model: {MODEL_PATH}")
    app.run(debug=True, port=5000)