from flask import Blueprint, request, jsonify, redirect, url_for
import os
import json
from datetime import datetime

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/approve/<filename>", methods=["POST"])
def approve_content(filename):
    access = request.form.get("access")  # "public" hoặc "premium"
    approved_by = request.form.get("approved_by")
    contents_path = os.path.join("storage", "creator_contents.json")
    if os.path.exists(contents_path):
        with open(contents_path, "r") as f:
            contents = json.load(f)
        for user_files in contents.values():
            for item in user_files:
                if item["filename"] == filename and item.get("status") == "pending":
                    item["status"] = "approved"
                    item["access"] = access
                    item["approved_by"] = approved_by
        with open(contents_path, "w") as f:
            json.dump(contents, f, indent=2)
    return redirect(url_for("auth.dashboard"))
