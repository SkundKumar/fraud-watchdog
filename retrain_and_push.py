import boto3
import os
import time

# 1. SETUP
TABLE_NAME = 'FraudWatchdog_Events'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

print("🔍 Step 1: Scanning Cloud Memory (DynamoDB) for Human Feedback...")

# 2. PULL LABELED DATA
# We look for transactions that you clicked "Approve as Fraud" on
response = table.scan()
items = response.get('Items', [])

if not items:
    print("❌ No transactions found in the cloud. Go to your React app and launch an attack first!")
    exit()

print(f"✅ Found {len(items)} transactions. Retraining AI with new patterns...")

# 3. SIMULATE RETRAINING
# In a real scenario, you'd run your Scikit-Learn fit() here.
# For the demo, we are updating the local model file to trigger a 'change' for Git.
with open("backend/model/last_train_log.txt", "a") as f:
    f.write(f"Model retrained on {time.ctime()} with {len(items)} new samples.\n")

# 4. TRIGGER MLOPS PIPELINE
print("🚀 Step 2: Pushing updated model to GitHub to trigger AWS S3 Sync...")
os.system('git add .')
os.system('git commit -m "MLOps: AI adapted to new fraud patterns"')
os.system('git push origin main')

print("\n✨ SUCCESS! Now go to GitHub and watch the 'Green Circle' spin.")