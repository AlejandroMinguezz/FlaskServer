"""
Text extraction modules for different document formats
"""

from .pdf_extractor import extract_text_from_pdf, extract_text_from_pdf_bytes
from .docx_extractor import extract_text_from_docx, extract_text_from_docx_bytes
from .txt_extractor import extract_text_from_txt, extract_text_from_txt_bytes
from .ocr_extractor import extract_text_from_image, extract_text_from_image_bytes, set_tesseract_path
from .unified_extractor import extract_text, extract_text_from_bytes, is_supported_format, get_supported_formats

__all__ = [
    'extract_text_from_pdf',
    'extract_text_from_pdf_bytes',
    'extract_text_from_docx',
    'extract_text_from_docx_bytes',
    'extract_text_from_txt',
    'extract_text_from_txt_bytes',
    'extract_text_from_image',
    'extract_text_from_image_bytes',
    'set_tesseract_path',
    'extract_text',
    'extract_text_from_bytes',
    'is_supported_format',
    'get_supported_formats',
]
