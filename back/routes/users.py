
from flask import Blueprint, request, jsonify
from controllers.user_controller import register_user, find_user_by_id, modify_user, remove_user, get_all_users
from werkzeug.security import generate_password_hash
from auth.decorators import jwt_required, role_required


users_bp = Blueprint('users_bp', __name__, url_prefix='/api/users')


# Only admins can create doctors, only doctors can create patients
@users_bp.route('', methods=['POST'])
@jwt_required
def create_user():
    user_data = request.get_json()
    if 'role' in user_data and 'type' not in user_data:
        user_data['type'] = user_data.pop('role')
    creator_role = request.user.get('role')
    new_user_type = user_data.get('type')
    if new_user_type == 'doctor':
        if creator_role != 'admin':
            return jsonify({'error': 'Only admins can create doctors'}), 403
    elif new_user_type == 'patient':
        if creator_role != 'doctor':
            return jsonify({'error': 'Only doctors can create patients'}), 403
        # Assign doctor_id to patient
        user_data['doctor_id'] = str(request.user.get('user_id'))
    elif new_user_type == 'admin':
        return jsonify({'error': 'Cannot create admin users via API'}), 403
    else:
        return jsonify({'error': 'Invalid user type'}), 400
    if 'password' in user_data:
        user_data['password_hash'] = generate_password_hash(user_data.pop('password'))
    result = register_user(user_data)
    return jsonify({'inserted_id': str(result.inserted_id)})


# Only admins and doctors can view users, but doctors can only view their own patients
@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required
@role_required('admin', 'doctor')
def get_user(user_id):
    user = find_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    # If doctor, only allow access to their own patients
    if request.user.get('role') == 'doctor' and user.get('type') == 'patient':
        if str(user.get('doctor_id')) != str(request.user.get('user_id')):
            return jsonify({'error': 'Forbidden'}), 403
    user['_id'] = str(user['_id'])
    user.pop('password_hash', None)
    return jsonify(user)


# Only admins can update doctors, only doctors can update their own patients
@users_bp.route('/<user_id>', methods=['PUT'])
@jwt_required
@role_required('admin', 'doctor')
def update_user(user_id):
    update = request.get_json()
    # Ensure 'type' field is present (convert 'role' to 'type' if needed)
    if 'role' in update and 'type' not in update:
        update['type'] = update.pop('role')
    user = find_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user.get('type') == 'doctor':
        if request.user.get('role') != 'admin':
            return jsonify({'error': 'Only admins can update doctors'}), 403
    elif user.get('type') == 'patient':
        if request.user.get('role') != 'doctor' or str(user.get('doctor_id')) != str(request.user.get('user_id')):
            return jsonify({'error': 'Only the assigned doctor can update this patient'}), 403
    else:
        return jsonify({'error': 'Cannot update this user type'}), 403
    result = modify_user(user_id, update)
    return jsonify({'modified_count': result.modified_count})


# Only admins can delete doctors, only doctors can delete their own patients
@users_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required
@role_required('admin', 'doctor')
def delete_user(user_id):
    user = find_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user.get('type') == 'doctor':
        if request.user.get('role') != 'admin':
            return jsonify({'error': 'Only admins can delete doctors'}), 403
    elif user.get('type') == 'patient':
        if request.user.get('role') != 'doctor' or str(user.get('doctor_id')) != str(request.user.get('user_id')):
            return jsonify({'error': 'Only the assigned doctor can delete this patient'}), 403
    else:
        return jsonify({'error': 'Cannot delete this user type'}), 403
    result = remove_user(user_id)
    return jsonify({'deleted_count': result.deleted_count})


# Only admins can list all doctors
@users_bp.route('/doctors', methods=['GET'])
@jwt_required
@role_required('admin')
def get_doctors():
    doctors = [user for user in get_all_users() if user.get('type') == 'doctor']
    for user in doctors:
        user['_id'] = str(user['_id'])
        user.pop('password_hash', None)
    return jsonify(doctors)


# Only admins can list all admins
@users_bp.route('/admins', methods=['GET'])
@jwt_required
@role_required('admin')
def get_admins():
    admins = [user for user in get_all_users() if user.get('type') == 'admin']
    for user in admins:
        user['_id'] = str(user['_id'])
        user.pop('password_hash', None)
    return jsonify(admins)

# Doctors can list their own patients
@users_bp.route('/patients', methods=['GET'])
@jwt_required
@role_required('doctor')
def get_patients():
    patients = [user for user in get_all_users() if user.get('type') == 'patient' and str(user.get('doctor_id')) == str(request.user.get('user_id'))]
    for user in patients:
        user['_id'] = str(user['_id'])
        user.pop('password_hash', None)
    return jsonify(patients)
