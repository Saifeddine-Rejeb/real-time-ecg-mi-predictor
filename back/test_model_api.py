import requests
import os

# Set the model API endpoint
predict_url = os.getenv("PREDICT_URL", "http://localhost:5001/predict")

# Build a (5000, 12) array: lead1 and lead2 filled with sample values, rest zero
sample_lead1 = [1.0] * 5000
sample_lead2 = [2.0] * 5000

ecgs = []
for i in range(5000):
    row = [sample_lead1[i], sample_lead2[i]] + [0.0]*10
    ecgs.append(row)

print(f"Sending to model API: shape=({len(ecgs)}, {len(ecgs[0])})")
print("First 2 rows:", ecgs[:2])
print("Last 2 rows:", ecgs[-2:])

try:
    response = requests.post(predict_url, json={"ecg": ecgs})
    print("Model API response:", response.json())
except Exception as e:
    print("Error calling model API:", e)
