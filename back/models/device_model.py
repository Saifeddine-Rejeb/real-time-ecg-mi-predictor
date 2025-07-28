from db.mongodb import db
from bson import ObjectId

# Device schema: assigned to patients
# Example device: { _id, serial, patient_id, type, status, last_seen }
devices = db.devices

# Device CRUD

def create_device(device):
    return devices.insert_one(device)

def get_device_by_id(device_id):
    return devices.find_one({'_id': ObjectId(device_id)})

def get_devices_by_patient(patient_id):
    return list(devices.find({'patient_id': patient_id}))

def update_device(device_id, update):
    return devices.update_one({'_id': ObjectId(device_id)}, {'$set': update})

def delete_device(device_id):
    return devices.delete_one({'_id': ObjectId(device_id)})
