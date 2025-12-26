import os
import uuid
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, current_app
from src.models import FolderTemplate, Group
from src.services.token import verify_token

bp = Blueprint("folder_structure", __name__, url_prefix="/admin/folder-structure")

# Usar la misma ruta que el explorador de archivos
BASE_STORAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../storage/files"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", BASE_STORAGE_PATH)

def _auth():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        token = request.args.get("token", "")
    if not token:
        return False
    payload = verify_token(token)
    if not payload:
        return False
    role = payload.get("role")
    return role == "admin" or role == 1 or role == "1"

@bp.before_request
def guard():
    if request.method == "OPTIONS":
        # Permitir peticiones OPTIONS para CORS preflight
        return jsonify({"status": "ok"}), 200
    if not _auth():
        return jsonify({"error": "unauthorized"}), 401

@bp.get("/")
def get_folder_structure():
    """Obtener toda la estructura de carpetas"""
    session = current_app.session()
    group_id = request.args.get("group_id")

    # Obtener carpetas raíz (sin parent)
    query = session.query(FolderTemplate).filter(FolderTemplate.parent_id == None)

    if group_id:
        query = query.filter(FolderTemplate.group_id == group_id)

    root_folders = query.order_by(FolderTemplate.order).all()
    print(f"[DirectIA Backend] Carpetas raíz encontradas: {len(root_folders)}")
    for folder in root_folders:
        print(f"  - {folder.name} (id: {folder.id}, group_id: {folder.group_id}, children: {len(folder.children)})")

    def folder_to_dict(folder):
        return {
            "id": folder.id,
            "name": folder.name,
            "description": folder.description,
            "icon": folder.icon,
            "parent_id": folder.parent_id,
            "order": folder.order,
            "protected": folder.protected,
            "group_id": folder.group_id,
            "children": [folder_to_dict(child) for child in sorted(folder.children, key=lambda x: x.order)]
        }

    structure = [folder_to_dict(folder) for folder in root_folders]
    print(f"[DirectIA Backend] Estructura JSON devuelta: {len(structure)} carpetas raíz")

    return jsonify({"folders": structure})

@bp.post("/")
def create_folder_template():
    """Crear una carpeta en la estructura"""
    session = current_app.session()
    data = request.get_json() or {}

    print(f"[DirectIA Backend] Creando carpeta con datos: {data}")

    if "name" not in data:
        return jsonify({"error": "El nombre es requerido"}), 400

    folder = FolderTemplate(
        name=data["name"],
        description=data.get("description", ""),
        icon=data.get("icon", "folder"),
        parent_id=data.get("parent_id"),
        order=data.get("order", 0),
        protected=data.get("protected", True),
        group_id=data.get("group_id")
    )

    session.add(folder)
    session.commit()

    print(f"[DirectIA Backend] Carpeta creada: {folder.name} (id: {folder.id}, parent_id: {folder.parent_id}, group_id: {folder.group_id})")

    return jsonify({
        "ok": True,
        "msg": "Carpeta creada en la estructura",
        "folder": {
            "id": folder.id,
            "name": folder.name,
            "description": folder.description,
            "icon": folder.icon,
            "parent_id": folder.parent_id,
            "order": folder.order,
            "protected": folder.protected,
            "group_id": folder.group_id
        }
    })

@bp.put("/<int:folder_id>")
def update_folder_template(folder_id):
    """Actualizar una carpeta de la estructura"""
    session = current_app.session()
    folder = session.query(FolderTemplate).get(folder_id)

    if not folder:
        return jsonify({"error": "Carpeta no encontrada"}), 404

    data = request.get_json() or {}

    if "name" in data:
        folder.name = data["name"]
    if "description" in data:
        folder.description = data["description"]
    if "icon" in data:
        folder.icon = data["icon"]
    if "order" in data:
        folder.order = data["order"]
    if "protected" in data:
        folder.protected = data["protected"]
    if "group_id" in data:
        folder.group_id = data["group_id"]

    session.commit()

    return jsonify({"ok": True, "msg": "Carpeta actualizada"})

@bp.delete("/<int:folder_id>")
def delete_folder_template(folder_id):
    """Eliminar una carpeta de la estructura"""
    session = current_app.session()
    folder = session.query(FolderTemplate).get(folder_id)

    if not folder:
        return jsonify({"error": "Carpeta no encontrada"}), 404

    session.delete(folder)
    session.commit()

    return jsonify({"ok": True, "msg": "Carpeta eliminada de la estructura"})

