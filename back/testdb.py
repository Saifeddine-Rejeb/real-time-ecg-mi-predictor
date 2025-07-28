from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import dotenv
import numpy as np
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import requests
import matplotlib.pyplot as plt


dotenv.load_dotenv('.env')

uri = os.getenv('MONGO_URI_ECG', None)

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    # List all databases in the cluster
    db_names = client.list_database_names()
    print("Databases in cluster:", db_names)
    # Access sensors_db and list its collections
    sensors_db = client.get_database('sensors_db')
    sensors_collections = sensors_db.list_collection_names()
    print("Collections in sensors_db:", sensors_collections)
    # Get the first item in the 'sensors' collection

    if 'sensors' in sensors_collections:
        # True streaming: fetch batches from MongoDB as needed in animation

        window = 10  
        total_batches = sensors_db['sensors'].count_documents({})
        print(f"Total items in 'sensors' collection: {total_batches} found.")
        start_idx = max(0, total_batches - 20)

        batch_cache = {'data': [], 'start': 0}

        def get_total_batches():
            return sensors_db['sensors'].count_documents({})

        def load_batches(start, count=10):
            docs = sensors_db['sensors'].find().sort('_id', 1).skip(start).limit(count)
            return [doc['batch'] for doc in docs if doc and 'batch' in doc and isinstance(doc['batch'], list)]

        def update(frame):
            plt.clf()
            idx = start_idx + frame

            if idx >= batch_cache['start'] + len(batch_cache['data']):
                batch_cache['data'] = load_batches(idx, 10)
                batch_cache['start'] = idx

            if idx < window:
                batch_indices = range(start_idx, idx+1)
            else:
                batch_indices = range(idx-window+1, idx+1)

            current_batches = []
            for i in batch_indices:
                cache_offset = i - batch_cache['start']
                if 0 <= cache_offset < len(batch_cache['data']):
                    current_batches.append(batch_cache['data'][cache_offset])
                else:
                    batch = load_batches(i, 1)
                    current_batches.extend(batch)

            lead1 = [item.get('lead1', 0) for batch in current_batches for item in batch]
            lead2 = [item.get('lead2', 0) for batch in current_batches for item in batch]
            n_points = min(len(lead1), 5000)
            x = list(range(n_points))
            plt.plot(x, lead1[:n_points], color='blue', label='Lead 1')
            plt.plot(x, lead2[:n_points], color='orange', label='Lead 2')
            plt.title('Live Sensor Data (Streaming, Sliding Window of 10 Batches)')
            plt.xlabel('Échantillon')
            plt.ylabel('Lead Value')
            plt.legend()
            plt.grid(True)

        def api_request_loop():
            print("\nTesting realtime vitals and prediction API with batches of 10...")
            predict_url = os.getenv("PREDICT_URL", "http://localhost:5000/api/realtime/predict")
            vitals_url = "http://localhost:5000/api/mongo/vitals"
            # Start from the last 20 batches, moving backwards in steps of 10
            for start in range(max(0, total_batches - 20), total_batches, 10):
                params = {"window": 10, "start": start}
                batches = load_batches(start, 10)
                all_samples = [item for batch in batches for item in batch]
                if len(all_samples) == 0:
                    print(f"Batches {start} to {start+9}: No data found, skipping API call.")
                    continue

                # Get vitals for this batch
                try:
                    vitals_response = requests.get(vitals_url, params=params)
                    print(f"Vitals for batches {start} to {start+9} (status {vitals_response.status_code}):")
                    vitals_data = vitals_response.json()
                    print(vitals_data)
                except Exception as e:
                    print(f"Error getting vitals for batches {start} to {start+9}: {e}")

                # Get prediction for this batch
                ecg_array = np.zeros((5000, 12), dtype=float)
                for i in range(min(5000, len(all_samples))):
                    sample = all_samples[i]
                    ecg_array[i, 0] = float(sample.get('lead1', 0))
                    ecg_array[i, 1] = float(sample.get('lead2', 0))
                print(f"Sending to API: shape={ecg_array.shape}")
                try:
                    response = requests.post(predict_url, json={"ecg": ecg_array.tolist()})
                    result = response.json()
                    print(f"Prediction for batches {start} to {start+9}:", result)
                except Exception as e:
                    print(f"Error for batches {start} to {start+9}: {e}")

        api_thread = threading.Thread(target=api_request_loop, daemon=True)
        api_thread.start()

        fig = plt.figure(figsize=(14, 5))
        anim = FuncAnimation(fig, update, frames=range(0, get_total_batches() - start_idx), interval=500, repeat=False)
        plt.show()
    else:
        print("'sensors' collection does not exist.")

except Exception as e:
    print(e)
