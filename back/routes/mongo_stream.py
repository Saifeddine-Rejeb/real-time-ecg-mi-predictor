from flask import Blueprint, jsonify, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import dotenv
import numpy as np
from utils import calculate_rr_intervals, heart_rate, heart_rate_variability
from flask import g, has_app_context

def get_sensors_db():
    if has_app_context():
        if 'sensors_db' not in g:
            dotenv.load_dotenv('.env')
            uri = os.getenv('MONGO_URI_ECG', None)
            client = MongoClient(uri, server_api=ServerApi('1'))
            try:
                client.admin.command('ping')
                g.sensors_db = client.get_database('sensors_db')
            except Exception:
                g.sensors_db = None
        return g.sensors_db
    return None

mongo_stream_bp = Blueprint('mongo_stream', __name__)

@mongo_stream_bp.route('/api/mongo/stream', methods=['GET'])
def mongo_stream():
    sensors_db = get_sensors_db()
    if sensors_db is None or 'sensors' not in sensors_db.list_collection_names():
        return jsonify({'error': 'MongoDB sensors collection not available'}), 500

    start = int(request.args.get('start', 0))
    count = int(request.args.get('count', 10))
    docs = sensors_db['sensors'].find().sort('_id', 1).skip(start).limit(count)

    results = []
    for doc in docs:
        batch = doc.get('batch', [])
        ecg = [[float(sample.get(f'lead{i}', 0)) for i in range(1, 13)] for sample in batch]
        results.append({'ecg': ecg[:5000]})

    return jsonify(results)

@mongo_stream_bp.route('/api/mongo/vitals', methods=['GET'])
def mongo_vitals():
    sensors_db = get_sensors_db()
    if sensors_db is None or 'sensors' not in sensors_db.list_collection_names():
        return jsonify({'error': 'MongoDB sensors collection not available'}), 500

    window = int(request.args.get('window', 10))
    start = int(request.args.get('start', 0))
    docs = sensors_db['sensors'].find().sort('_id', 1).skip(start).limit(window)

    all_samples = []
    for doc in docs:
        batch = doc.get('batch', [])
        all_samples.extend(batch)

    signal = np.zeros((len(all_samples), 12))
    for i, sample in enumerate(all_samples):
        for j in range(12):
            signal[i, j] = float(sample.get(f'lead{j+1}', 0))

    try:
        rr_distances, _ = calculate_rr_intervals(signal)
    except:
        rr_distances = []

    avg_rr = round(sum(rr_distances) / len(rr_distances), 2) if rr_distances else None
    hr = heart_rate(rr_distances) if rr_distances else None
    hrv = heart_rate_variability(rr_distances) if rr_distances else None

    vitals = {
        'heartRate': hr,
        'hrv': hrv,
        'respiratoryRate': '--',
        'skinTemp': '--',
        'pcg': '--',
        'pcgSignal': [],
        'rrDistances': rr_distances,
        'rrIntervalAvg': avg_rr,
    }

    return jsonify(vitals)
