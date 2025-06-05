from flask import Blueprint, request, send_file, jsonify
import os

stream_bp = Blueprint("stream", __name__)

@stream_bp.route("/test", methods=["GET"])
def test_stream():
    return jsonify({"message": "Stream module active!"})
