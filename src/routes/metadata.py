from flask import Blueprint, request, jsonify, current_app
from src.services import metadata as metadata_service

bp = Blueprint("metadata", __name__, url_prefix="/api/metadata")

@bp.route("/listar", methods=["GET"])
def listar_metadata():
    solo_protegidas = request.args.get("protegida") == "true"
    metadata_col = current_app.mongo["metadata"]
    result, status = metadata_service.listar_metadata(metadata_col, solo_protegidas)
    return jsonify(result), status
