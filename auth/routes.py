from flask import Blueprint, request, jsonify
from .utils import hash_password, verify_password, generate_jwt
import json
from pathlib import Path

auth_bp = Blueprint("auth", __name__)
USERS_FILE = Path("storage/users.json")

def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    users = load_users()
    if data["username"] in users:
        return jsonify({"error": "User exists"}), 400
    users[data["username"]] = {
        "password": hash_password(data["password"]),
        "role": "user"
    }
    USERS_FILE.write_text(json.dumps(users, indent=2))
    return jsonify({"message": "Registered"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    users = load_users()
    user = users.get(data["username"])
    if not user or not verify_password(data["password"], user["password"]):
        return jsonify({"error": "Invalid credentials"}), 401
    token = generate_jwt({"username": data["username"], "role": user["role"]})
    return jsonify({"token": token})
