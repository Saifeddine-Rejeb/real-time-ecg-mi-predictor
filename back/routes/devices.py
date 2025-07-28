from flask import Blueprint, request, jsonify
from controllers.device_controller import add_device, find_device_by_id, find_devices_by_patient, modify_device, remove_device
from datetime import datetime

devices_bp = Blueprint('devices_bp', __name__, url_prefix='/api/devices')

@devices_bp.route('', methods=['POST'])
def create_device():
    device_data = request.get_json()
    device_data['assigned_at'] = datetime.utcnow().isoformat() + 'Z'
    result = add_device(device_data)
    return jsonify({'inserted_id': str(result.inserted_id)})

@devices_bp.route('/<device_id>', methods=['GET'])
def get_device(device_id):
    device = find_device_by_id(device_id)
    if device:
        device['_id'] = str(device['_id'])
        return jsonify(device)
    return jsonify({'error': 'Device not found'}), 404

@devices_bp.route('/patient/<patient_id>', methods=['GET'])
def get_devices_by_patient(patient_id):
    devices = find_devices_by_patient(patient_id)
    for d in devices:
        d['_id'] = str(d['_id'])
    return jsonify(devices)

@devices_bp.route('/<device_id>', methods=['PUT'])
def update_device(device_id):
    update = request.get_json()
    result = modify_device(device_id, update)
    return jsonify({'modified_count': result.modified_count})

@devices_bp.route('/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    result = remove_device(device_id)
    return jsonify({'deleted_count': result.deleted_count})
