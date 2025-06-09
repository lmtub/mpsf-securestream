from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, hashed):
    return check_password_hash(hashed, password)

def generate_jwt(payload, exp_minutes=30):
    payload["exp"] = datetime.utcnow() + timedelta(minutes=exp_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
