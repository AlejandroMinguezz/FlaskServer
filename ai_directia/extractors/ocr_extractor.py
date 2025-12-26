"""
OCR text extraction module for images
"""

import pytesseract
from PIL import Image
from pathlib import Path
import io


def extract_text_from_image(file_path, lang='spa+eng'):
    """
    Extract text from an image using OCR (Tesseract)

    Args:
        file_path: Path to the image file
        lang: Language(s) for OCR (default: 'spa+eng' for Spanish and English)

    Returns:
        dict: {
            'text': extracted text,
            'success': bool,
            'confidence': OCR confidence score (if available),
            'error': error message if any
        }
    """
    try:
        file_path = Path(file_path)

        if not file_path.exists():
            return {
                'text': '',
                'success': False,
                'confidence': 0,
                'error': f'File not found: {file_path}'
            }

        # Open image
        image = Image.open(file_path)

        # Perform OCR
        text = pytesseract.image_to_string(image, lang=lang)

        # Get OCR data for confidence
        try:
            ocr_data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in ocr_data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        except:
            avg_confidence = 0

        return {
            'text': text.strip(),
            'success': True,
            'confidence': round(avg_confidence, 2),
            'error': None
        }

    except pytesseract.TesseractNotFoundError:
        return {
            'text': '',
            'success': False,
            'confidence': 0,
            'error': 'Tesseract OCR is not installed or not in PATH. Please install Tesseract.'
        }
    except Exception as e:
        return {
            'text': '',
            'success': False,
            'confidence': 0,
            'error': str(e)
        }


def extract_text_from_image_bytes(image_bytes, lang='spa+eng'):
    """
    Extract text from image bytes using OCR

    Args:
        image_bytes: Image file content as bytes
        lang: Language(s) for OCR (default: 'spa+eng')

    Returns:
        dict: Same format as extract_text_from_image
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Perform OCR
        text = pytesseract.image_to_string(image, lang=lang)

        # Get OCR data for confidence
        try:
            ocr_data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in ocr_data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        except:
            avg_confidence = 0

        return {
            'text': text.strip(),
            'success': True,
            'confidence': round(avg_confidence, 2),
            'error': None
        }

    except pytesseract.TesseractNotFoundError:
        return {
            'text': '',
            'success': False,
            'confidence': 0,
            'error': 'Tesseract OCR is not installed or not in PATH. Please install Tesseract.'
        }
    except Exception as e:
        return {
            'text': '',
            'success': False,
            'confidence': 0,
            'error': str(e)
        }


def set_tesseract_path(path):
    """
    Set custom path to Tesseract executable

    Args:
        path: Path to tesseract executable
    """
    pytesseract.pytesseract.tesseract_cmd = path
