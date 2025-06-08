from flask import Blueprint, request, jsonify, render_template, redirect, url_for, make_response
from .utils import hash_password, verify_password, generate_jwt, decode_jwt
import json
from pathlib import Path
import os
auth_bp = Blueprint("auth", __name__)
USERS_FILE = Path("storage/users.json")

def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

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

        # ✅ Tạo response và set cookie chứa JWT
        resp = make_response(redirect(url_for("auth.dashboard")))
        resp.set_cookie("token", token, httponly=True, secure=False, samesite="Strict", max_age=3600)
        return resp

    return render_template("login.html")
@auth_bp.route("/logout")
def logout():
    resp = redirect(url_for("auth.login"))
    resp.set_cookie("token", "", expires=0)
    return resp
@auth_bp.route("/dashboard")
def dashboard():
    token = request.cookies.get("token")  # Hoặc từ session
    if not token:
        return redirect(url_for("auth.login"))

    payload = decode_jwt(token)
    if not payload:
        return redirect(url_for("auth.login"))
    user_info = decode_jwt(token) if token else {}
    username = user_info.get("username", "unknown")
    role = user_info.get("role", "user")

    uploaded_files = []  # Luôn khởi tạo mặc định

    if role == "creator":
        contents_path = os.path.join("storage", "creator_contents.json")
        if os.path.exists(contents_path):
            with open(contents_path, "r") as f:
                contents = json.load(f)
            # Kiểm tra username có trong contents không
            if username in contents:
                uploaded_files = [item["filename"] for item in contents[username]]
            
    pending_files = []

    if role == "admin":
        contents_path = os.path.join("storage", "creator_contents.json")
        if os.path.exists(contents_path):
            with open(contents_path, "r") as f:
                contents = json.load(f)
            for user_files in contents.values():
                for item in user_files:
                    if item.get("status") == "pending":
                        pending_files.append(item["filename"])
    else:
        pending_files = None

    public_files = []
    premium_files = []
    contents_path = os.path.join("storage", "creator_contents.json")
    if os.path.exists(contents_path):
        with open(contents_path, "r") as f:
            contents = json.load(f)
        for user_files in contents.values():
            for item in user_files:
                if item.get("status") == "approved":
                    if item.get("access") == "public":
                        public_files.append(item["filename"])
                    elif item.get("access") == "premium":
                        premium_files.append(item["filename"])
    
    if role == "user":
        premium_files = []
    elif role != "premium":
        public_files = []
        premium_files = []


    return render_template(
        "dashboard.html",
        username=payload.get("username"),
        role=payload.get("role"),
        uploaded_files=uploaded_files,
        pending_files=pending_files,
        public_files=public_files,
        premium_files=premium_files
    )
@auth_bp.route("/play/<filename>")
def play_video(filename):
    return render_template("player.html", filename=filename)