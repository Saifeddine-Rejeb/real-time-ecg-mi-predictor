from db.mongodb import db
from bson import ObjectId

# User schema: admin, doctor, patient
# Example user: { _id, name, email, password_hash, type: 'admin'|'doctor'|'patient', doctor_id, patient_id, device_ids }
users = db.users

# User CRUD

def create_user(user):
    return users.insert_one(user)

def get_user_by_email(email):
    return users.find_one({'email': email})

def get_user_by_id(user_id):
    return users.find_one({'_id': ObjectId(user_id)})

def find_all_users():
    return list(users.find())

def update_user(user_id, update):
    return users.update_one({'_id': ObjectId(user_id)}, {'$set': update})

def delete_user(user_id):
    return users.delete_one({'_id': ObjectId(user_id)})