@bp.post("/apply/<int:group_id>")
def apply_folder_structure(group_id):
    """Aplicar la estructura de carpetas físicamente en el sistema de archivos"""
    session = current_app.session()
    metadata_col = current_app.mongo.metadata

    # Obtener usuario del token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = verify_token(token)
    user = payload.get("username", "admin") if payload else "admin"

    print(f"[DirectIA Backend] Aplicando estructura para grupo {group_id}")
    print(f"[DirectIA Backend] Ruta base de almacenamiento: {UPLOAD_DIR}")
    print(f"[DirectIA Backend] Usuario: {user}")

    # Asegurar que el directorio base existe
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        print(f"[DirectIA Backend] Directorio base creado: {UPLOAD_DIR}")

    # Verificar que el grupo existe
    group = session.query(Group).get(group_id)
    if not group:
        print(f"[DirectIA Backend] Error: Grupo {group_id} no encontrado")
        return jsonify({"error": "Grupo no encontrado"}), 404

    print(f"[DirectIA Backend] Grupo encontrado: {group.name}")

    # Obtener estructura de carpetas para este grupo (específicas del grupo + globales)
    folders = session.query(FolderTemplate).filter(
        (FolderTemplate.group_id == group_id) | (FolderTemplate.group_id == None)
    ).order_by(FolderTemplate.order).all()

    print(f"[DirectIA Backend] Carpetas a aplicar: {len(folders)} total")
    for folder in folders:
        group_label = f"grupo {folder.group_id}" if folder.group_id else "global"
        print(f"  - {folder.name} ({group_label}, parent_id: {folder.parent_id}, protected: {folder.protected})")

    created_folders = []
    errors = []

    def create_physical_folder(folder, parent_path=""):
        try:
            # Construir ruta
            folder_path = os.path.join(parent_path, folder.name) if parent_path else folder.name
            full_path = os.path.join(UPLOAD_DIR, folder_path)
            relative_path = "/" + os.path.dirname(folder_path).replace("\\", "/") if parent_path else "/"

            # Verificar si ya existe en MongoDB
            existing_metadata = metadata_col.find_one({
                "filename": folder.name,
                "relative_path": relative_path,
                "tipo": "carpeta"
            })

            # Crear carpeta física si no existe
            if not os.path.exists(full_path):
                os.makedirs(full_path, exist_ok=True)
                created_folders.append(folder_path)
                print(f"[DirectIA Backend] ✓ Creada físicamente: {full_path}")
            else:
                print(f"[DirectIA Backend] - Ya existe físicamente: {full_path}")

            # Registrar en MongoDB si no existe
            if not existing_metadata:
                metadata_col.insert_one({
                    "file_id": str(uuid.uuid4()),
                    "filename": folder.name,
                    "relative_path": relative_path,
                    "tipo": "carpeta",
                    "protegida": folder.protected,  # Usar el valor de protected de la template
                    "created_at": datetime.now(timezone.utc),
                    "user": user,
                    "template_id": folder.id,  # Referencia a la template
                    "group_id": folder.group_id  # Para saber a qué grupo pertenece
                })
                print(f"[DirectIA Backend] ✓ Registrada en MongoDB: {folder.name} (protegida: {folder.protected})")
            else:
                # Actualizar protección si es necesario
                if existing_metadata.get("protegida") != folder.protected:
                    metadata_col.update_one(
                        {"_id": existing_metadata["_id"]},
                        {"$set": {"protegida": folder.protected}}
                    )
                    print(f"[DirectIA Backend] ↻ Actualizada protección: {folder.name} (protegida: {folder.protected})")
                else:
                    print(f"[DirectIA Backend] - Ya existe en MongoDB: {folder.name}")

            # Crear subcarpetas recursivamente
            for child in folder.children:
                create_physical_folder(child, folder_path)

        except Exception as e:
            error_msg = f"Error creando {folder.name}: {str(e)}"
            errors.append(error_msg)
            print(f"[DirectIA Backend] ✗ {error_msg}")

    # Crear carpetas raíz y sus hijos
    root_folders = [f for f in folders if f.parent_id is None]
    print(f"[DirectIA Backend] Carpetas raíz a crear: {len(root_folders)}")

    for folder in root_folders:
        create_physical_folder(folder)

    print(f"[DirectIA Backend] Resultado: {len(created_folders)} carpetas creadas, {len(errors)} errores")

    return jsonify({
        "ok": True,
        "msg": f"Estructura aplicada al grupo '{group.name}': {len(created_folders)} carpetas creadas",
        "created": created_folders,
        "errors": errors,
        "total_templates": len(folders),
        "group_name": group.name
    })

@bp.post("/initialize-defaults")
def initialize_default_structure():
    """Inicializar estructura por defecto"""
    session = current_app.session()

    print("[DirectIA Backend] Inicializando estructura por defecto...")

    # Verificar si ya existe estructura
    existing = session.query(FolderTemplate).first()
    if existing:
        print(f"[DirectIA Backend] Ya existe estructura: {existing.name}")
        return jsonify({"error": "Ya existe una estructura definida"}), 400

    # Estructura por defecto
    default_folders = [
        {"name": "Documentos", "description": "Documentos generales", "icon": "folder", "order": 1},
        {"name": "Imágenes", "description": "Archivos de imagen", "icon": "image", "order": 2},
        {"name": "Videos", "description": "Archivos de video", "icon": "video", "order": 3},
        {"name": "Facturas", "description": "Facturas y comprobantes", "icon": "excel", "order": 4},
        {"name": "Contratos", "description": "Contratos y acuerdos legales", "icon": "text", "order": 5},
        {"name": "Reportes", "description": "Reportes e informes", "icon": "file", "order": 6},
    ]

    created = []
    for folder_data in default_folders:
        folder = FolderTemplate(
            name=folder_data["name"],
            description=folder_data["description"],
            icon=folder_data["icon"],
            order=folder_data["order"],
            protected=True,
            parent_id=None,
            group_id=None
        )
        session.add(folder)
        created.append(folder_data["name"])
        print(f"[DirectIA Backend] Creando carpeta por defecto: {folder_data['name']} (parent_id=None, group_id=None)")

    session.commit()
    print(f"[DirectIA Backend] Estructura por defecto creada exitosamente: {len(created)} carpetas")

    return jsonify({
        "ok": True,
        "msg": f"Estructura por defecto creada: {len(created)} carpetas",
        "folders": created
    })
