from flask import Flask, jsonify, request
from flask_cors import CORS
import wfdb
import requests
import os 
from utils import calculate_rr_intervals, heart_rate, heart_rate_variability
from routes.users import users_bp
from routes.devices import devices_bp
from routes.reports import reports_bp
from routes.alerts import alerts_bp
from auth.routes import auth_bp
from routes.realtime import realtime_bp
from routes.mongo_stream import mongo_stream_bp
import numpy as np
app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(users_bp)
app.register_blueprint(devices_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(realtime_bp)
app.register_blueprint(mongo_stream_bp)


# ECG route: returns raw ECG signal for a given file
@app.route('/api/ecg')
def get_ecg():
    file_param = request.args.get('file')
    if not file_param: 
        return jsonify({'error': 'Missing file parameter'}), 400
    ecg_file_path = f"test/{file_param}"
    try:
        signal, fields = wfdb.rdsamp(ecg_file_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    n_samples, n_leads = signal.shape
    data = []
    for i in range(n_samples):
        entry = {'time': i}
        for j in range(n_leads):
            entry[f'lead{j+1}'] = float(signal[i, j])
        data.append(entry)
    return jsonify(data)

# Prediction route: sends ECG data to microservice for a given file
@app.route('/api/predict', methods=['POST'])
def predict():
    req_data = request.get_json()
    file_param = req_data.get('file')
    if not file_param:
        return jsonify({'error': 'Missing file parameter'}), 400
    ecg_file_path = f"test/{file_param}"
    try:
        signal, fields = wfdb.rdsamp(ecg_file_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    ecg_data = signal.tolist()
    predict_url = os.getenv("PREDICT_URL", "http://localhost:5001/predict")

    print('Received ECG data:', type(ecg_data))  
    try:
        response = requests.post(predict_url, json={"ecg": ecg_data})
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:   
        return jsonify({"error": str(e)}), 500

@app.route('/api/vitals')
def vitals():
    patient_param = request.args.get('patient')
    rr_distances = []
    pcg_signal = []
    if patient_param:
        ecg_file_path = f"test/normal/{patient_param}"
        try:
            signal, fields = wfdb.rdsamp(ecg_file_path)
            rr_distances, r_peaks = calculate_rr_intervals(signal)
        except Exception as e:
            print('Error reading ECG file from normal:', e)
            ecg_file_path = f"test/mi(crise)/{patient_param}"
            try:
                signal, fields = wfdb.rdsamp(ecg_file_path)
                rr_distances, r_peaks = calculate_rr_intervals(signal)
            except Exception as e2:
                print('Error reading ECG file from mi(crise):', e2)
                rr_distances = []
        
        # Try to read PCG signal from testpcg.py location
        pcg_file_path = f"test/pcg/a0409"
        try:
            pcg_signal, pcg_fields = wfdb.rdsamp(pcg_file_path)
            pcg_signal = pcg_signal[:, 0].tolist()  # Use first channel
            # Only keep the first 10 seconds
            if 'fs' in pcg_fields:
                sample_rate = int(pcg_fields['fs'])
                pcg_signal = pcg_signal[:sample_rate * 10]
        except Exception as e:
            print('Error reading PCG file:', e)
            pcg_signal = []
    avg_rr = round(sum(rr_distances) / len(rr_distances), 2) if rr_distances else None
    heart_rate_value = heart_rate(rr_distances) if rr_distances else None
    hrv = heart_rate_variability(rr_distances) if rr_distances else None

    example_vitals = {
        'heartRate': heart_rate_value,
        'pcg': 'Normal S1/S2',
        'skinTemp': 36.9,
        'hrv': hrv,
        'respiratoryRate': 16,
        'rrDistances': rr_distances,
        'pcgSignal': pcg_signal,
        'rrIntervalAvg': avg_rr,
    }
    return jsonify(example_vitals)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

