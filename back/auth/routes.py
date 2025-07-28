from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from controllers.user_controller import find_user_by_email
from .jwt_utils import generate_token
from controllers.user_controller import modify_user

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = find_user_by_email(email)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    modify_user(str(user['_id']), {'status': True})
    token = generate_token(user['_id'], user['type'])
    return jsonify({'token': token, 'role': user['type'], 'email': user['email']})

@auth_bp.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    email = data.get('email')
    user = find_user_by_email(email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    modify_user(str(user['_id']), {'status': False})
    return jsonify({'message': 'Logged out successfully'})
