import os
import shutil
import uuid
from datetime import datetime, timezone
from urllib.parse import unquote
from werkzeug.utils import secure_filename
from src.services.file_icons import get_file_info, get_folder_icon

BASE_STORAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../storage/files"))

def list_files():
    """
    Lista todos los archivos y carpetas en el almacenamiento.

    Returns:
        dict con lista de elementos, cada uno con:
        - nombre: ruta relativa
        - tipo: tipo de elemento (archivo/carpeta)
        - icon: nombre del icono a mostrar
        - category: categoría del archivo
        - extension: extensión del archivo (solo archivos)
        - size: tamaño en bytes (solo archivos)
        - modified: fecha de modificación ISO (solo archivos)
    """
    elementos = []
    for root, dirs, files in os.walk(BASE_STORAGE_PATH):
        rel_root = os.path.relpath(root, BASE_STORAGE_PATH)
        rel_root = "" if rel_root == "." else rel_root

        # Procesar carpetas
        for d in dirs:
            ruta = os.path.join(rel_root, d).replace("\\", "/")
            folder_info = get_folder_icon()
            elementos.append({
                "nombre": ruta,
                "tipo": folder_info['type'],
                "icon": folder_info['icon'],
                "category": folder_info['category']
            })

        # Procesar archivos
        for f in files:
            ruta = os.path.join(rel_root, f).replace("\\", "/")
            path = os.path.join(root, f)
            file_info = get_file_info(f)

            elementos.append({
                "nombre": ruta,
                "tipo": file_info['type'],
                "icon": file_info['icon'],
                "category": file_info['category'],
                "extension": file_info['extension'],
                "size": os.path.getsize(path),
                "modified": datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
            })

    return {"elementos": elementos}


def upload_file(file, folder, user, metadata_col, ia_activa=False, ocr_fn=None, beto_fn=None):
    if not file:
        return {"error": "No file uploaded"}, 400

    filename = secure_filename(file.filename)

    # Limpiar y normalizar el path del folder
    # Si folder viene vacío o es ".", usar la raíz
    folder = folder.strip() if folder else ""

    # Si el folder contiene el nombre del archivo, extraer solo el directorio
    if folder and not folder.endswith('/'):
        # Verificar si es un path completo que incluye el archivo
        folder_as_path = os.path.join(BASE_STORAGE_PATH, folder)
        if os.path.isfile(folder_as_path):
            # Es un archivo existente, obtener solo el directorio
            folder = os.path.dirname(folder)
        elif '.' in os.path.basename(folder) and not os.path.isdir(folder_as_path):
            # Parece ser un nombre de archivo (tiene extensión), extraer directorio
            folder = os.path.dirname(folder)

    # Normalizar: eliminar "/" inicial si existe
    folder = folder.lstrip('/')

    # Crear el directorio si no existe
    folder_path = os.path.join(BASE_STORAGE_PATH, folder) if folder else BASE_STORAGE_PATH
    os.makedirs(folder_path, exist_ok=True)

    # Manejar archivos duplicados (nombrearchivo(1).ext, nombrearchivo(2).ext, etc.)
    file_path = os.path.join(folder_path, filename)
    if os.path.exists(file_path):
        name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(file_path):
            new_filename = f"{name}({counter}){ext}"
            file_path = os.path.join(folder_path, new_filename)
            counter += 1
        filename = os.path.basename(file_path)
        print(f"[UPLOAD] Archivo duplicado detectado, renombrado a: {filename}")

    file.save(file_path)
    print(f"[UPLOAD] Archivo recibido: {file_path}")

    file_id = str(uuid.uuid4())
    relative_path = f"/{folder}/" if folder else "/"

    metadata = {
        "file_id": file_id,
        "filename": filename,
        "relative_path": relative_path,
        "size": os.path.getsize(file_path),
        "uploaded_at": datetime.now(timezone.utc),
        "user": user,
        "status": "uploaded"
    }

    if ia_activa and ocr_fn and beto_fn:
        print(f"[IA] Clasificación activada para '{filename}'")
        try:
            print(f"[IA] Ejecutando OCR sobre: {file_path}")
            texto_extraido = ocr_fn(file_path)
            print(f"[IA] OCR completado. {len(texto_extraido)} caracteres extraídos.")
            print(f"[IA] Fragmento OCR → {texto_extraido[:300]}")

            print("[IA] Ejecutando BETO...")
            tipo, confianza, nombre_sugerido, carpeta_sugerida = beto_fn(texto_extraido)
            print(f"[IA] Resultado BETO → Tipo: {tipo} | Confianza: {confianza:.2f}")

            metadata.update({
                "clasificacion": {
                    "tipo": tipo,
                    "confianza": confianza,
                    "nombre_sugerido": nombre_sugerido,
                    "carpeta_sugerida": carpeta_sugerida,
                    "procesado_por": "BETO"
                }
            })

        except Exception as e:
            print(f"[ERROR IA] Error durante OCR o clasificación: {e}")
            metadata["clasificacion_error"] = str(e)

    result = metadata_col.insert_one(metadata)
    metadata["_id"] = str(result.inserted_id)

    response = {"message": "File uploaded successfully", "metadata": metadata}
    if ia_activa:
        response.update({
            "tipo": metadata.get("clasificacion", {}).get("tipo"),
            "confianza": metadata.get("clasificacion", {}).get("confianza"),
            "nombre_sugerido": metadata.get("clasificacion", {}).get("nombre_sugerido"),
            "carpeta_sugerida": metadata.get("clasificacion", {}).get("carpeta_sugerida")
        })

    print(f"[UPLOAD] Subida completada: {filename}")
    return response, 201


