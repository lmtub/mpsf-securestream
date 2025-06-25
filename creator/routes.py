from flask import Blueprint, request, jsonify, redirect, url_for
import os
import subprocess
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from auth.utils import decode_jwt
import random
import string

creator_bp = Blueprint("creator", __name__)

# Cấu hình
ALLOWED_EXTENSIONS = {"mp4", "mp3"}
UPLOAD_DIR = os.path.join("storage", "encrypted_media")
KEY_FILE = os.path.join("storage", "encrypted_keys.json")
USER_CONTENT_FILE = os.path.join("storage", "creator_contents.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Hàm kiểm tra định dạng file hợp lệ
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Hàm tạo chuỗi ngẫu nhiên để ẩn tên file
def random_string(length=12):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# API Creator upload file
@creator_bp.route("/upload", methods=["POST"])
def upload_file():
    try:
        # Kiểm tra file hợp lệ
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Định dạng file không hợp lệ"}), 400

        # Xử lý tên file
        original_filename = secure_filename(file.filename)  # Tên thật, chỉ lưu cho quản lý
        storage_name = random_string()  # Tên ngẫu nhiên để ẩn file trên server

        input_path = os.path.join("tmp", original_filename)
        os.makedirs("tmp", exist_ok=True)
        file.save(input_path)

        if not os.path.exists(input_path):
            return jsonify({"error": "File tạm không lưu được"}), 500

        # Tạo key_id và key ngẫu nhiên
        key_id = os.urandom(16).hex()
        key = os.urandom(16).hex()

        # Chuẩn bị lệnh Packager, ẩn tên file output
        output_mpd = os.path.join(UPLOAD_DIR, f"{storage_name}_stream.mpd")
        packager_cmd = r"C:\ffmpeg\bin\packager.exe"

        cmd = [
            packager_cmd,
            f"in={input_path},stream=audio,output={UPLOAD_DIR}/{storage_name}_audio.mp4",
            f"in={input_path},stream=video,output={UPLOAD_DIR}/{storage_name}_video.mp4",
            "--enable_raw_key_encryption",
            "--keys", f"label=:key_id={key_id}:key={key}",
            f"--mpd_output={output_mpd}"
        ]

        subprocess.run(cmd, check=True)
        os.remove(input_path)

        # Lưu key vào file, theo tên ngẫu nhiên
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "r") as f:
                keys_data = json.load(f)
        else:
            keys_data = {}

        keys_data[storage_name] = {
            "key_id": key_id,
            "key": key,
            "original_filename": original_filename
        }

        with open(KEY_FILE, "w") as f:
            json.dump(keys_data, f, indent=2)

        # Lưu thông tin nội dung vào file quản lý
        token = request.cookies.get("token")
        username = "unknown"
        if token:
            payload = decode_jwt(token)
            if payload:
                username = payload.get("username", "unknown")

        if os.path.exists(USER_CONTENT_FILE):
            with open(USER_CONTENT_FILE, "r") as f:
                content_data = json.load(f)
        else:
            content_data = {}

        if username not in content_data:
            content_data[username] = []

        content_data[username].append({
            "display_name": original_filename,  # Tên hiển thị trên dashboard
            "storage_name": storage_name,       # Tên thực tế dùng phát video
            "uploaded_at": datetime.now().isoformat(),
            "status": "pending",
            "access": None
        })

        with open(USER_CONTENT_FILE, "w") as f:
            json.dump(content_data, f, indent=2)

        return redirect(url_for("auth.dashboard"))

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Packager failed: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500
