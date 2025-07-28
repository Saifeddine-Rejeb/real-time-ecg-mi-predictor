from models.alert_model import create_alert, get_alert_by_id, get_alerts_by_patient, get_alerts_by_doctor, update_alert, delete_alert

# Business logic for alerts
def add_alert(alert_data):
    # Add validation, etc. here
    return create_alert(alert_data)

def find_alert_by_id(alert_id):
    return get_alert_by_id(alert_id)

def find_alerts_by_patient(patient_id):
    return get_alerts_by_patient(patient_id)

def find_alerts_by_doctor(doctor_id):
    return get_alerts_by_doctor(doctor_id)

def modify_alert(alert_id, update):
    return update_alert(alert_id, update)

def remove_alert(alert_id):
    return delete_alert(alert_id)
