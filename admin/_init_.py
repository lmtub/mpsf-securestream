from flask import Blueprint, jsonify, request
import os
import json

admin_bp = Blueprint("admin", __name__)

USERS_FILE = os.path.join("storage", "users.json")
LOG_FILE = os.path.join("logs", "access.log")
CREATOR_CONTENT_FILE = os.path.join("storage", "creator_contents.json")

@admin_bp.route("/admin/users", methods=["GET"])
def list_users():
    if not os.path.exists(USERS_FILE):
        return jsonify([])
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
    return jsonify(users)

@admin_bp.route("/admin/logs", methods=["GET"])
def view_logs():
    if not os.path.exists(LOG_FILE):
        return jsonify({"log": "(empty)"})
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    return jsonify({"log": content})

@admin_bp.route("/admin/delete-user/<username>", methods=["DELETE"])
def delete_user(username):
    if not os.path.exists(USERS_FILE):
        return jsonify({"error": "Users file not found"}), 404
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
    if username in users:
        del users[username]
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)
        return jsonify({"message": f"Deleted user '{username}'"})
    else:
        return jsonify({"error": "User not found"}), 404

@admin_bp.route("/admin/approve/<filename>", methods=["POST"])
def approve_content(filename):
    # Simulate approval by marking content "approved" in a dummy list
    if not os.path.exists(CREATOR_CONTENT_FILE):
        return jsonify({"error": "No content to approve"}), 404
    with open(CREATOR_CONTENT_FILE, "r") as f:
        data = json.load(f)
    updated = False
    for creator, uploads in data.items():
        for file in uploads:
            if file["filename"] == filename:
                file["approved"] = True
                updated = True
    if updated:
        with open(CREATOR_CONTENT_FILE, "w") as f:
            json.dump(data, f)
        return jsonify({"message": f"Approved content: {filename}"})
    return jsonify({"error": "File not found in uploads"}), 404