"""
PDF text extraction module
"""

import pdfplumber
from pathlib import Path


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file using pdfplumber

    Args:
        file_path: Path to the PDF file

    Returns:
        dict: {
            'text': extracted text,
            'success': bool,
            'pages': number of pages,
            'error': error message if any
        }
    """
    try:
        text_content = []
        file_path = Path(file_path)

        if not file_path.exists():
            return {
                'text': '',
                'success': False,
                'pages': 0,
                'error': f'File not found: {file_path}'
            }

        with pdfplumber.open(file_path) as pdf:
            num_pages = len(pdf.pages)

            for page_num, page in enumerate(pdf.pages, start=1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                except Exception as e:
                    print(f"Warning: Could not extract text from page {page_num}: {e}")
                    continue

            full_text = '\n\n'.join(text_content)

            return {
                'text': full_text,
                'success': True,
                'pages': num_pages,
                'error': None
            }

    except Exception as e:
        return {
            'text': '',
            'success': False,
            'pages': 0,
            'error': str(e)
        }


def extract_text_from_pdf_bytes(pdf_bytes):
    """
    Extract text from PDF file bytes

    Args:
        pdf_bytes: PDF file content as bytes

    Returns:
        dict: Same format as extract_text_from_pdf
    """
    import io

    try:
        text_content = []

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            num_pages = len(pdf.pages)

            for page_num, page in enumerate(pdf.pages, start=1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                except Exception as e:
                    print(f"Warning: Could not extract text from page {page_num}: {e}")
                    continue

            full_text = '\n\n'.join(text_content)

            return {
                'text': full_text,
                'success': True,
                'pages': num_pages,
                'error': None
            }

    except Exception as e:
        return {
            'text': '',
            'success': False,
            'pages': 0,
            'error': str(e)
        }
