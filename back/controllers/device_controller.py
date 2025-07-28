from models.device_model import create_device, get_device_by_id, get_devices_by_patient, update_device, delete_device

# Business logic for devices
def add_device(device_data):
    # Add validation, etc. here
    return create_device(device_data)

def find_device_by_id(device_id):
    return get_device_by_id(device_id)

def find_devices_by_patient(patient_id):
    return get_devices_by_patient(patient_id)

def modify_device(device_id, update):
    return update_device(device_id, update)

def remove_device(device_id):
    return delete_device(device_id)
