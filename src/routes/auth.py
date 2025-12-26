from flask import Blueprint, request, jsonify, current_app
from src.services import auth as auth_service

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@bp.route("/register", methods=["POST"])
def register():
    session = current_app.session()
    result, status = auth_service.register(session, request.get_json())
    session.close()
    return jsonify(result), status

@bp.route("/login", methods=["POST"])
def login():
    session = current_app.session()
    result, status = auth_service.login(session, request.get_json())
    session.close()
    return jsonify(result), status

@bp.route("/change_password", methods=["POST"])
def change_password():
    session = current_app.session()
    result, status = auth_service.change_password(session, request.get_json())
    session.close()
    return jsonify(result), status
