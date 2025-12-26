import os, subprocess, json
from pathlib import Path
from flask import Blueprint, jsonify, request, render_template, abort,current_app
from src.models import User, Role, Group, GroupMember
from werkzeug.security import generate_password_hash
from src.services.token import verify_token

bp = Blueprint("admin", __name__, url_prefix="/admin")

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
COMPOSE_FILE = os.getenv("DOCKER_COMPOSE_FILE", "docker/docker-compose.yml")
WORKDIR = os.getenv("COMPOSE_WORKDIR", os.getcwd())


def _auth():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        token = request.args.get("token", "")
    payload = verify_token(token)
    if not payload:
        return False
    role = payload.get("role")
    # acepta si el nombre es "admin" o el id es 1
    return role == "admin" or role == 1 or role == "1"



def _run(cmd):
    # requiere que el usuario que ejecuta Flask pueda usar docker sin sudo
    return subprocess.run(cmd, cwd=WORKDIR, capture_output=True, text=True)

def _parse_docker_ps():
    """Parsea la salida de docker ps y devuelve lista de contenedores"""
    res = _run(["docker", "ps", "-a", "--filter", "name=directia_", "--format", "{{.Names}}\t{{.Status}}\t{{.State}}"])
    if res.returncode != 0:
        return []

    containers = []
    for line in res.stdout.strip().split('\n'):
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) >= 3:
            containers.append({
                "name": parts[0],
                "status": parts[1],
                "state": parts[2]
            })
    return containers

@bp.before_request
def guard():
    # Permitir peticiones OPTIONS (CORS preflight) sin autenticación
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    # Permite ver el panel HTML sin header Authorization si llegas con ?token=...
    if request.endpoint == "admin.panel":
        return
    if not _auth():
        return jsonify({"error":"unauthorized"}), 401

@bp.get("/")
def panel():
    qtoken = request.args.get("token", "")
    payload = verify_token(qtoken)
    if not payload:
        abort(401)
    role = payload.get("role")
    if role != "admin" and role not in (1, "1"):
        abort(403)
    return render_template("admin.html", token=qtoken)

@bp.get("/status")
def status():
    res = _run(["docker","compose","-f",COMPOSE_FILE,"ps"])
    return jsonify({"ok":res.returncode==0,"output":res.stdout or res.stderr})

@bp.post("/start")
def start():
    res = _run(["docker","compose","-f",COMPOSE_FILE,"up","-d"])
    return jsonify({"ok":res.returncode==0,"output":res.stdout or res.stderr})

@bp.post("/stop")
def stop():
    res = _run(["docker","compose","-f",COMPOSE_FILE,"down"])
    return jsonify({"ok":res.returncode==0,"output":res.stdout or res.stderr})

@bp.post("/restart")
def restart():
    res = _run(["docker","compose","-f",COMPOSE_FILE,"restart"])
    return jsonify({"ok":res.returncode==0,"output":res.stdout or res.stderr})


@bp.get("/users")
def list_users():
    session = current_app.session()
    users = session.query(User).all()
    data = [{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "active": u.active,
        "role_id": u.role_id,
        "role_name": u.role.name if u.role else None
    } for u in users]
    return jsonify({"users": data})

@bp.put("/users/<int:user_id>")
def update_user(user_id):
    session = current_app.session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.get_json() or {}

    # Actualizar email
    if "email" in data:
        user.email = data["email"]

    # Actualizar contraseña
    if "password" in data and data["password"]:
        user.password_hash = generate_password_hash(data["password"])

    # Actualizar estado activo
    if "active" in data:
        user.active = bool(data["active"])

    # Actualizar rol
    if "role_name" in data:
        role = session.query(Role).filter_by(name=data["role_name"]).first()
        if role:
            user.role_id = role.id
        else:
            return jsonify({"error": f"Rol '{data['role_name']}' no existe"}), 400
    elif "role_id" in data:
        role = session.query(Role).get(data["role_id"])
        if role:
            user.role_id = data["role_id"]
        else:
            return jsonify({"error": f"Rol con ID {data['role_id']} no existe"}), 400

    session.commit()
    return jsonify({"ok": True, "msg": "Usuario actualizado"})

