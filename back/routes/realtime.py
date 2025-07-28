from flask import Blueprint, request, jsonify
import os
import requests

realtime_bp = Blueprint('realtime', __name__)

@realtime_bp.route('/api/realtime/predict', methods=['GET', 'POST'])
def realtime_predict():
    """
    Streams batches 10 by 10 from sensors collection and sends each group to the model API.
    Returns a list of predictions for each group.
    Query params: patient_id (optional)
    """
    req_data = request.get_json()
    ecg_data = req_data.get('ecg')
    if not ecg_data:
        return jsonify({"success": False, "error": "Missing 'ecg' data in request."}), 400
    predict_url = os.getenv("PREDICT_URL", "http://localhost:5001/predict")
    try:
        response = requests.post(predict_url, json={"ecg": ecg_data})
        result = response.json()
        return jsonify({"success": True, "prediction": result}), response.status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


