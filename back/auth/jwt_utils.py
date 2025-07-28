import jwt
import datetime
from flask import current_app
import os
import dotenv
dotenv.load_dotenv('.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')  
ALGORITHM = os.getenv('ALGORITHM', 'HS256')

# Generate JWT token
def generate_token(user_id, role, expires_in=3600):
    payload = {
        'user_id': str(user_id),
        'role': role,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Decode and verify JWT token
def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
