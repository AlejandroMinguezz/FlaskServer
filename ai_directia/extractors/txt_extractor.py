"""
TXT text extraction module
"""

from pathlib import Path


def extract_text_from_txt(file_path, encoding='utf-8'):
    """
    Extract text from a plain text file

    Args:
        file_path: Path to the text file
        encoding: File encoding (default: utf-8)

    Returns:
        dict: {
            'text': extracted text,
            'success': bool,
            'lines': number of lines,
            'error': error message if any
        }
    """
    try:
        file_path = Path(file_path)

        if not file_path.exists():
            return {
                'text': '',
                'success': False,
                'lines': 0,
                'error': f'File not found: {file_path}'
            }

        # Try to read with specified encoding
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                text = f.read()
        except UnicodeDecodeError:
            # Fallback to latin-1 if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as f:
                text = f.read()

        lines = text.split('\n')
        num_lines = len(lines)

        return {
            'text': text,
            'success': True,
            'lines': num_lines,
            'error': None
        }

    except Exception as e:
        return {
            'text': '',
            'success': False,
            'lines': 0,
            'error': str(e)
        }


def extract_text_from_txt_bytes(txt_bytes, encoding='utf-8'):
    """
    Extract text from text file bytes

    Args:
        txt_bytes: Text file content as bytes
        encoding: File encoding (default: utf-8)

    Returns:
        dict: Same format as extract_text_from_txt
    """
    try:
        # Try to decode with specified encoding
        try:
            text = txt_bytes.decode(encoding)
        except UnicodeDecodeError:
            # Fallback to latin-1 if UTF-8 fails
            text = txt_bytes.decode('latin-1')

        lines = text.split('\n')
        num_lines = len(lines)

        return {
            'text': text,
            'success': True,
            'lines': num_lines,
            'error': None
        }

    except Exception as e:
        return {
            'text': '',
            'success': False,
            'lines': 0,
            'error': str(e)
        }
