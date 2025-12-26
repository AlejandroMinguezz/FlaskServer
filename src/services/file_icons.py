# src/services/file_icons.py
"""
Utilidad para detectar tipos de archivos y asignar iconos apropiados
"""

import os

# Mapeo de extensiones a tipos de archivo e iconos
FILE_TYPE_MAPPINGS = {
    # Documentos
    'pdf': {'type': 'pdf', 'icon': 'pdf', 'category': 'document'},
    'doc': {'type': 'word', 'icon': 'word', 'category': 'document'},
    'docx': {'type': 'word', 'icon': 'word', 'category': 'document'},
    'odt': {'type': 'document', 'icon': 'document', 'category': 'document'},
    'txt': {'type': 'text', 'icon': 'text', 'category': 'document'},
    'rtf': {'type': 'document', 'icon': 'document', 'category': 'document'},

    # Hojas de cálculo
    'xls': {'type': 'excel', 'icon': 'excel', 'category': 'spreadsheet'},
    'xlsx': {'type': 'excel', 'icon': 'excel', 'category': 'spreadsheet'},
    'ods': {'type': 'spreadsheet', 'icon': 'spreadsheet', 'category': 'spreadsheet'},
    'csv': {'type': 'csv', 'icon': 'csv', 'category': 'spreadsheet'},

    # Presentaciones
    'ppt': {'type': 'powerpoint', 'icon': 'powerpoint', 'category': 'presentation'},
    'pptx': {'type': 'powerpoint', 'icon': 'powerpoint', 'category': 'presentation'},
    'odp': {'type': 'presentation', 'icon': 'presentation', 'category': 'presentation'},

    # Imágenes
    'jpg': {'type': 'image', 'icon': 'image', 'category': 'image'},
    'jpeg': {'type': 'image', 'icon': 'image', 'category': 'image'},
    'png': {'type': 'image', 'icon': 'image', 'category': 'image'},
    'gif': {'type': 'image', 'icon': 'image', 'category': 'image'},
    'bmp': {'type': 'image', 'icon': 'image', 'category': 'image'},
    'svg': {'type': 'vector', 'icon': 'vector', 'category': 'image'},
    'webp': {'type': 'image', 'icon': 'image', 'category': 'image'},
    'ico': {'type': 'image', 'icon': 'image', 'category': 'image'},

    # Audio
    'mp3': {'type': 'audio', 'icon': 'audio', 'category': 'media'},
    'wav': {'type': 'audio', 'icon': 'audio', 'category': 'media'},
    'flac': {'type': 'audio', 'icon': 'audio', 'category': 'media'},
    'aac': {'type': 'audio', 'icon': 'audio', 'category': 'media'},
    'ogg': {'type': 'audio', 'icon': 'audio', 'category': 'media'},
    'm4a': {'type': 'audio', 'icon': 'audio', 'category': 'media'},

    # Video
    'mp4': {'type': 'video', 'icon': 'video', 'category': 'media'},
    'avi': {'type': 'video', 'icon': 'video', 'category': 'media'},
    'mkv': {'type': 'video', 'icon': 'video', 'category': 'media'},
    'mov': {'type': 'video', 'icon': 'video', 'category': 'media'},
    'wmv': {'type': 'video', 'icon': 'video', 'category': 'media'},
    'flv': {'type': 'video', 'icon': 'video', 'category': 'media'},
    'webm': {'type': 'video', 'icon': 'video', 'category': 'media'},

    # Archivos comprimidos
    'zip': {'type': 'archive', 'icon': 'archive', 'category': 'archive'},
    'rar': {'type': 'archive', 'icon': 'archive', 'category': 'archive'},
    '7z': {'type': 'archive', 'icon': 'archive', 'category': 'archive'},
    'tar': {'type': 'archive', 'icon': 'archive', 'category': 'archive'},
    'gz': {'type': 'archive', 'icon': 'archive', 'category': 'archive'},
    'bz2': {'type': 'archive', 'icon': 'archive', 'category': 'archive'},

    # Código
    'py': {'type': 'code', 'icon': 'code-python', 'category': 'code'},
    'js': {'type': 'code', 'icon': 'code-javascript', 'category': 'code'},
    'ts': {'type': 'code', 'icon': 'code-typescript', 'category': 'code'},
    'java': {'type': 'code', 'icon': 'code-java', 'category': 'code'},
    'c': {'type': 'code', 'icon': 'code-c', 'category': 'code'},
    'cpp': {'type': 'code', 'icon': 'code-cpp', 'category': 'code'},
    'h': {'type': 'code', 'icon': 'code-header', 'category': 'code'},
    'cs': {'type': 'code', 'icon': 'code-csharp', 'category': 'code'},
    'php': {'type': 'code', 'icon': 'code-php', 'category': 'code'},
    'rb': {'type': 'code', 'icon': 'code-ruby', 'category': 'code'},
    'go': {'type': 'code', 'icon': 'code-go', 'category': 'code'},
    'rs': {'type': 'code', 'icon': 'code-rust', 'category': 'code'},

    # Web
    'html': {'type': 'html', 'icon': 'html', 'category': 'web'},
    'htm': {'type': 'html', 'icon': 'html', 'category': 'web'},
    'css': {'type': 'css', 'icon': 'css', 'category': 'web'},
    'scss': {'type': 'css', 'icon': 'css', 'category': 'web'},
    'sass': {'type': 'css', 'icon': 'css', 'category': 'web'},
    'xml': {'type': 'xml', 'icon': 'xml', 'category': 'web'},
    'json': {'type': 'json', 'icon': 'json', 'category': 'data'},
    'yaml': {'type': 'yaml', 'icon': 'yaml', 'category': 'data'},
    'yml': {'type': 'yaml', 'icon': 'yaml', 'category': 'data'},

    # Bases de datos
    'sql': {'type': 'database', 'icon': 'database', 'category': 'data'},
    'db': {'type': 'database', 'icon': 'database', 'category': 'data'},
    'sqlite': {'type': 'database', 'icon': 'database', 'category': 'data'},
    'mdb': {'type': 'database', 'icon': 'database', 'category': 'data'},

    # Ejecutables
    'exe': {'type': 'executable', 'icon': 'executable', 'category': 'executable'},
    'msi': {'type': 'installer', 'icon': 'installer', 'category': 'executable'},
    'app': {'type': 'application', 'icon': 'application', 'category': 'executable'},
    'dmg': {'type': 'disk-image', 'icon': 'disk', 'category': 'executable'},
    'iso': {'type': 'disk-image', 'icon': 'disk', 'category': 'executable'},

    # Otros formatos comunes
    'md': {'type': 'markdown', 'icon': 'markdown', 'category': 'document'},
    'log': {'type': 'log', 'icon': 'log', 'category': 'document'},
    'ini': {'type': 'config', 'icon': 'config', 'category': 'config'},
    'conf': {'type': 'config', 'icon': 'config', 'category': 'config'},
    'env': {'type': 'config', 'icon': 'config', 'category': 'config'},
}


