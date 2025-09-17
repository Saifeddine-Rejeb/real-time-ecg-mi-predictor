from flask import Flask, jsonify, request
from flask_cors import CORS
import wfdb
import requests
import os 
from scipy.signal import butter, sosfilt, iirnotch, filtfilt, medfilt, resample
import scipy.stats
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
CORS(app,
    resources={r"/api/*": {"origins": ["http://localhost:5173"]}},
    supports_credentials=True,
    expose_headers=["Authorization"])

BASE_ECG_DIR = os.getenv("ECG_DATA_DIR", "patients_test")

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
    ecg_file_path = os.path.join(BASE_ECG_DIR, file_param)
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

# List available ECG records under patients_test
@app.route('/api/records')
def list_records():
    target_class = request.args.get('class')
    include_meta = str(request.args.get('meta', 'false')).lower() == 'true'
    records = []
    try:
        class_dirs = [d for d in os.listdir(BASE_ECG_DIR) if os.path.isdir(os.path.join(BASE_ECG_DIR, d))]
        if target_class:
            class_dirs = [d for d in class_dirs if d == target_class]
        for class_dir in class_dirs:
            class_path = os.path.join(BASE_ECG_DIR, class_dir)
            for name in os.listdir(class_path):
                if not name.endswith('.hea'):
                    continue
                base = os.path.splitext(name)[0]
                dat_path = os.path.join(class_path, base + '.dat')
                if not os.path.exists(dat_path):
                    continue
                rel_path = os.path.join(class_dir, base).replace('\\', '/')
                item = {
                    'id': base,
                    'class': class_dir,
                    'path': rel_path,
                }
                if include_meta:
                    try:
                        header = wfdb.rdheader(os.path.join(class_path, base))
                        fs = getattr(header, 'fs', None)
                        sig_len = getattr(header, 'sig_len', None)
                        n_sig = getattr(header, 'n_sig', None)
                        item.update({'fs': fs, 'samples': sig_len, 'leads': n_sig})
                    except Exception:
                        pass
                records.append(item)
        return jsonify(records)
    except FileNotFoundError:
        return jsonify([])

# Prediction route: sends ECG data to microservice for a given file
@app.route('/api/predict', methods=['POST'])
def predict():
    req_data = request.get_json()
    file_param = req_data.get('file')
    if not file_param:
        return jsonify({'error': 'Missing file parameter'}), 400
    ecg_file_path = os.path.join(BASE_ECG_DIR, file_param)
    try:
        signal, fields = wfdb.rdsamp(ecg_file_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # --- Preprocessing pipeline (match test.py) ---
    # 1. Select first lead
    if hasattr(signal, 'ndim') and signal.ndim == 2:
        sig = signal[:, 0].astype(float)
    else:
        sig = signal.astype(float)

    # 2. Bandpass filter (0.5–40 Hz)
    fs = int(fields.get('fs', 360)) if isinstance(fields, dict) else 360
    try:
        sos_bandpass = butter(4, [0.5, 40], btype='band', fs=fs, output='sos')
        sig = sosfilt(sos_bandpass, sig)
    except Exception:
        pass

    # 3. Notch filter (50 Hz)
    try:
        b_notch, a_notch = iirnotch(50, 30, fs=fs)
        sig = filtfilt(b_notch, a_notch, sig)
    except Exception:
        pass

    # 4. Baseline removal (median filter)
    try:
        baseline = medfilt(sig, kernel_size=71)
        sig = sig - baseline
    except Exception:
        pass

    # 5. Outlier removal (z-score)
    try:
        z_scores = np.abs(scipy.stats.zscore(sig))
        outliers_mask = z_scores < 3.0
        if np.sum(~outliers_mask) > 0:
            sig_clean = sig.copy()
            outlier_indices = np.where(~outliers_mask)[0]
            for idx in outlier_indices:
                if idx > 0 and idx < len(sig) - 1:
                    sig_clean[idx] = (sig[idx - 1] + sig[idx + 1]) / 2
            sig = sig_clean
    except Exception:
        pass

    # 6. Resample to 187
    try:
        sig = resample(sig, 187)
    except Exception:
        sig = sig[:187] if len(sig) >= 187 else np.pad(sig, (0, 187 - len(sig)), 'constant')

    # 7. Min-max normalization
    sig_min = np.min(sig)
    sig_max = np.max(sig)
    if sig_max - sig_min > 0:
        sig_norm = (sig - sig_min) / (sig_max - sig_min)
    else:
        sig_norm = np.zeros_like(sig)
    sig_norm = np.clip(sig_norm, 0, 1)

    ecg_data = sig_norm.tolist()
    predict_url = os.getenv("PREDICT_URL", "http://localhost:5001/predict")

    print('Prepared ECG array shape:', np.shape(ecg_data))
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
        normalized = patient_param.replace('\\', '/')
        ecg_file_path = None

        if '/' in normalized:
            ecg_file_path = os.path.join(BASE_ECG_DIR, *normalized.split('/'))
        else:
            try:
                candidates = [
                    os.path.join(BASE_ECG_DIR, d, patient_param)
                    for d in os.listdir(BASE_ECG_DIR)
                    if os.path.isdir(os.path.join(BASE_ECG_DIR, d))
                ]
            except FileNotFoundError:
                candidates = []

            for cand in candidates:
                try:
                    signal, fields = wfdb.rdsamp(cand)
                    ecg_file_path = cand
                    break
                except Exception:
                    continue

        if ecg_file_path is None:
            ecg_file_path = os.path.join(BASE_ECG_DIR, patient_param)

        try:
            signal, fields = wfdb.rdsamp(ecg_file_path)
            fs = int(fields.get('fs', 500)) if isinstance(fields, dict) else 500
            rr_distances, r_peaks = calculate_rr_intervals(signal, fs=fs)
        except Exception as e:
            print('Error reading ECG file:', e)
            rr_distances = []

        pcg_file_path = f"test/pcg/a0409"
        try:
            pcg_signal, pcg_fields = wfdb.rdsamp(pcg_file_path)
            pcg_signal = pcg_signal[:, 0].tolist()  
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

