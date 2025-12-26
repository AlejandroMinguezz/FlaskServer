import os
from .ocr import ejecutar_ocr, extract_text_from_docx, extract_text_from_txt


def extract_text(file_path: str) -> str:
    """
    Extrae texto de un archivo segun su extension.
    Soporta: PDF, DOCX, TXT, imagenes (JPG, PNG, etc.)

    Args:
        file_path: Ruta al archivo

    Returns:
        Texto extraido del documento
    """
    if not os.path.exists(file_path):
        print(f"[ERROR] Archivo no encontrado: {file_path}")
        return ""

    ext = os.path.splitext(file_path)[1].lower()

    # DOCX - Usar python-docx
    if ext in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)

    # TXT - Lectura directa
    elif ext == '.txt':
        return extract_text_from_txt(file_path)

    # PDF e imagenes - Usar OCR
    elif ext in ['.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
        return ejecutar_ocr(file_path)

    else:
        print(f"[WARNING] Formato no soportado: {ext}")
        return ""


__all__ = ['extract_text', 'ejecutar_ocr', 'extract_text_from_docx', 'extract_text_from_txt']
