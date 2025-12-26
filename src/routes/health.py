from flask import Blueprint, jsonify
from src.services import health as health_service

bp = Blueprint("health", __name__)

@bp.route("/", methods=["GET"])
def index():
    result, status = health_service.check()
    return jsonify(result), status
