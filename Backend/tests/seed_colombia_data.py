import requests
import os
import sys

BASE_URL = "http://localhost:8000/api/v1"

def login():
    print("Logging in as Admin...")
    login_data = {
        "username": "admin@territorial.com",
        "password": "admin123"
    }
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if resp.status_code == 200:
            token = resp.json()["access_token"]
            print("Login successful")
            return token
        else:
            print(f"Login FAILED: {resp.status_code} {resp.text}")
            return None
    except Exception as e:
        print(f"Login connection FAILED: {e}")
        return None

def upload_dataset(token, file_path):
    print(f"\nSeeding {file_path}...")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
        
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(file_path, "rb") as f:
        files = {'file': (os.path.basename(file_path), f)}
        data = {
            "sourceName": "Preload Departamentos y Municipios",
            "sourceType": "CSV"
        }
        try:
            resp = requests.post(f"{BASE_URL}/ingestion/datasets/upload", headers=headers, files=files, data=data)
            if resp.status_code == 200:
                dataset_id = resp.json()["datasetId"]
                print(f"SUCCESS: Seeded dataset_id={dataset_id} for {os.path.basename(file_path)}")
                return True
            else:
                print(f"FAILED: {resp.status_code} {resp.text}")
                return False
        except Exception as e:
            print(f"Request failed: {e}")
            return False

if __name__ == "__main__":
    token = login()
    if not token:
        sys.exit(1)
        
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "colombia_departamentos_municipios.csv"))
    success = upload_dataset(token, csv_path)
    if success:
        print("\nColombia departments and municipalities successfully seeded in the database!")
    else:
        print("\nFailed to seed database.")
        sys.exit(1)
