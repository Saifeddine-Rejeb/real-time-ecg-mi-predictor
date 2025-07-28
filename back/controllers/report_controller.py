from models.report_model import create_report, get_report_by_id, get_reports_by_patient, get_reports_by_doctor, update_report, delete_report

# Business logic for reports
def add_report(report_data):
    # Add validation, etc. here
    return create_report(report_data)

def find_report_by_id(report_id):
    return get_report_by_id(report_id)

def find_reports_by_patient(patient_id):
    return get_reports_by_patient(patient_id)

def find_reports_by_doctor(doctor_id):
    return get_reports_by_doctor(doctor_id)

def modify_report(report_id, update):
    return update_report(report_id, update)

def remove_report(report_id):
    return delete_report(report_id)
