# src/routes/file_icons_route.py
"""
Endpoint para obtener información sobre iconos de archivos
"""
from flask import Blueprint, jsonify
from src.services.file_icons import FILE_TYPE_MAPPINGS, get_file_info, get_folder_icon

bp = Blueprint("file_icons", __name__, url_prefix="/api/file-icons")


@bp.route("/mappings", methods=["GET"])
def get_icon_mappings():
    """
    Retorna el mapeo completo de extensiones a iconos.

    Returns:
        JSON con todas las extensiones soportadas y sus iconos correspondientes
    """
    return jsonify({
        "mappings": FILE_TYPE_MAPPINGS,
        "folder": get_folder_icon(),
        "total_extensions": len(FILE_TYPE_MAPPINGS)
    })


@bp.route("/categories", methods=["GET"])
def get_categories():
    """
    Retorna las categorías disponibles de archivos.

    Returns:
        JSON con lista de categorías únicas
    """
    categories = set()
    for info in FILE_TYPE_MAPPINGS.values():
        categories.add(info['category'])

    return jsonify({
        "categories": sorted(list(categories))
    })


@bp.route("/extensions/<category>", methods=["GET"])
def get_extensions_by_category(category):
    """
    Retorna todas las extensiones de una categoría específica.

    Args:
        category: Nombre de la categoría (document, image, code, etc.)

    Returns:
        JSON con extensiones de esa categoría
    """
    extensions = {}
    for ext, info in FILE_TYPE_MAPPINGS.items():
        if info['category'] == category:
            extensions[ext] = info

    return jsonify({
        "category": category,
        "extensions": extensions,
        "count": len(extensions)
    })
