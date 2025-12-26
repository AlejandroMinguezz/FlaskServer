from flask import Blueprint, request, jsonify, send_from_directory, current_app
from src.services import files as file_service
from src.services.token import verify_token
from src.ia.ocr.ocr import ejecutar_ocr
from src.ia.clasificadores.beto.inferencia import ejecutar_beto

bp = Blueprint("files", __name__, url_prefix="/api/files")


@bp.route("/list", methods=["GET"])
def list_files():
    result = file_service.list_files()
    return jsonify(result)


@bp.route("/upload", methods=["POST"])
def upload_file():
    ia_activada = request.args.get("ia", "false").lower() == "true"
    file = request.files.get("file")
    folder = request.form.get("folder", "").strip()
    user = request.form.get("user", "unknown")

    metadata_col = current_app.mongo["metadata"]

    result, status = file_service.upload_file(
        file=file,
        folder=folder,
        user=user,
        metadata_col=metadata_col,
        ia_activa=ia_activada,
        ocr_fn=ejecutar_ocr if ia_activada else None,
        beto_fn=ejecutar_beto if ia_activada else None
    )
    return jsonify(result), status

@bp.route("/download/<path:filepath>", methods=["GET"])
def download_file(filepath):
    ok, directory, filename = file_service.download_file(filepath)
    if ok:
        return send_from_directory(directory, filename, as_attachment=True)
    return jsonify({"error": "Archivo no encontrado"}), 404

@bp.route("/delete/<path:ruta>", methods=["DELETE"])
def delete_element(ruta):
    metadata_col = current_app.mongo["metadata"]

    # Verificar si la carpeta es protegida
    username = request.args.get("username", "")
    parts = ruta.rsplit('/', 1)
    if len(parts) == 2:
        relative_path = "/" + parts[0]
        filename = parts[1]
    else:
        relative_path = "/"
        filename = parts[0]

    # Buscar si el elemento está protegido
    elemento = metadata_col.find_one({"filename": filename, "relative_path": relative_path})
    if elemento and elemento.get("protegida"):
        # Solo los admins pueden eliminar carpetas protegidas
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = verify_token(token)
        if not payload or (payload.get("role") != 1 and payload.get("role") != "admin"):
            return jsonify({"error": "Solo los administradores pueden eliminar carpetas protegidas"}), 403

    result, status = file_service.delete_element(ruta, metadata_col)
    return jsonify(result), status

@bp.route("/create_folder", methods=["POST"])
def create_folder():
    data = request.get_json()
    # Aceptar tanto 'ruta' como 'folder_path' para compatibilidad
    ruta = data.get("ruta") or data.get("folder_path")
    protegida = data.get("protegida", False)
    # Aceptar tanto 'user' como 'username' para compatibilidad
    user = data.get("user") or data.get("username") or "unknown"

    if not ruta:
        return jsonify({"error": "Se requiere 'ruta' o 'folder_path'"}), 400

    # Solo los admins pueden crear carpetas protegidas
    if protegida:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = verify_token(token)
        if not payload or (payload.get("role") != 1 and payload.get("role") != "admin"):
            return jsonify({"error": "Solo los administradores pueden crear carpetas protegidas"}), 403

    metadata_col = current_app.mongo["metadata"]
    result, status = file_service.create_folder(ruta, protegida, user, metadata_col)
    return jsonify(result), status

@bp.route("/create_file", methods=["POST"])
def create_file():
    data = request.get_json()
    ruta = data.get("ruta")
    user = data.get("user", "unknown")

    metadata_col = current_app.mongo["metadata"]
    result, status = file_service.create_file(ruta, user, metadata_col)
    return jsonify(result), status

@bp.route("/move", methods=["POST"])
def move_file():
    data = request.get_json()
    origen_rel = data.get("origen")
    destino_rel = data.get("destino")
    metadata_col = current_app.mongo["metadata"]
    result, status = file_service.move_file(origen_rel, destino_rel, metadata_col)
    return jsonify(result), status
