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

def upload_dataset(token, file_path, source_name, source_type):
    print(f"\nUploading {file_path}...")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
        
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(file_path, "rb") as f:
        files = {'file': (os.path.basename(file_path), f)}
        data = {"sourceName": source_name, "sourceType": source_type}
        try:
            resp = requests.post(f"{BASE_URL}/ingestion/datasets/upload", headers=headers, files=files, data=data)
            if resp.status_code == 200:
                dataset_id = resp.json()["datasetId"]
                print(f"SUCCESS: dataset_id={dataset_id} for {os.path.basename(file_path)}")
                return True
            elif resp.status_code == 409:
                print(f"SUCCESS (ALREADY UPLOADED): {resp.status_code} {resp.json().get('detail')}")
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
        
    datasets = [
        ("bogota_calidad_educativa.csv", "Calidad Educativa Bogota", "CSV"),
        ("bogota_infraestructura_servicios.json", "Infraestructura y Servicios Bogota", "JSON"),
        ("bogota_salud_bienestar.csv", "Salud y Bienestar Bogota", "CSV"),
        ("bogota_desarrollo_socioeconomico.json", "Desarrollo Socioeconomico Bogota", "JSON")
    ]
    
    all_success = True
    for filename, name, dtype in datasets:
        # The files are in the root directory, which is one level up from Backend/tests/
        # Or we can use absolute paths relative to workspace root
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", filename))
        success = upload_dataset(token, path, name, dtype)
        if not success:
            all_success = False
            
    if all_success:
        print("\nAll 4 real datasets processed/verified successfully!")
    else:
        print("\nSome datasets failed to process.")
        sys.exit(1)
