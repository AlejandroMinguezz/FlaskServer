"""
Unified text extraction module
Automatically detects format and uses appropriate extractor
"""

from pathlib import Path
import mimetypes

from .pdf_extractor import extract_text_from_pdf, extract_text_from_pdf_bytes
from .docx_extractor import extract_text_from_docx, extract_text_from_docx_bytes
from .txt_extractor import extract_text_from_txt, extract_text_from_txt_bytes
from .ocr_extractor import extract_text_from_image, extract_text_from_image_bytes


# File extension to extractor mapping
EXTRACTORS = {
    '.pdf': extract_text_from_pdf,
    '.docx': extract_text_from_docx,
    '.doc': extract_text_from_docx,  # Try DOCX for old .doc files
    '.txt': extract_text_from_txt,
    '.text': extract_text_from_txt,
    '.png': extract_text_from_image,
    '.jpg': extract_text_from_image,
    '.jpeg': extract_text_from_image,
    '.tiff': extract_text_from_image,
    '.bmp': extract_text_from_image,
    '.gif': extract_text_from_image,
}

BYTES_EXTRACTORS = {
    'pdf': extract_text_from_pdf_bytes,
    'docx': extract_text_from_docx_bytes,
    'doc': extract_text_from_docx_bytes,
    'txt': extract_text_from_txt_bytes,
    'text': extract_text_from_txt_bytes,
    'png': extract_text_from_image_bytes,
    'jpg': extract_text_from_image_bytes,
    'jpeg': extract_text_from_image_bytes,
    'tiff': extract_text_from_image_bytes,
    'bmp': extract_text_from_image_bytes,
    'gif': extract_text_from_image_bytes,
}


def detect_file_type(file_path):
    """
    Detect file type from extension

    Args:
        file_path: Path to file

    Returns:
        str: File type ('pdf', 'docx', 'txt', 'image', 'unknown')
    """
    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    if extension == '.pdf':
        return 'pdf'
    elif extension in ['.docx', '.doc']:
        return 'docx'
    elif extension in ['.txt', '.text']:
        return 'txt'
    elif extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
        return 'image'
    else:
        # Try to detect from mime type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            if 'pdf' in mime_type:
                return 'pdf'
            elif 'word' in mime_type or 'document' in mime_type:
                return 'docx'
            elif 'text' in mime_type:
                return 'txt'
            elif 'image' in mime_type:
                return 'image'

        return 'unknown'


def extract_text(file_path):
    """
    Extract text from file, automatically detecting format

    Args:
        file_path: Path to the file

    Returns:
        dict: {
            'text': extracted text,
            'success': bool,
            'file_type': detected file type,
            'error': error message if any,
            ... additional format-specific fields
        }
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return {
            'text': '',
            'success': False,
            'file_type': 'unknown',
            'error': f'File not found: {file_path}'
        }

    # Detect file type
    extension = file_path.suffix.lower()

    if extension not in EXTRACTORS:
        return {
            'text': '',
            'success': False,
            'file_type': 'unknown',
            'error': f'Unsupported file format: {extension}'
        }

    # Use appropriate extractor
    extractor = EXTRACTORS[extension]

    try:
        result = extractor(file_path)
        result['file_type'] = detect_file_type(file_path)
        result['file_name'] = file_path.name
        return result

    except Exception as e:
        return {
            'text': '',
            'success': False,
            'file_type': detect_file_type(file_path),
            'error': f'Extraction error: {str(e)}'
        }


def extract_text_from_bytes(file_bytes, file_extension):
    """
    Extract text from file bytes

    Args:
        file_bytes: File content as bytes
        file_extension: File extension (e.g., 'pdf', 'docx', 'txt')

    Returns:
        dict: Same format as extract_text
    """
    # Normalize extension
    ext = file_extension.lower().lstrip('.')

    if ext not in BYTES_EXTRACTORS:
        return {
            'text': '',
            'success': False,
            'file_type': 'unknown',
            'error': f'Unsupported file format: {ext}'
        }

    # Use appropriate extractor
    extractor = BYTES_EXTRACTORS[ext]

    try:
        result = extractor(file_bytes)
        result['file_type'] = ext
        return result

    except Exception as e:
        return {
            'text': '',
            'success': False,
            'file_type': ext,
            'error': f'Extraction error: {str(e)}'
        }


def is_supported_format(file_path_or_extension):
    """
    Check if file format is supported

    Args:
        file_path_or_extension: File path or extension

    Returns:
        bool: True if supported
    """
    if isinstance(file_path_or_extension, Path):
        extension = file_path_or_extension.suffix.lower()
    else:
        extension = str(file_path_or_extension).lower()
        if not extension.startswith('.'):
            extension = '.' + extension

    return extension in EXTRACTORS


def get_supported_formats():
    """
    Get list of supported file formats

    Returns:
        list: List of supported extensions
    """
    return list(EXTRACTORS.keys())
