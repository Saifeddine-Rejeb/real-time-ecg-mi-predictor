from db.mongodb import db
from bson import ObjectId

# Report schema: made by doctors about patients
# Example report: { _id, doctor_id, patient_id, date, content, files, diagnosis }
reports = db.reports

# Report CRUD

def create_report(report):
    return reports.insert_one(report)

def get_report_by_id(report_id):
    return reports.find_one({'_id': ObjectId(report_id)})

def get_reports_by_patient(patient_id):
    return list(reports.find({'patient_id': patient_id}))

def get_reports_by_doctor(doctor_id):
    return list(reports.find({'doctor_id': doctor_id}))

def update_report(report_id, update):
    return reports.update_one({'_id': ObjectId(report_id)}, {'$set': update})

def delete_report(report_id):
    return reports.delete_one({'_id': ObjectId(report_id)})
