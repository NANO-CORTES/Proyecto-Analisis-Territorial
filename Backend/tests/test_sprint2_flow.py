import requests
import json
import time

GATEWAY_URL = "http://localhost:8000"

def test_sprint2_flow():
    print("=== SPRINT 2 INTEGRATION TEST ===")
    
    # 1. Login
    print("\n1. Logging in as Admin...")
    login_data = {
        "username": "admin@territorial.com",
        "password": "admin123"
    }
    try:
        # Auth proxy is at /api/v1/auth/login
        resp = requests.post(f"{GATEWAY_URL}/api/v1/auth/login", data=login_data)
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} - {resp.text}")
            return
        token = resp.json()["access_token"]
        print("Login successful")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Set Configuration (HU-14)
    print("\n2. Setting Scoring Configuration...")
    profile_data = {
        "name": "Tiendas de Conveniencia",
        "description": "Perfil para apertura de minimercados",
        "target_business_type": "Retail"
    }
    
    try:
        # Create Profile - Path: /api/v1/configuration/api/v1/config/profiles
        # (Based on ms-configuration main.py endpoints)
        resp = requests.post(f"{GATEWAY_URL}/api/v1/configuration/api/v1/config/profiles", json=profile_data, headers=headers)
        print(f"Create Profile: {resp.status_code}")
        if resp.status_code == 200:
            profile = resp.json()
            profile_id = profile["id"]
            
            # Set Weights - Path: /api/v1/configuration/api/v1/config/scoring
            weights_data = {
                "profile_id": profile_id,
                "population_weight": 0.4,
                "income_weight": 0.3,
                "education_weight": 0.2,
                "competition_weight": 0.1
            }
            resp = requests.post(f"{GATEWAY_URL}/api/v1/configuration/api/v1/config/scoring", json=weights_data, headers=headers)
            print(f"Set Weights: {resp.status_code}")
    except Exception as e:
        print(f"Config failed: {e}")

    # 3. Analytics - Indicators & Scoring (HU-13, 15)
    print("\n3. Testing Analytics (Mock Run ID)...")
    dummy_run_id = "test-run-123"
    
    try:
        # Calculate Indicators - Path: /api/v1/analytics/api/v1/indicators/calculate
        resp = requests.post(f"{GATEWAY_URL}/api/v1/analytics/api/v1/indicators/calculate?transformation_run_id={dummy_run_id}", headers=headers)
        # Note: This will return 500 if no data in transformation, but we check if the endpoint is reached
        print(f"Calculate Indicators: {resp.status_code}")
        
        # Execute Scoring - Path: /api/v1/analytics/api/v1/scoring/execute
        resp = requests.post(f"{GATEWAY_URL}/api/v1/analytics/api/v1/scoring/execute?transformation_run_id={dummy_run_id}", headers=headers)
        print(f"Execute Scoring: {resp.status_code}")
    except Exception as e:
        print(f"Analytics failed: {e}")

    # 4. BFF Summary (HU-17)
    print("\n4. Testing BFF Zone Summary...")
    zone_code = "BOG-001"
    try:
        # BFF path is /api/v1/bff/zone-summary/{zone_code}
        resp = requests.get(f"{GATEWAY_URL}/api/v1/bff/zone-summary/{zone_code}", headers=headers)
        print(f"BFF Summary: {resp.status_code}")
        if resp.status_code == 200:
            print(json.dumps(resp.json(), indent=2))
        else:
             print(f"BFF Summary result: {resp.text}")
    except Exception as e:
        print(f"BFF Summary failed: {e}")

if __name__ == "__main__":
    test_sprint2_flow()
