import os
import sys
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import request, current_app

# Add ai_directia to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'ai_directia'))

from ai_directia.inference.classifier import DocumentClassifier

# Initialize classifier (singleton pattern)
_classifier = None


def get_classifier():
    """
    Get or initialize the classifier (singleton)

    Returns:
        DocumentClassifier instance or None if initialization fails
    """
    global _classifier

    if _classifier is None:
        try:
            # Path to model and config relative to FlaskServerTFG root
            model_dir = str(Path(__file__).parent.parent.parent / 'ai_directia' / 'models' / 'v1_tfidf_svm')
            config_path = str(Path(__file__).parent.parent.parent / 'ai_directia' / 'config' / 'categories.json')

            _classifier = DocumentClassifier(
                model_dir=model_dir,
                config_path=config_path
            )
            print("[OK] AI Classifier initialized successfully")
        except Exception as e:
            print(f"[ERROR] Could not initialize AI classifier: {e}")
            _classifier = None

    return _classifier


def clasificar_documento(file):
    """
    Servicio de clasificación de documentos con IA robusta.

    Espera:
        - file: archivo multipart
        - user (opcional): nombre de usuario para personalizar carpeta sugerida

    Retorna:
        - success: True/False
        - tipo_documento: categoría del documento
        - tipo_documento_en: categoría en inglés
        - category_id: ID de la categoría
        - confianza: nivel de confianza (0-1)
        - confidence_level: high/medium/low
        - carpeta_sugerida: ruta sugerida para guardar el documento
        - carpeta_existe: indica si la carpeta sugerida ya existe
        - descripcion: descripción de la categoría
        - top_predictions: lista de las 3 mejores predicciones
        - metadata: información sobre el archivo procesado
    """
    if not file:
        return {"success": False, "error": "No se subió archivo"}, 400

    # Get classifier
    classifier = get_classifier()

    if classifier is None:
        return {
            "success": False,
            "error": "El sistema de clasificación IA no está disponible. El modelo no está entrenado."
        }, 503

    # Get username from request (if exists)
    username = request.form.get('user', 'usuario')

    if file.filename == '':
        print(f"[IA ERROR] Nombre de archivo vacío")
        return {"success": False, "error": "No se seleccionó ningún archivo"}, 400

    try:
        # Read file content
        print(f"[IA] Clasificando archivo: {file.filename} para usuario: {username}")
        file_bytes = file.read()
        print(f"[IA] Bytes leídos: {len(file_bytes)}")

        # Get file extension
        file_extension = os.path.splitext(file.filename)[1].lstrip('.')

        # Validate file extension
        if not file_extension:
            return {"success": False, "error": "El archivo no tiene extensión"}, 400

        # Classify document
        resultado = classifier.classify_file_bytes(
            file_bytes=file_bytes,
            file_extension=file_extension,
            file_name=file.filename
        )

        # Check if classification failed
        if 'error' in resultado:
            return {"success": False, "error": resultado['error']}, 400

        # Adjust suggested folder to include username
        if 'carpeta_sugerida' in resultado:
            carpeta = resultado['carpeta_sugerida']
            # Replace /Documentos/ with /username/Documentos/
            if carpeta.startswith('/Documentos/'):
                resultado['carpeta_sugerida'] = f'/{username}{carpeta}'

        # Check if suggested folder exists
        carpeta_sugerida = resultado.get("carpeta_sugerida", "")
        carpeta_existe = False

        if carpeta_sugerida and username:
            # Get storage path
            storage_path = current_app.config.get("STORAGE_PATH", "./storage/files")
            # Suggested folder comes as /username/Documentos/Facturas
            # We need to build the physical path
            carpeta_relativa = carpeta_sugerida.lstrip('/')
            carpeta_fisica = os.path.join(storage_path, carpeta_relativa)
            carpeta_existe = os.path.exists(carpeta_fisica) and os.path.isdir(carpeta_fisica)

            print(f"[IA] Carpeta sugerida: {carpeta_sugerida}")
            print(f"[IA] Carpeta física: {carpeta_fisica}")
            print(f"[IA] Existe: {carpeta_existe}")

        # Add folder existence information
        resultado["carpeta_existe"] = carpeta_existe

        # Add success flag
        resultado['success'] = True

        return resultado, 200

    except ValueError as e:
        # Text extraction error
        return {
            "success": False,
            "error": f"Error al procesar el archivo: {str(e)}"
        }, 400

    except Exception as e:
        # General error
        print(f"[ERROR] Classification error: {str(e)}")
        return {
            "success": False,
            "error": f"Error interno: {str(e)}"
        }, 500
