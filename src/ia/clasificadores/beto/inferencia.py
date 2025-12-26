import re
from datetime import datetime
from typing import Tuple
from src.ia.classifier import DocumentClassifier


# Instancia global del clasificador (se carga una sola vez)
_classifier = None


def get_classifier():
    """Obtiene la instancia del clasificador (singleton)."""
    global _classifier
    if _classifier is None:
        _classifier = DocumentClassifier()
    return _classifier


def _extract_info_from_text(text: str, doc_type: str) -> dict:
    """
    Extrae información relevante del texto según el tipo de documento.

    Args:
        text: Texto del documento
        doc_type: Tipo de documento clasificado

    Returns:
        Dict con información extraída (números, fechas, nombres, etc.)
    """
    info = {
        "numeros": [],
        "fechas": [],
        "nombres": []
    }

    # Extraer números (posibles números de factura, recibo, etc.)
    numeros = re.findall(r'\b\d{3,}\b', text)
    if numeros:
        info["numeros"] = numeros[:3]  # Máximo 3 números

    # Extraer fechas en varios formatos
    fechas = re.findall(
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
        text
    )
    if fechas:
        info["fechas"] = fechas[:2]  # Máximo 2 fechas

    # Para CVs, intentar extraer nombre (primeras palabras en mayúsculas)
    if doc_type == "cv":
        lines = text.split('\n')[:5]  # Primeras 5 líneas
        for line in lines:
            # Buscar nombres (palabras capitalizadas)
            nombres = re.findall(r'\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*\b', line)
            if nombres:
                info["nombres"].extend(nombres[:2])
                break

    return info


def _generate_filename(doc_type: str, text: str, info: dict) -> str:
    """
    Genera un nombre de archivo sugerido basado en el tipo de documento.

    Args:
        doc_type: Tipo de documento
        text: Texto completo del documento
        info: Información extraída del texto

    Returns:
        Nombre de archivo sugerido
    """
    timestamp = datetime.now().strftime("%Y%m%d")

    # Mapeo de tipos a prefijos
    prefijos = {
        "factura": "Factura",
        "recibo": "Recibo",
        "cv": "CV",
        "pagare": "Pagare",
        "contrato": "Contrato",
        "otro": "Documento"
    }

    prefijo = prefijos.get(doc_type, "Documento")

    # Generar nombre según el tipo
    if doc_type in ["factura", "recibo", "pagare"]:
        # Usar número si está disponible
        if info["numeros"]:
            numero = info["numeros"][0]
            return f"{prefijo}_{numero}.pdf"
        else:
            return f"{prefijo}_{timestamp}.pdf"

    elif doc_type == "cv":
        # Usar nombre de la persona si está disponible
        if info["nombres"]:
            nombre = info["nombres"][0].replace(" ", "_")
            return f"CV_{nombre}.pdf"
        else:
            return f"CV_{timestamp}.pdf"

    elif doc_type == "contrato":
        # Usar fecha si está disponible
        if info["fechas"]:
            fecha = info["fechas"][0].replace("/", "-")
            return f"Contrato_{fecha}.pdf"
        else:
            return f"Contrato_{timestamp}.pdf"

    else:
        # Genérico
        return f"{prefijo}_{timestamp}.pdf"


def _generate_folder(doc_type: str) -> str:
    """
    Genera una ruta de carpeta sugerida basada en el tipo de documento.

    Args:
        doc_type: Tipo de documento

    Returns:
        Ruta de carpeta sugerida
    """
    carpetas = {
        "factura": "/Documentos/Facturas/",
        "recibo": "/Documentos/Recibos/",
        "cv": "/Recursos_Humanos/CVs/",
        "pagare": "/Finanzas/Pagares/",
        "contrato": "/Legal/Contratos/",
        "otro": "/Documentos/Otros/"
    }

    return carpetas.get(doc_type, "/Documentos/")


def ejecutar_beto(texto: str) -> Tuple[str, float, str, str]:
    """
    Función de inferencia para el clasificador BETO.
    Dado un texto, devuelve la clasificación, confianza, nombre sugerido y carpeta sugerida.

    Args:
        texto: Texto extraído del documento mediante OCR

    Returns:
        Tupla con (tipo, confianza, nombre_sugerido, carpeta_sugerida)
    """
    if not texto or not texto.strip():
        return "desconocido", 0.0, "Documento_sin_texto.pdf", "/Documentos/"

    try:
        # Obtener clasificador
        classifier = get_classifier()

        # Clasificar el texto
        resultado = classifier.classify_text(texto)
        tipo = resultado["tipo"]
        confianza = resultado["confianza"]

        # Extraer información del texto
        info = _extract_info_from_text(texto, tipo)

        # Generar nombre y carpeta sugeridos
        nombre_sugerido = _generate_filename(tipo, texto, info)
        carpeta_sugerida = _generate_folder(tipo)

        # Capitalizar tipo para respuesta
        tipo_capitalizado = tipo.capitalize()

        return tipo_capitalizado, confianza, nombre_sugerido, carpeta_sugerida

    except Exception as e:
        print(f"[ERROR] Error en ejecutar_beto: {e}")
        return "Error", 0.0, "Documento_error.pdf", "/Documentos/"