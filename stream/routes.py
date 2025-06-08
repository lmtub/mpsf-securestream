from flask import Blueprint, request, send_file, jsonify, current_app, after_this_request
import os
import json
import base64
import jwt
from datetime import datetime  
from flask import render_template
from crypto.utils import encrypt_key_with_master
from crypto.aes_engine import encrypt_file, generate_aes_key, decrypt_file, decrypt_key_with_master

import mimetypes

def get_mimetype(filename):
    mimetype, _ = mimetypes.guess_type(filename)
    return mimetype or "application/octet-stream"

stream_bp = Blueprint("stream", __name__)

SECRET_KEY = "mpsf-secret-key"  # Thay bằng secret thực tế của bạn

def log_access(username: str, filename: str):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "access.log"), "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {username} accessed {filename}\n")

def verify_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception:
        return None

@stream_bp.route("/test", methods=["GET"])
def test_stream():
    return jsonify({"message": "Stream module active!"})

@stream_bp.route("/encrypt", methods=["POST"])
def encrypt_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    input_path = os.path.join("tmp", file.filename)
    os.makedirs("tmp", exist_ok=True)
    file.save(input_path)

    key = generate_aes_key()
    output_path = os.path.join("tmp", "enc_" + file.filename)
    encrypt_info = encrypt_file(input_path, output_path, key)

    encrypted_key_str = encrypt_key_with_master(key)

    # Lưu key vào encrypted_keys.json (ví dụ đơn giản, thực tế nên mã hóa key)
    keys_path = os.path.join("tmp", "encrypted_keys.json")
    keys_data = {}
    if os.path.exists(keys_path):
        with open(keys_path, "r") as f:
            keys_data = json.load(f)
    keys_data[file.filename] = base64.b64encode(key).decode()
    with open(keys_path, "w") as f:
        json.dump(keys_data, f)

    with open(output_path, "rb") as f:
        encrypted_data = f.read()

    return jsonify({
        "encrypted_file": encrypted_data.hex(),
        "key": key.hex(),
        "nonce": encrypt_info["nonce"],
        "tag": encrypt_info["tag"]
    })

@stream_bp.route("/download/<filename>", methods=["GET"])
def download_decrypt(filename):
    # Lấy JWT từ header hoặc cookie
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = request.cookies.get("token")

    if not token:
        return jsonify({"error": "Missing or invalid JWT"}), 401

    payload = verify_jwt(token)
    if not payload:
        return jsonify({"error": "Invalid JWT"}), 401

    user_role = payload.get("role", "user") 
    username = payload.get("username", "unknown")

    # Kiểm tra quyền truy cập từ creator_contents.json
    access_file = os.path.join("storage", "creator_contents.json")
    file_access = None

    if os.path.exists(access_file):
        with open(access_file, "r", encoding="utf-8") as f:
            creator_data = json.load(f)
            for creator, uploads in creator_data.items():
                for item in uploads:
                    if item.get("filename") == filename:
                        file_access = item.get("access", "private")

    # Quy định phân quyền truy cập
    if file_access == "public":
        pass  # ai cũng truy cập được
    elif file_access == "premium":
        if user_role not in ["premium", "admin"]:
            return jsonify({"error": "Chỉ tài khoản premium hoặc admin mới xem được file này."}), 403
    elif file_access is None:
        return jsonify({"error": "Không tìm thấy quyền truy cập file."}), 404
    else:
        return jsonify({"error": "Bạn không có quyền truy cập file này."}), 403

    # Đọc AES key đã mã hóa
    key_path = os.path.join("storage", "encrypted_keys.json")
    if not os.path.exists(key_path):
        return jsonify({"error": "Key file not found"}), 404

    with open(key_path, "r") as f:
        keys_data = json.load(f)

    key_id = "enc_" + filename
    if key_id not in keys_data:
        return jsonify({"error": f"Key for file '{key_id}' not found"}), 404

    encrypted_key_str = keys_data[key_id]
    key = decrypt_key_with_master(encrypted_key_str)

    # Giải mã file
    enc_path = os.path.join("storage", "encrypted_media", "enc_" + filename)
    dec_path = os.path.join(current_app.root_path, "tmp", "dec_" + filename)

    os.makedirs("tmp", exist_ok=True)
    print(f"[DEBUG] Tuyệt đối dec_path = {dec_path}")
    if not os.path.exists(enc_path):
        return jsonify({"error": "Encrypted file not found"}), 404

    try:
        decrypt_file(enc_path, dec_path, key)
    except Exception as e:
        return jsonify({"error": f"Decryption failed: {str(e)}"}), 500

    if not os.path.exists(dec_path):
        return jsonify({"error": "Decryption failed or output file missing"}), 500
    
    # Ghi log và gửi file
    log_access(username, filename)
    @after_this_request
    def cleanup(response):
        try:
            if os.path.exists(dec_path):
                os.remove(dec_path)
        except Exception:
            pass
        return response
    return send_file(dec_path, mimetype=get_mimetype(filename), as_attachment=False)

@stream_bp.route("/play/<filename>")
def play_video(filename):
    return render_template("player.html", filename=filename)