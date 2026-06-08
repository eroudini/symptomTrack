from flask import Blueprint, jsonify

logs_bp = Blueprint("logs", __name__)

@logs_bp.route("/", methods=["GET"])
def get_logs():
    return jsonify({
        "message": "Liste des symptômes",
        "logs": []
    })