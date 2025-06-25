from flask import Blueprint, request, jsonify, render_template, redirect, url_for, make_response
from .utils import hash_password, verify_password, generate_jwt, decode_jwt
import json
from pathlib import Path
import os

auth_bp = Blueprint("auth", __name__)

USERS_FILE = Path("storage/users.json")

# Hàm load danh sách user từ file
def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

# Đăng ký tài khoản
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users = load_users()
        
        if username in users:
            return render_template("register.html", error="User exists")
        
        users[username] = {
            "password": hash_password(password),
            "role": "user"
        }
        USERS_FILE.write_text(json.dumps(users, indent=2))
        return redirect(url_for("auth.login"))

    return render_template("register.html")

# Đăng nhập
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users = load_users()
        
        user = users.get(username)
        if not user or not verify_password(password, user["password"]):
            return render_template("login.html", error="Invalid credentials")

        token = generate_jwt({"username": username, "role": user["role"]})

        resp = make_response(redirect(url_for("auth.dashboard")))
        resp.set_cookie("token", token, httponly=True, secure=True, samesite="Strict", max_age=3600)
        return resp

    return render_template("login.html")

# Đăng xuất
@auth_bp.route("/logout")
def logout():
    resp = redirect(url_for("auth.login"))
    resp.set_cookie("token", "", expires=0)
    return resp

# Trang Dashboard
@auth_bp.route("/dashboard")
def dashboard():
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("auth.login"))

    payload = decode_jwt(token)
    if not payload:
        return redirect(url_for("auth.login"))

    username = payload.get("username", "unknown")
    role = payload.get("role", "user")

    uploaded_files = []
    pending_files = []
    public_files = []
    premium_files = []

    contents_path = os.path.join("storage", "creator_contents.json")
    if os.path.exists(contents_path):
        with open(contents_path, "r") as f:
            contents = json.load(f)

        # Creator xem danh sách file của mình
        if role == "creator" and username in contents:
            uploaded_files = [
                {
                    "display_name": item["display_name"],
                    "storage_name": item["storage_name"],
                    "status": item["status"],
                    "access": item["access"]
                }
                for item in contents[username]
            ]

        # Admin duyệt video
        if role == "admin":
            for user_files in contents.values():
                for item in user_files:
                    if item.get("status") == "pending":
                        pending_files.append({
                            "display_name": item["display_name"],
                            "storage_name": item["storage_name"]
                        })

        # Phân quyền xem video công khai hoặc premium
        for user_files in contents.values():
            for item in user_files:
                if item.get("status") == "approved":
                    video_info = {
                        "display_name": item["display_name"],
                        "storage_name": item["storage_name"]
                    }
                    if item.get("access") == "public":
                        public_files.append(video_info)
                    elif item.get("access") == "premium":
                        premium_files.append(video_info)

    # Nếu user thường chỉ xem được public
    if role == "user":
        premium_files = []
    # Nếu không phải premium, ẩn hết
    elif role != "premium":
        public_files = []
        premium_files = []

    return render_template(
        "dashboard.html",
        username=username,
        role=role,
        uploaded_files=uploaded_files,
        pending_files=pending_files if role == "admin" else None,
        public_files=public_files,
        premium_files=premium_files
    )

# Trang play video, chỉ truyền storage_name
@auth_bp.route("/play/<storage_name>")
def play_video(storage_name):
    return render_template("player.html", storage_name=storage_name)
