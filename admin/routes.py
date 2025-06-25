from flask import Blueprint, request, jsonify, redirect, url_for
import os
import json
from datetime import datetime

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/approve/<storage_name>", methods=["POST"])
def approve_content(storage_name):
    access = request.form.get("access")  # "public" hoặc "premium"
    approved_by = request.form.get("approved_by")

    contents_path = os.path.join("storage", "creator_contents.json")
    if not os.path.exists(contents_path):
        return jsonify({"error": "Không tìm thấy dữ liệu nội dung"}), 404

    with open(contents_path, "r") as f:
        contents = json.load(f)

    # Duyệt từng user và từng file để cập nhật
    for user_files in contents.values():
        for item in user_files:
            if item["storage_name"] == storage_name and item.get("status") == "pending":
                item["status"] = "approved"
                item["access"] = access
                item["approved_by"] = approved_by

    with open(contents_path, "w") as f:
        json.dump(contents, f, indent=2, ensure_ascii=False)

    return redirect(url_for("auth.dashboard"))
