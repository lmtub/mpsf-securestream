from flask import Blueprint, request, jsonify, redirect, url_for
import os
from werkzeug.utils import secure_filename
from crypto.aes_engine import encrypt_file, generate_aes_key
import base64
import json
from datetime import datetime
from auth.utils import decode_jwt
creator_bp = Blueprint("creator", __name__)

UPLOAD_DIR = os.path.join("storage", "encrypted_media")
KEY_FILE = os.path.join("storage", "encrypted_keys.json")
USER_CONTENT_FILE = os.path.join("storage", "creator_contents.json")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@creator_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join("tmp", filename)
    os.makedirs("tmp", exist_ok=True)
    file.save(input_path)

    key = generate_aes_key()
    output_path = os.path.join(UPLOAD_DIR, "enc_" + filename)
    encrypt_info = encrypt_file(input_path, output_path, key)

    with open(KEY_FILE, "r") as f:
        keys_data = json.load(f) if os.path.getsize(KEY_FILE) > 0 else {}
    keys_data["enc_" + filename] = base64.b64encode(key).decode()
    with open(KEY_FILE, "w") as f:
        json.dump(keys_data, f, indent=2)

    token = request.cookies.get("token")
    username = "unknown"
    if token:
        payload = decode_jwt(token)
        if payload:
            username = payload.get("username", "unknown")

    content_data = {}
    if os.path.exists(USER_CONTENT_FILE):
        with open(USER_CONTENT_FILE, "r") as f:
            content_data = json.load(f)
    if username not in content_data:
        content_data[username] = []
    content_data[username].append({
    "filename": filename,
    "uploaded_at": datetime.now().isoformat(),
    "status": "pending",  # Thêm trường này
    "access": None        # Chưa có quyền truy cập
    })
    with open(USER_CONTENT_FILE, "w") as f:
        json.dump(content_data, f)

    return redirect(url_for("auth.dashboard"))

@creator_bp.route("/my-content", methods=["GET"])
def my_content():
    username = request.headers.get("X-Username", "unknown")
    if os.path.exists(USER_CONTENT_FILE):
        with open(USER_CONTENT_FILE, "r") as f:
            content_data = json.load(f)
        return jsonify(content_data.get(username, []))
    return jsonify([])

@creator_bp.route("/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    filepath = os.path.join(UPLOAD_DIR, "enc_" + filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    with open(KEY_FILE, "r") as f:
        keys_data = json.load(f)
    keys_data.pop(filename, None)
    with open(KEY_FILE, "w") as f:
        json.dump(keys_data, f)
    return jsonify({"message": f"Deleted {filename}"})