def get_file_info(filename: str) -> dict:
    """
    Obtiene información del tipo de archivo e icono basándose en la extensión.

    Args:
        filename: Nombre del archivo con extensión

    Returns:
        dict con keys: type, icon, category, extension
    """
    # Obtener extensión sin el punto y en minúsculas
    _, ext = os.path.splitext(filename)
    ext = ext.lower().lstrip('.')

    # Buscar en el mapeo
    if ext in FILE_TYPE_MAPPINGS:
        info = FILE_TYPE_MAPPINGS[ext].copy()
        info['extension'] = ext
        return info

    # Tipo desconocido
    return {
        'type': 'file',
        'icon': 'file',
        'category': 'unknown',
        'extension': ext if ext else 'none'
    }


def get_folder_icon() -> dict:
    """
    Retorna información para carpetas.

    Returns:
        dict con información de icono para carpetas
    """
    return {
        'type': 'folder',
        'icon': 'folder',
        'category': 'folder',
        'extension': None
    }


def get_icon_for_classification(classification_type: str) -> str:
    """
    Obtiene el icono sugerido basado en la clasificación de IA.

    Args:
        classification_type: Tipo de clasificación (factura, recibo, cv, etc.)

    Returns:
        Nombre del icono sugerido
    """
    classification_icons = {
        'factura': 'invoice',
        'recibo': 'receipt',
        'cv': 'cv',
        'curriculum': 'cv',
        'pagare': 'promissory-note',
        'contrato': 'contract',
        'otro': 'document',
        'unknown': 'file'
    }

    return classification_icons.get(classification_type.lower(), 'document')
