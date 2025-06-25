from flask import Blueprint, request, send_file, jsonify, current_app, render_template, g
import os
import json
import base64
import jwt
from datetime import datetime  
import mimetypes
from dotenv import load_dotenv
from crypto.aes_engine import encrypt_file, generate_aes_key, decrypt_file, decrypt_key_with_master, encrypt_key_with_master
from functools import wraps

load_dotenv()

stream_bp = Blueprint("stream", __name__)

SECRET_KEY = os.environ.get("SECRET_KEY")

# Giúp Flask đoán định dạng file trả về
def get_mimetype(filename):
    mimetype, _ = mimetypes.guess_type(filename)
    return mimetype or "application/octet-stream"

# Middleware kiểm tra JWT
def require_jwt(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token") or None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Thiếu hoặc sai JWT"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except Exception:
            return jsonify({"error": "JWT không hợp lệ"}), 401

        g.payload = payload
        return f(*args, **kwargs)
    return decorated

# Ghi log truy cập file
def log_access(username, storage_name):
    os.makedirs("logs", exist_ok=True)
    with open("logs/access.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {username} accessed {storage_name}\n")

# Test module
@stream_bp.route("/test")
def test_stream():
    return jsonify({"message": "Stream module active!"})

# Trang phát video, chỉ nhận storage_name
@stream_bp.route("/play/<storage_name>")
@require_jwt
def play_video(storage_name):
    return render_template("player.html", storage_name=storage_name)

# Lấy Key giải mã video, ẩn hoàn toàn tên thật
@stream_bp.route("/api/get_key/<storage_name>")
@require_jwt
def get_key(storage_name):
    role = g.payload.get("role", "user")

    contents_path = os.path.join("storage", "creator_contents.json")
    if not os.path.exists(contents_path):
        return jsonify({"error": "Không tìm thấy dữ liệu"}), 404

    with open(contents_path, "r") as f:
        contents = json.load(f)

    file_access = None
    file_status = None
    for uploads in contents.values():
        for item in uploads:
            if item["storage_name"] == storage_name:
                file_access = item.get("access")
                file_status = item.get("status")

    if file_status != "approved":
        return jsonify({"error": "Nội dung chưa được duyệt"}), 403
    if file_access == "premium" and role not in ["premium", "admin"]:
        return jsonify({"error": "Chỉ tài khoản premium hoặc admin có quyền"}), 403
    if file_access not in ["public", "premium"]:
        return jsonify({"error": "Bạn không có quyền truy cập"}), 403

    key_path = os.path.join("storage", "encrypted_keys.json")
    if not os.path.exists(key_path):
        return jsonify({"error": "Không tìm thấy khoá"}), 404

    with open(key_path, "r") as f:
        keys_data = json.load(f)

    if storage_name not in keys_data:
        return jsonify({"error": "Key không tồn tại"}), 404

    key_info = keys_data[storage_name]
    return jsonify({
        "key_id": key_info["key_id"],
        "key": key_info["key"]
    })

# Tải và giải mã video, không lộ tên thật
@stream_bp.route("/download/<storage_name>")
@require_jwt
def download_decrypt(storage_name):
    payload = g.payload
    username = payload.get("username", "unknown")
    role = payload.get("role", "user")

    contents_path = os.path.join("storage", "creator_contents.json")
    file_access = None

    if os.path.exists(contents_path):
        with open(contents_path, "r", encoding="utf-8") as f:
            contents = json.load(f)
            for uploads in contents.values():
                for item in uploads:
                    if item.get("storage_name") == storage_name:
                        file_access = item.get("access", "private")

    if file_access == "public":
        pass
    elif file_access == "premium":
        if role not in ["premium", "admin"]:
            return jsonify({"error": "Chỉ premium hoặc admin được phép"}), 403
    elif file_access is None:
        return jsonify({"error": "Không tìm thấy quyền truy cập file"}), 404
    else:
        return jsonify({"error": "Bạn không có quyền truy cập"}), 403

    key_path = os.path.join("storage", "encrypted_keys.json")
    if not os.path.exists(key_path):
        return jsonify({"error": "Key không tồn tại"}), 404

    with open(key_path, "r") as f:
        keys_data = json.load(f)

    if storage_name not in keys_data:
        return jsonify({"error": "Không tìm thấy key cho file này"}), 404

    key_info = keys_data[storage_name]
    key = decrypt_key_with_master(key_info["key"])

    enc_path = os.path.join("storage", "encrypted_media", f"enc_{storage_name}")
    dec_path = os.path.join(current_app.root_path, "tmp", f"dec_{storage_name}")

    os.makedirs("tmp", exist_ok=True)
    if not os.path.exists(enc_path):
        return jsonify({"error": "File mã hoá không tồn tại"}), 404

    try:
        decrypt_file(enc_path, dec_path, key)
    except Exception as e:
        return jsonify({"error": f"Giải mã thất bại: {str(e)}"}), 500

    log_access(username, storage_name)
    return send_file(dec_path, mimetype=get_mimetype(storage_name), as_attachment=False)
