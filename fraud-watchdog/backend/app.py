import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import os
import csv
from datetime import datetime
import subprocess

# --- 1. GLOBAL STORAGE FOR DASHBOARD ---
recent_predictions = []

# --- 2. LOAD MODEL ---
# Checks for V2 first, falls back to V1 if retraining hasn't happened
MODEL_PATH = 'backend/model/fraud_v2.pkl'
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = 'backend/model/fraud_v1.pkl'

print(f"🚀 Loading model: {MODEL_PATH}")
model = joblib.load(MODEL_PATH)

# --- 3. DEFINE APP & CORS ---
app = FastAPI(title="Financial Fraud Watchdog")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Transaction(BaseModel):
    features: list[float] 

@app.get("/")
def read_root():
    return {"message": "Fraud Watchdog API is Awake 🐕"}

@app.get("/live-feed")
def get_live_feed():
    # Returns the last 20 transactions to the React Frontend
    return recent_predictions

@app.post("/retrain")
def trigger_retrain():
    # This allows the Frontend button to run your retrain.py script
    try:
        subprocess.Popen(["python", "backend/retrain.py"])
        return {"status": "Retraining Started"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

@app.post("/predict")
def predict_fraud(transaction: Transaction):
    # Prepare data for model
    columns = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
    df = pd.DataFrame([transaction.features], columns=columns)
    
    # Run Prediction
    prediction = int(model.predict(df)[0])
    probs = model.predict_proba(df)[0] 
    confidence = max(probs)
    
    # MLOps Logic
    status = "HIGH_CONFIDENCE"
    if confidence < 0.75:
        status = "UNCERTAIN_GREY_ZONE"

    result = {
        "id": datetime.now().strftime("%H%M%S%f")[-6:],
        "prediction": "FRAUD" if prediction == 1 else "LEGIT",
        "confidence_score": round(confidence, 4),
        "mlops_status": status,
        "amount": transaction.features[-1],
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }

    # Store for Frontend
    recent_predictions.append(result)
    if len(recent_predictions) > 20:
        recent_predictions.pop(0)

    return result

handler = Mangum(app)