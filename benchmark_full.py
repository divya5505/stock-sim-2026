import requests
import time
import json

# 1. CONFIGURATION
# If you are testing locally:
API_URL = "http://127.0.0.1:8000/api/trade"

# If you want to test the Cloud (DigitalOcean) later, swap this URL:
# API_URL = "https://your-app-name.ondigitalocean.app/api/trade"

# 2. PAYLOAD (The Data)
# We use the credentials from your seed.py
trade_data = {
    "team_id": "TEAM_01",
    "team_password": "trade11!",  # Matches the security fix we added
    "ticker": "VOLT",
    "quantity": 1,
    "side": "buy",
    "dealer_id": "DEALER_1",
    "dealer_password": "admin123"
}

def measure_api_speed():
    print(f"🚀 SENDING TRADE REQUEST TO: {API_URL}")
    print(f"📦 Payload: {json.dumps(trade_data, indent=2)}")
    print("-" * 40)

    # 3. START TIMER
    start_time = time.perf_counter()

    try:
        # 4. SEND REQUEST (The heavy lifting)
        response = requests.post(API_URL, json=trade_data)
        
        # 5. STOP TIMER
        end_time = time.perf_counter()
        
        total_time_ms = (end_time - start_time) * 1000

        # 6. ANALYZE RESULT
        if response.status_code == 200:
            print(f"✅ SUCCESS! Trade Executed.")
            print(f"💰 Response: {response.json()}")
        else:
            print(f"❌ FAILED! Status Code: {response.status_code}")
            print(f"⚠️ Error Detail: {response.text}")

        print("-" * 40)
        print(f"⚡ TOTAL API LATENCY: {total_time_ms:.2f} ms")
        
        if total_time_ms < 1000:
            print("🏆 RATING: EXCELLENT (Sub-second)")
        elif total_time_ms < 2000:
            print("⚠️ RATING: ACCEPTABLE (Might feel slightly slow)")
        else:
            print("🔴 RATING: SLOW (Needs optimization)")

    except requests.exceptions.ConnectionError:
        print("❌ CRITICAL ERROR: Could not connect to server.")
        print("👉 Did you remember to run 'uvicorn main:app --reload' in another terminal?")

if __name__ == "__main__":
    measure_api_speed()