@bp.post("/users")
def create_user():
    session = current_app.session()
    data = request.get_json() or {}
    if not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "Datos incompletos"}), 400

    if session.query(User).filter_by(username=data["username"]).first():
        return jsonify({"error": "Usuario ya existe"}), 409

    # Buscar rol por nombre o usar "usuario" por defecto
    role_name = data.get("role", "usuario")
    role = session.query(Role).filter_by(name=role_name).first()
    if not role:
        return jsonify({"error": f"Rol '{role_name}' no existe"}), 400

    user = User(
        username=data["username"],
        email=data["email"],
        password_hash=generate_password_hash(data["password"]),
        role_id=role.id,
        active=True,
    )
    session.add(user)
    session.commit()
    return jsonify({"ok": True, "msg": "Usuario creado correctamente"})


# ========================================
# ENDPOINTS DE GESTIÓN DE GRUPOS
# ========================================

@bp.get("/grupos")
def list_grupos():
    """Lista todos los grupos"""
    session = current_app.session()
    grupos = session.query(Group).all()
    data = [{
        "id": g.id,
        "name": g.name,
        "created_at": g.created_at.isoformat() if g.created_at else None,
        "member_count": len(g.members)
    } for g in grupos]
    return jsonify({"grupos": data})

@bp.post("/grupos")
def create_grupo():
    """Crea un nuevo grupo"""
    session = current_app.session()
    data = request.get_json() or {}

    # Aceptar tanto 'name' como 'nombre' para compatibilidad con el frontend
    group_name = data.get("name") or data.get("nombre")

    if not group_name:
        return jsonify({"error": "El nombre del grupo es requerido"}), 400

    # Verificar si el grupo ya existe
    if session.query(Group).filter_by(name=group_name).first():
        return jsonify({"error": "El grupo ya existe"}), 409

    grupo = Group(name=group_name)
    session.add(grupo)
    session.commit()

    return jsonify({
        "ok": True,
        "msg": "Grupo creado correctamente",
        "grupo": {
            "id": grupo.id,
            "name": grupo.name,
            "created_at": grupo.created_at.isoformat() if grupo.created_at else None
        }
    })

@bp.put("/grupos/<int:group_id>")
def update_grupo(group_id):
    """Actualiza un grupo existente"""
    session = current_app.session()
    grupo = session.query(Group).get(group_id)

    if not grupo:
        return jsonify({"error": "Grupo no encontrado"}), 404

    data = request.get_json() or {}

    # Aceptar tanto 'name' como 'nombre' para compatibilidad con el frontend
    group_name = data.get("name") or data.get("nombre")

    if group_name:
        # Verificar que el nuevo nombre no esté en uso
        existing = session.query(Group).filter_by(name=group_name).first()
        if existing and existing.id != group_id:
            return jsonify({"error": "El nombre del grupo ya está en uso"}), 409
        grupo.name = group_name

    session.commit()
    return jsonify({"ok": True, "msg": "Grupo actualizado correctamente"})

@bp.delete("/grupos/<int:group_id>")
def delete_grupo(group_id):
    """Elimina un grupo"""
    session = current_app.session()
    grupo = session.query(Group).get(group_id)

    if not grupo:
        return jsonify({"error": "Grupo no encontrado"}), 404

    # No permitir eliminar el grupo de administradores (ID 1)
    if group_id == 1:
        return jsonify({"error": "No se puede eliminar el grupo de administradores"}), 403

    session.delete(grupo)
    session.commit()
    return jsonify({"ok": True, "msg": "Grupo eliminado correctamente"})

@bp.get("/grupos/<int:group_id>/usuarios")
def get_group_users(group_id):
    """Obtiene los usuarios de un grupo"""
    session = current_app.session()
    grupo = session.query(Group).get(group_id)

    if not grupo:
        return jsonify({"error": "Grupo no encontrado"}), 404

    # Obtener usuarios del grupo
    members = session.query(User).join(GroupMember).filter(GroupMember.group_id == group_id).all()

    data = [{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "active": u.active,
        "role_id": u.role_id,
        "role_name": u.role.name if u.role else None
    } for u in members]

    return jsonify({"usuarios": data})

