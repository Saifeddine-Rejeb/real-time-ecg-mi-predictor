
import requests
import json
import os
import dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

dotenv.load_dotenv('.env')
uri = os.getenv('MONGO_URI_ECG', None)
client = MongoClient(uri, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    sensors_db = client.get_database('sensors_db')
    print('MongoDB connection successful.')
except Exception as e:
    sensors_db = None
    print('MongoDB connection error:', e)

def test_mongo_ecg(base_url="http://localhost:5000", window=10, start=0):
    url = f"{base_url}/api/mongo/ecg?window={window}&start={start}"
    print(f"Testing ECG endpoint: {url}")
    response = requests.get(url)
    print("Status Code:", response.status_code)
    try:
        data = response.json()
        print("ECG Data (first 5):", json.dumps(data[:5], indent=2))
    except Exception as e:
        print("Error parsing ECG response:", e)

def test_mongo_vitals(base_url="http://localhost:5000", window=10, start=0):
    url = f"{base_url}/api/mongo/vitals?window={window}&start={start}"
    print(f"Testing Vitals endpoint: {url}")
    response = requests.get(url)
    print("Status Code:", response.status_code)
    try:
        data = response.json()
        print("Vitals Data:", json.dumps(data, indent=2))
    except Exception as e:
        print("Error parsing Vitals response:", e)

if __name__ == "__main__":
    test_mongo_ecg()
    test_mongo_vitals()
