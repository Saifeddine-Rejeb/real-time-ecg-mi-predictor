import os
from flask import Flask, request, jsonify
from utils import predict_signal
import json
from flask_cors import CORS
import traceback
import numpy as np

app = Flask(__name__)
CORS(app)

@app.route('/')
def root():
    return 'Prediction service is alive', 200


@app.route('/predict', methods=['POST'])

def predict():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No ECG signal provided'}), 400
    if 'ecg' not in data:
        return jsonify({'error': 'ECG data is missing'}), 400

    ecg = data['ecg']
    ecg = np.array(ecg) 

    
    try:
        prediction = predict_signal(ecg)
        if prediction is None:
            return jsonify({'prediction': None, 'class': 'NORM'}), 200
        return jsonify({'prediction': int(prediction), 'class': 'MI' if prediction == 1 else 'NORM'}), 200
    except Exception as e:
        print("Exception during prediction:", traceback.format_exc())  
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