@bp.post("/grupos/<int:group_id>/usuarios/<int:user_id>")
def add_user_to_group(group_id, user_id):
    """Añade un usuario a un grupo"""
    session = current_app.session()

    # Verificar que el grupo existe
    grupo = session.query(Group).get(group_id)
    if not grupo:
        return jsonify({"error": "Grupo no encontrado"}), 404

    # Verificar que el usuario existe
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Verificar si ya está en el grupo
    existing = session.query(GroupMember).filter_by(
        group_id=group_id,
        user_id=user_id
    ).first()

    if existing:
        return jsonify({"error": "El usuario ya está en el grupo"}), 409

    # Añadir al grupo
    member = GroupMember(group_id=group_id, user_id=user_id)
    session.add(member)
    session.commit()

    return jsonify({"ok": True, "msg": "Usuario añadido al grupo correctamente"})

@bp.delete("/grupos/<int:group_id>/usuarios/<int:user_id>")
def remove_user_from_group(group_id, user_id):
    """Elimina un usuario de un grupo"""
    session = current_app.session()

    member = session.query(GroupMember).filter_by(
        group_id=group_id,
        user_id=user_id
    ).first()

    if not member:
        return jsonify({"error": "El usuario no está en el grupo"}), 404

    session.delete(member)
    session.commit()

    return jsonify({"ok": True, "msg": "Usuario eliminado del grupo correctamente"})


# ========================================
# ENDPOINTS DE CONTROL DE CONTENEDORES
# ========================================

@bp.get("/containers")
def list_containers():
    """Lista todos los contenedores de DirectIA con su estado"""
    containers = _parse_docker_ps()

    # Enriquecer con stats si el contenedor está corriendo
    for container in containers:
        if container["state"] == "running":
            res = _run(["docker", "stats", "--no-stream", "--format",
                       "{{.CPUPerc}}\t{{.MemUsage}}", container["name"]])
            if res.returncode == 0 and res.stdout.strip():
                parts = res.stdout.strip().split('\t')
                if len(parts) >= 2:
                    container["cpu"] = parts[0]
                    container["memory"] = parts[1]
                else:
                    container["cpu"] = "N/A"
                    container["memory"] = "N/A"
        else:
            container["cpu"] = "N/A"
            container["memory"] = "N/A"

    return jsonify({"ok": True, "containers": containers})

@bp.post("/containers/<container_name>/start")
def start_container(container_name):
    """Inicia un contenedor específico"""
    res = _run(["docker", "start", container_name])
    return jsonify({
        "ok": res.returncode == 0,
        "msg": f"Contenedor {container_name} iniciado" if res.returncode == 0 else "Error al iniciar contenedor",
        "output": res.stdout or res.stderr
    })

@bp.post("/containers/<container_name>/stop")
def stop_container(container_name):
    """Detiene un contenedor específico"""
    res = _run(["docker", "stop", container_name])
    return jsonify({
        "ok": res.returncode == 0,
        "msg": f"Contenedor {container_name} detenido" if res.returncode == 0 else "Error al detener contenedor",
        "output": res.stdout or res.stderr
    })

@bp.post("/containers/<container_name>/restart")
def restart_container(container_name):
    """Reinicia un contenedor específico"""
    res = _run(["docker", "restart", container_name])
    return jsonify({
        "ok": res.returncode == 0,
        "msg": f"Contenedor {container_name} reiniciado" if res.returncode == 0 else "Error al reiniciar contenedor",
        "output": res.stdout or res.stderr
    })

@bp.post("/containers/<container_name>/recreate")
def recreate_container(container_name):
    """Recrea un contenedor (útil para aplicar cambios de configuración)"""
    # Detener y eliminar el contenedor
    stop_res = _run(["docker", "stop", container_name])
    if stop_res.returncode != 0:
        return jsonify({"ok": False, "msg": "Error al detener contenedor", "output": stop_res.stderr})

    remove_res = _run(["docker", "rm", container_name])
    if remove_res.returncode != 0:
        return jsonify({"ok": False, "msg": "Error al eliminar contenedor", "output": remove_res.stderr})

    # Recrear con docker-compose
    service_name = container_name.replace("directia_", "")
    up_res = _run(["docker", "compose", "-f", COMPOSE_FILE, "up", "-d", service_name])

    return jsonify({
        "ok": up_res.returncode == 0,
        "msg": f"Contenedor {container_name} recreado" if up_res.returncode == 0 else "Error al recrear contenedor",
        "output": up_res.stdout or up_res.stderr
    })

