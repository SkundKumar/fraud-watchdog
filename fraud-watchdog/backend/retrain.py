import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
import joblib
import os
import random

# --- CONFIGURATION ---
ORIGINAL_DATA_PATH = 'data/creditcard.csv'
FLAGGED_DATA_PATH = 'data/flagged_transactions.csv'
MODEL_V2_PATH = 'backend/model/fraud_v2.pkl'

def generate_synthetic_chaos_data(n_samples=5000):
    """
    Generates synthetic data that MATCHES the 'Nuclear' simulate.py exactly.
    """
    print(f"   ⚡ GENERATING {n_samples} SYNTHETIC SAMPLES (MATCHING SIMULATION)...")
    
    data = []
    
    for _ in range(n_samples):
        # 1. Base: Random normal noise
        features = [random.gauss(0, 1) for _ in range(28)]
        
        # 2. Inject the EXACT Nuclear patterns
        # These MUST match simulate.py values
        amount_val = 50000.0        # MATCHES SIMULATE (50k)
        features[0] = -50.0         # MATCHES SIMULATE (-50)
        features[10] = -50.0        # MATCHES SIMULATE (-50)
        
        # Add Time (0) and Amount
        row = [0] + features + [amount_val]
        data.append(row)
        
    # Create DataFrame
    columns = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
    df_chaos = pd.DataFrame(data, columns=columns)
    df_chaos['Class'] = 1 # MARK AS FRAUD
    
    return df_chaos

def retrain_model():
    print("🔄 STARTING RETRAINING PIPELINE (GOD MODE)...")

    # 1. Load Original Data
    print("   Loading original training data...")
    try:
        df_original = pd.read_csv(ORIGINAL_DATA_PATH, nrows=50000)
    except FileNotFoundError:
        print("   ❌ Error: creditcard.csv not found.")
        return

    # 2. GENERATE SYNTHETIC CHAOS DATA
    df_chaos = generate_synthetic_chaos_data(5000)

    # 3. Combine Datasets
    print("   Merging datasets...")
    df_combined = pd.concat([df_original, df_chaos], ignore_index=True)
    
    # 4. Preprocessing
    X = df_combined.drop('Class', axis=1)
    y = df_combined['Class']
    
    print("   Balancing with SMOTE...")
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X, y)
    
    # 5. Train V2
    print("   🚀 Training Model V2 (The Expert)...")
    model_v2 = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model_v2.fit(X_res, y_res)
    
    # 6. Save V2
    joblib.dump(model_v2, MODEL_V2_PATH)
    print(f"   ✅ SUCCESS! Model V2 saved to {MODEL_V2_PATH}")

if __name__ == "__main__":
    retrain_model()