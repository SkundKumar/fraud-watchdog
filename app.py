import os, subprocess, joblib, numpy as np, pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)
CORS(app)

# CONFIGURATION
MODEL_PATH = 'backend/model/fraud_v2.pkl'
DATA_STORE = 'backend/data/training_buffer.csv'
mlops_stats = {"version": 1.0, "maturity": 45, "threats_caught": 0}

# ENSURE DATA FOLDERS EXIST
os.makedirs('backend/data', exist_ok=True)

def initialize_buffer():
    """Creates a baseline dataset so the AI doesn't forget 'Safe' patterns."""
    if not os.path.exists(DATA_STORE):
        # Generate 200 safe baseline examples
        baseline = []
        for _ in range(200):
            row = [np.random.normal(0, 1.2) for _ in range(30)]
            baseline.append(row + [0]) # Label 0 = Safe
        
        cols = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount', 'Label']
        pd.DataFrame(baseline, columns=cols).to_csv(DATA_STORE, index=False)

initialize_buffer()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        model = joblib.load(MODEL_PATH)
        col_names = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
        
        # Mapping Features
        features = [0.0] * 30 
        features[0], features[1], features[2], features[29] = float(data['Time'])/1000, float(data['V1']), float(data['V2']), float(data['Amount'])
        for i in range(3, 29): features[i] = np.random.normal(0, 1.2)
            
        df = pd.DataFrame([features], columns=col_names)
        proba = model.predict_proba(df)[0][1]
        
        # Decision Logic
        status = "Safe"
        if proba > 0.55: status, mlops_stats["threats_caught"] = "FRAUD", mlops_stats["threats_caught"] + 1
        elif 0.20 <= proba <= 0.55: status = "REQUIRES_HUMAN_REVIEW"
        
        # Save temporary state for the next retraining trigger
        with open('backend/data/last_features.npy', 'wb') as f: np.save(f, np.array(features))
        
        return jsonify({'id': f"TXN-{int(datetime.now().timestamp())}", 'status': status, 'probability': str(round(proba, 4)), 'amount': str(data['Amount']), 'stats': mlops_stats})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/trigger-mlops', methods=['POST'])
def trigger_mlops():
    try:
        # 1. LOAD LAST THREAT
        features = np.load('backend/data/last_features.npy').tolist()
        
        # 2. APPEND TO DATA LAKE (Permanent Memory)
        df_buffer = pd.read_csv(DATA_STORE)
        new_row = features + [1] # Label 1 = Fraud
        df_buffer.loc[len(df_buffer)] = new_row
        df_buffer.to_csv(DATA_STORE, index=False)
        
        # 3. ON-THE-FLY RETRAINING
        # We retrain on the WHOLE buffer (Safe Baseline + New Fraud)
        X = df_buffer.drop('Label', axis=1)
        y = df_buffer['Label']
        
        # Use a faster, lighter Forest for on-the-fly updates
        new_model = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42)
        new_model.fit(X, y)
        joblib.dump(new_model, MODEL_PATH)
        
        # 4. MLOPS SYNC
        mlops_stats["maturity"] = min(99, int((len(df_buffer[df_buffer['Label']==1]) / 50) * 100) + 45)
        mlops_stats["version"] = round(mlops_stats["version"] + 0.1, 1)
        
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', f"MLOps: On-the-fly retraining v{mlops_stats['version']}"], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        return jsonify({"status": "success", "message": "Brain Updated with Data Lake!", "stats": mlops_stats})
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)