@bp.get("/containers/<container_name>/logs")
def container_logs(container_name):
    """Obtiene los últimos logs de un contenedor"""
    lines = request.args.get("lines", "100")
    res = _run(["docker", "logs", "--tail", lines, container_name])

    return jsonify({
        "ok": res.returncode == 0,
        "logs": res.stdout or res.stderr,
        "container": container_name
    })

@bp.get("/containers/<container_name>/stats")
def container_stats(container_name):
    """Obtiene estadísticas en tiempo real de un contenedor"""
    res = _run(["docker", "stats", "--no-stream", "--format",
               "{{.CPUPerc}}\t{{.MemPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}",
               container_name])

    if res.returncode != 0:
        return jsonify({"ok": False, "error": "Contenedor no encontrado o no está corriendo"})

    parts = res.stdout.strip().split('\t')
    if len(parts) >= 5:
        stats = {
            "cpu": parts[0],
            "mem_percent": parts[1],
            "mem_usage": parts[2],
            "net_io": parts[3],
            "block_io": parts[4]
        }
    else:
        stats = {"error": "No se pudieron obtener estadísticas"}

    return jsonify({"ok": True, "stats": stats, "container": container_name})


# ========================================
# ENDPOINT PARA CREAR ESTRUCTURA DE CARPETAS
# ========================================

@bp.post("/create-folder-structure")
def create_folder_structure():
    """
    Crea automáticamente la estructura de carpetas predeterminada
    basada en las categorías del clasificador IA

    Body JSON:
        {
            "username": "nombre_usuario",  # Requerido
            "grupo_id": 1                   # Opcional
        }

    Retorna:
        {
            "ok": true,
            "msg": "Estructura de carpetas creada correctamente",
            "folders_created": ["/usuario/Documentos/Facturas/", ...],
            "folders_skipped": ["/usuario/Documentos/Otros/"],  # Ya existían
            "total": 9
        }
    """
    data = request.get_json() or {}
    username = data.get("username")

    if not username:
        return jsonify({"error": "Se requiere el campo 'username'"}), 400

    # Verificar que el usuario existe
    session = current_app.session()
    user = session.query(User).filter_by(username=username).first()
    if not user:
        return jsonify({"error": f"Usuario '{username}' no encontrado"}), 404

    # Leer configuración de categorías
    config_path = Path(__file__).parent.parent.parent / 'ai_directia' / 'config' / 'categories.json'

    if not config_path.exists():
        return jsonify({"error": "Archivo de configuración de categorías no encontrado"}), 500

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        return jsonify({"error": f"Error al leer configuración: {str(e)}"}), 500

    categories = config.get('categories', [])

    if not categories:
        return jsonify({"error": "No se encontraron categorías en la configuración"}), 500

    # Obtener ruta base de almacenamiento
    storage_path = current_app.config.get("STORAGE_PATH", "./storage/files")
    base_path = Path(storage_path) / username

    folders_created = []
    folders_skipped = []

    # Crear carpeta base del usuario si no existe
    if not base_path.exists():
        base_path.mkdir(parents=True, exist_ok=True)
        folders_created.append(f"/{username}/")

    # Crear carpetas para cada categoría
    for category in categories:
        folder_path = category.get('folder_path', '')

        if not folder_path:
            continue

        # Limpiar la ruta: remover el / inicial y final
        clean_path = folder_path.strip('/')

        # Construir ruta física completa
        full_path = base_path / clean_path

        try:
            if full_path.exists():
                folders_skipped.append(f"/{username}/{clean_path}/")
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                folders_created.append(f"/{username}/{clean_path}/")
                print(f"[Admin] Carpeta creada: {full_path}")
        except Exception as e:
            print(f"[Admin] Error al crear carpeta {full_path}: {str(e)}")
            return jsonify({
                "error": f"Error al crear carpeta {clean_path}: {str(e)}"
            }), 500

    return jsonify({
        "ok": True,
        "msg": "Estructura de carpetas creada correctamente",
        "folders_created": folders_created,
        "folders_skipped": folders_skipped,
        "total": len(folders_created) + len(folders_skipped),
        "categories": len(categories)
    })
