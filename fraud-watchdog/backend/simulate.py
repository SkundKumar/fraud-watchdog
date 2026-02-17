import requests
import random
import time
import json

# The URL of your API
API_URL = "http://127.0.0.1:8000/predict"

# ANSI Colors for making the terminal look cool
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

def generate_random_transaction():
    # 1. Create a "Normal-ish" transaction (mostly 0s)
    features = [random.gauss(0, 1) for _ in range(28)] # V1-V28
    
    # 2. Add Time (random) and Amount (random)
    time_val = random.randint(0, 170000)
    amount_val = random.uniform(0, 100) # Normal small amount
    
    # --- CHAOS MODE: THE NUCLEAR OPTION ---
    # 50% chance to be a "Massive Fraud"
    # We use EXTREME values so the model cannot miss it
    if random.random() < 0.5: 
        amount_val = 50000.0        # Huge money (50k)
        features[0] = -50.0         # Impossible V1 value
        features[10] = -50.0        # Impossible V10 value
    
    # Combine into the list of 30 features
    full_features = [time_val] + features + [amount_val]
    return full_features

def run_simulation():
    print(f"🚀 Starting NUCLEAR CHAOS Simulation... Targeting {API_URL}")
    print("-" * 60)

    try:
        while True:
            # 1. Generate Fake Data
            fake_features = generate_random_transaction()
            payload = {"features": fake_features}

            # 2. Send to API
            try:
                response = requests.post(API_URL, json=payload)
                data = response.json()
                
                # 3. Print based on Status
                pred = data['prediction']
                conf = data['confidence_score']
                status = data['mlops_status']

                # VISUALIZATION LOGIC
                if status == "UNCERTAIN_GREY_ZONE":
                    print(f"{Colors.YELLOW}[⚠️ DRIFT DETECTED] {pred} | Conf: {conf:.2f} | Status: {status}{Colors.RESET}")
                elif pred == "FRAUD":
                    # This means V2 caught it!
                    print(f"{Colors.RED}[🚫 BLOCKED]       {pred} | Conf: {conf:.2f} | Model V2 is working!{Colors.RESET}")
                else:
                    print(f"{Colors.GREEN}[✅ ALLOWED]       {pred} | Conf: {conf:.2f}{Colors.RESET}")

            except Exception as e:
                print(f"Error calling API: {e}")

            # Faster speed for demo
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n🛑 Simulation Stopped.")

if __name__ == "__main__":
    run_simulation()