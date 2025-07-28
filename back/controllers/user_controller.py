from models.user_model import create_user, get_user_by_email, get_user_by_id, update_user, delete_user, find_all_users

# Business logic for users
def register_user(user_data):
    return create_user(user_data)

def find_user_by_email(email):
    return get_user_by_email(email)

def find_user_by_id(user_id):
    return get_user_by_id(user_id)

def modify_user(user_id, update):
    return update_user(user_id, update)

def remove_user(user_id):
    return delete_user(user_id)

def get_all_users():
    return find_all_users()