from flask import Blueprint, request, jsonify
from src.services import ia as ia_service

bp = Blueprint("ia", __name__, url_prefix="/api")


@bp.route("/clasificar", methods=["POST"])
def clasificar():
    """
    Endpoint para clasificar documentos con IA.
    Espera un archivo multipart y devuelve el tipo de documento,
    confianza y carpeta sugerida.
    """
    file = request.files.get("file")
    if not file:
        return jsonify({"success": False, "error": "No se proporcionó archivo"}), 400

    result, status = ia_service.clasificar_documento(file)
    return jsonify(result), status


@bp.route("/clasificar/categorias", methods=["GET"])
def obtener_categorias():
    """
    Get list of available categories

    Response:
        {
            "success": true,
            "categories": [
                {
                    "id": "factura",
                    "name": "Factura",
                    "name_en": "Invoice",
                    "folder_path": "/Documentos/Facturas/",
                    "description": "Documentos de facturación..."
                },
                ...
            ],
            "total": 9
        }
    """
    classifier = ia_service.get_classifier()

    if classifier is None:
        return jsonify({
            'success': False,
            'error': 'El sistema de clasificación IA no está disponible'
        }), 503

    try:
        categories = classifier.get_categories()
        return jsonify({
            'success': True,
            'categories': categories,
            'total': len(categories)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route("/clasificar/info", methods=["GET"])
def obtener_info_modelo():
    """
    Get information about the AI model

    Response:
        {
            "success": true,
            "model_info": {
                "model_type": "SVC",
                "training_date": "2025-01-15T10:30:00",
                "vocabulary_size": 5000,
                "num_categories": 9,
                "metrics": {
                    "test": {
                        "accuracy": 1.0,
                        "f1_macro": 1.0,
                        "f1_weighted": 1.0
                    }
                }
            }
        }
    """
    classifier = ia_service.get_classifier()

    if classifier is None:
        return jsonify({
            'success': False,
            'error': 'El sistema de clasificación IA no está disponible'
        }), 503

    try:
        info = classifier.get_model_info()
        return jsonify({
            'success': True,
            'model_info': info
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route("/clasificar/health", methods=["GET"])
def health_check():
    """
    Health check for AI classification system

    Response:
        {
            "success": true,
            "status": "operational",
            "classifier_loaded": true,
            "message": "AI classification system is operational"
        }
    """
    classifier = ia_service.get_classifier()

    if classifier is None:
        return jsonify({
            'success': False,
            'status': 'unavailable',
            'classifier_loaded': False,
            'message': 'AI classifier not initialized. Model may not be trained.'
        }), 503

    return jsonify({
        'success': True,
        'status': 'operational',
        'classifier_loaded': True,
        'message': 'AI classification system is operational'
    }), 200


# Error handlers
@bp.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'El archivo es demasiado grande. Tamaño máximo: 16MB'
    }), 413


@bp.errorhandler(500)
def internal_server_error(error):
    """Handle internal server error"""
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500