def download_file(filepath):
    full_path = os.path.join(BASE_STORAGE_PATH, unquote(filepath))
    if os.path.isfile(full_path):
        return True, os.path.dirname(full_path), os.path.basename(full_path)
    return False, None, None


def delete_element(ruta, metadata_col):
    decoded_ruta = unquote(ruta)
    full_path = os.path.join(BASE_STORAGE_PATH, decoded_ruta)

    if os.path.isfile(full_path):
        os.remove(full_path)
    elif os.path.isdir(full_path):
        shutil.rmtree(full_path)
    else:
        return {"error": "Ruta no encontrada"}, 404

    filename = os.path.basename(decoded_ruta)
    relative_path = "/" + os.path.dirname(decoded_ruta).replace("\\", "/")
    if relative_path == "/.":
        relative_path = "/"

    # Usar delete_many para eliminar todos los duplicados
    result = metadata_col.delete_many({"filename": filename, "relative_path": relative_path})
    print(f"[DELETE] Eliminados {result.deleted_count} registros de metadata para {filename} en {relative_path}")

    # Si es una carpeta, eliminar también todos los archivos dentro
    if os.path.isdir(full_path) or result.deleted_count == 0:
        # Buscar por relative_path que comience con la ruta de la carpeta
        folder_pattern = relative_path.rstrip('/') + '/' + filename + '/'
        result_children = metadata_col.delete_many({"relative_path": {"$regex": f"^{folder_pattern}"}})
        print(f"[DELETE] Eliminados {result_children.deleted_count} archivos dentro de la carpeta")

    return {"message": "Elemento eliminado correctamente"}, 200


def create_folder(ruta, protegida, user, metadata_col):
    if not ruta:
        return {"error": "Ruta no especificada"}, 400

    full_path = os.path.join(BASE_STORAGE_PATH, ruta)
    os.makedirs(full_path, exist_ok=True)

    metadata_col.insert_one({
        "file_id": str(uuid.uuid4()),
        "filename": os.path.basename(ruta),
        "relative_path": "/" + os.path.dirname(ruta).replace("\\", "/"),
        "tipo": "carpeta",
        "protegida": protegida,
        "created_at": datetime.now(timezone.utc),
        "user": user
    })

    return {"message": "Carpeta creada"}, 201


def create_file(ruta, user="unknown", metadata_col=None):
    if not ruta:
        return {"error": "Ruta no especificada"}, 400

    full_path = os.path.join(BASE_STORAGE_PATH, ruta)
    if os.path.exists(full_path):
        return {"error": "El archivo ya existe"}, 409

    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write("")

    # Guardar metadata en MongoDB si se proporciona la colección
    if metadata_col is not None:
        filename = os.path.basename(ruta)
        relative_path = "/" + os.path.dirname(ruta).replace("\\", "/").lstrip("/")
        if relative_path == "/.":
            relative_path = "/"

        metadata_col.insert_one({
            "file_id": str(uuid.uuid4()),
            "filename": filename,
            "relative_path": relative_path,
            "size": 0,
            "created_at": datetime.now(timezone.utc),
            "user": user,
            "status": "created"
        })

    return {"message": "Archivo creado"}, 201


def move_file(origen_rel, destino_rel, metadata_col):
    origen = os.path.join(BASE_STORAGE_PATH, origen_rel)
    destino = os.path.join(BASE_STORAGE_PATH, destino_rel)

    if not os.path.exists(origen):
        return {"error": "El archivo de origen no existe"}, 404

    if os.path.isdir(destino):
        destino = os.path.join(destino, os.path.basename(origen))

    if os.path.isfile(destino):
        return {"error": "Ya existe un archivo con ese nombre en destino"}, 409

    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.move(origen, destino)

    new_relative = "/" + os.path.dirname(os.path.relpath(destino, BASE_STORAGE_PATH)).replace("\\", "/")
    new_filename = os.path.basename(destino)

    metadata_col.update_one(
        {"filename": os.path.basename(origen)},
        {"$set": {
            "relative_path": new_relative if new_relative != "/." else "/",
            "filename": new_filename
        }}
    )

    return {"ok": True, "new_path": new_relative, "filename": new_filename}, 200
