import os
import time
from src.ia.ocr import extract_text
from src.ia.utils import clean_text
from src.ia.classifier_ml import MLDocumentClassifier
from src.ia.classifier_optimized import DocumentClassifier
from src.ia.logger import get_logger


# Inicializar logger
logger = get_logger()

# Inicializar clasificadores (primero ML, luego keywords como fallback)
classifier_type = "keywords"  # Default
try:
    classifier_ml = MLDocumentClassifier(model_name="tfidf_svm_v1")
    print("[INFO] Usando clasificador ML (TF-IDF + SVM)")
    classifier = classifier_ml
    classifier_type = "ml"
except Exception as e:
    print(f"[WARNING] Error al cargar clasificador ML: {e}")
    print("[INFO] Usando clasificador optimizado basado en keywords como fallback")
    classifier = DocumentClassifier()
    classifier_type = "keywords"


def analizar_documento(file_path: str, username: str = None):
    """
    Analiza un documento y retorna su clasificación.

    Args:
        file_path: Ruta al archivo a analizar
        username: Usuario que sube el archivo (para personalizar carpeta_sugerida)

    Returns:
        Dict con tipo_documento, confianza y carpeta_sugerida
    """
    start_time = time.time()

    if not os.path.exists(file_path):
        logger.log_error(file_path, "Archivo no encontrado", username, "file_not_found")
        return {"error": "Archivo no encontrado"}

    try:
        # Extraer texto (soporta PDF, DOCX, TXT, imágenes)
        raw_text = extract_text(file_path)

        # Limpieza de texto
        text = clean_text(raw_text)

        if not text.strip():
            result = {
                "tipo_documento": "desconocido",
                "confianza": 0.0,
                "carpeta_sugerida": "/Documentos/Otros"
            }

            # Log empty document
            logger.log_prediction(
                file_path=file_path,
                predicted_type="desconocido",
                confidence=0.0,
                username=username,
                suggested_folder=result["carpeta_sugerida"],
                text_preview="[documento vacío]",
                processing_time=time.time() - start_time,
                classifier_type=classifier_type
            )

            return result

        # Clasificar con username para generar carpeta personalizada
        resultado = classifier.classify_text(text, username=username)

        # Log successful prediction
        processing_time = time.time() - start_time
        logger.log_prediction(
            file_path=file_path,
            predicted_type=resultado.get("tipo_documento", "unknown"),
            confidence=resultado.get("confianza", 0.0),
            username=username,
            suggested_folder=resultado.get("carpeta_sugerida"),
            text_preview=text,
            processing_time=processing_time,
            classifier_type=classifier_type
        )

        print(f"[INFO] Documento clasificado: {resultado['tipo_documento']} "
              f"(confianza: {resultado['confianza']:.2f}, tiempo: {processing_time:.2f}s)")

        return resultado

    except Exception as e:
        # Log error
        logger.log_error(file_path, str(e), username, "classification_error")
        return {"error": f"Error en pipeline: {str(e)}"}
