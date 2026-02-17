import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

# --- CONFIGURATION ---
DATA_PATH = 'data/creditcard.csv'
MODEL_PATH = 'backend/model/fraud_v1.pkl'

# --- 1. LOAD DATA ---
if not os.path.exists(DATA_PATH):
    print(f"ERROR: File not found at {DATA_PATH}. Did you download it?")
    exit()

print("Loading dataset... (This might take 30 seconds)")
# We use all rows. If your PC is very slow, add nrows=50000 inside read_csv
df = pd.read_csv(DATA_PATH)

# --- 2. PREPROCESSING ---
# The dataset is already cleaned (V1-V28 are PCA features).
# 'Class' is the target: 0 = Normal, 1 = Fraud
X = df.drop('Class', axis=1)
y = df['Class']

# --- 3. HANDLE IMBALANCE (SMOTE) ---
print("Balancing data with SMOTE... (Creating synthetic fraud examples)")
# This makes sure the model sees 50% fraud and 50% legit during training
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

print(f"Original dataset shape: {y.value_counts()}")
print(f"Resampled dataset shape: {y_res.value_counts()}")

# --- 4. SPLIT DATA ---
X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, random_state=42)

# --- 5. TRAIN MODEL ---
print("Training the Random Forest Model... (Go grab a coffee, this takes time)")
# n_estimators=50 is a balance between speed and accuracy
model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# --- 6. EVALUATE ---
print("Evaluating Model...")
y_pred = model.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# --- 7. SAVE MODEL ---
# Create directory if it doesn't exist
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(model, MODEL_PATH)
print(f"SUCCESS! Model saved to {MODEL_PATH}")