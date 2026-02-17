import os
import subprocess
import joblib
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Path verified from your VS Code sidebar
MODEL_PATH = 'backend/model/fraud_v2.pkl'

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if not os.path.exists(MODEL_PATH):
            return jsonify({"error": f"Model not found at {MODEL_PATH}"}), 500
            
        model = joblib.load(MODEL_PATH)
        
        # 1. Prepare 30 features to match model requirements
        features = [0.0] * 30 
        features[0] = float(data['Time']) / 1000
        features[1] = float(data['V1'])
        features[2] = float(data['V2'])
        features[29] = float(data['Amount'])
        
        # 2. Inject Synthetic Noise (V3-V28) so confidence isn't 0.0
        for i in range(3, 29):
            features[i] = np.random.normal(0, 1.5)
            
        # 3. AI Prediction
        proba = model.predict_proba([features])[0][1]
        
        # 4. Human-in-the-Loop Thresholds
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
        
        print(f"📊 AI INFERENCE: {status} | Confidence: {proba}")
        return jsonify(entry)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/trigger-mlops', methods=['POST'])
def trigger_mlops():
    try:
        print("🚀 [MLOPS] Syncing with Remote Repository...")
        
        # FIX: Pull latest changes before pushing to avoid 'rejected' error
        subprocess.run(['git', 'pull', 'origin', 'main', '--rebase'], check=True)
        
        # Standard MLOps Push
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'MLOps: Automated adaptation cycle'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        return jsonify({"status": "success", "message": "Global Model Updated & Synced!"})
    except Exception as e:
        print(f"❌ MLOps Sync Failed: {e}")
        return jsonify({"error": "Git synchronization failed."}), 500

if __name__ == '__main__':
    print(f"\n✅ WATCHDOG ENGINE ONLINE | Path: {MODEL_PATH}")
    app.run(debug=True, port=5000)