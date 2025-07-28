from flask import Blueprint, request, jsonify
from controllers.alert_controller import add_alert, find_alert_by_id, find_alerts_by_patient, find_alerts_by_doctor, modify_alert, remove_alert

alerts_bp = Blueprint('alerts_bp', __name__, url_prefix='/api/alerts')

@alerts_bp.route('', methods=['POST'])
def create_alert():
    alert_data = request.get_json()
    result = add_alert(alert_data)
    return jsonify({'inserted_id': str(result.inserted_id)})

@alerts_bp.route('/<alert_id>', methods=['GET'])
def get_alert(alert_id):
    alert = find_alert_by_id(alert_id)
    if alert:
        alert['_id'] = str(alert['_id'])
        return jsonify(alert)
    return jsonify({'error': 'Alert not found'}), 404

@alerts_bp.route('/patient/<patient_id>', methods=['GET'])
def get_alerts_by_patient(patient_id):
    alerts = find_alerts_by_patient(patient_id)
    for a in alerts:
        a['_id'] = str(a['_id'])
    return jsonify(alerts)

@alerts_bp.route('/doctor/<doctor_id>', methods=['GET'])
def get_alerts_by_doctor(doctor_id):
    alerts = find_alerts_by_doctor(doctor_id)
    for a in alerts:
        a['_id'] = str(a['_id'])
    return jsonify(alerts)

@alerts_bp.route('/<alert_id>', methods=['PUT'])
def update_alert(alert_id):
    update = request.get_json()
    result = modify_alert(alert_id, update)
    return jsonify({'modified_count': result.modified_count})

@alerts_bp.route('/<alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    result = remove_alert(alert_id)
    return jsonify({'deleted_count': result.deleted_count})
