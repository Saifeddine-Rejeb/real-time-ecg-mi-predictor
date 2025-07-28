from flask import Blueprint, request, jsonify
from controllers.report_controller import add_report, find_report_by_id, find_reports_by_patient, find_reports_by_doctor, modify_report, remove_report

reports_bp = Blueprint('reports_bp', __name__, url_prefix='/api/reports')

@reports_bp.route('', methods=['POST'])
def create_report():
    report_data = request.get_json()
    result = add_report(report_data)
    return jsonify({'inserted_id': str(result.inserted_id)})

@reports_bp.route('/<report_id>', methods=['GET'])
def get_report(report_id):
    report = find_report_by_id(report_id)
    if report:
        report['_id'] = str(report['_id'])
        return jsonify(report)
    return jsonify({'error': 'Report not found'}), 404

@reports_bp.route('/patient/<patient_id>', methods=['GET'])
def get_reports_by_patient(patient_id):
    reports = find_reports_by_patient(patient_id)
    for r in reports:
        r['_id'] = str(r['_id'])
    return jsonify(reports)

@reports_bp.route('/doctor/<doctor_id>', methods=['GET'])
def get_reports_by_doctor(doctor_id):
    reports = find_reports_by_doctor(doctor_id)
    for r in reports:
        r['_id'] = str(r['_id'])
    return jsonify(reports)

@reports_bp.route('/<report_id>', methods=['PUT'])
def update_report(report_id):
    update = request.get_json()
    result = modify_report(report_id, update)
    return jsonify({'modified_count': result.modified_count})

@reports_bp.route('/<report_id>', methods=['DELETE'])
def delete_report(report_id):
    result = remove_report(report_id)
    return jsonify({'deleted_count': result.deleted_count})
