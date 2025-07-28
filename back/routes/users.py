from flask import Blueprint, request, jsonify
from controllers.user_controller import register_user, find_user_by_id, modify_user, remove_user
from werkzeug.security import generate_password_hash
from controllers.user_controller import get_all_users

users_bp = Blueprint('users_bp', __name__, url_prefix='/api/users')

@users_bp.route('', methods=['POST'])
def create_user():
    user_data = request.get_json()
    if 'password' in user_data:
        user_data['password_hash'] = generate_password_hash(user_data.pop('password'))
    result = register_user(user_data)
    return jsonify({'inserted_id': str(result.inserted_id)})

@users_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    user = find_user_by_id(user_id)
    if user:
        user['_id'] = str(user['_id'])
        user.pop('password_hash', None)
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

@users_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    update = request.get_json()
    result = modify_user(user_id, update)
    return jsonify({'modified_count': result.modified_count})

@users_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    result = remove_user(user_id)
    return jsonify({'deleted_count': result.deleted_count})

@users_bp.route('/doctors', methods=['GET'])
def get_doctors():
    doctors = [user for user in get_all_users() if user['type'] == 'doctor']
    for user in doctors:
        user['_id'] = str(user['_id'])
        user.pop('password_hash', None)
    return jsonify(doctors)

@users_bp.route('/admins', methods=['GET'])
def get_admins():
    admins = [user for user in get_all_users() if user['type'] == 'admin']
    for user in admins:
        user['_id'] = str(user['_id'])
        user.pop('password_hash', None)
    return jsonify(admins)
