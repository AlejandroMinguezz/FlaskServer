"""
Endpoints para feedback de usuarios sobre clasificación de documentos.
Permite a los usuarios corregir clasificaciones incorrectas.
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import os

bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')


@bp.route('/submit', methods=['POST'])
def submit_feedback():
    """
    Endpoint para enviar feedback sobre una clasificación.

    Request body:
    {
        "file_path": "documento.pdf",
        "predicted_type": "factura",
        "actual_type": "recibo",
        "confidence": 0.85,
        "username": "user123",
        "comment": "Es un recibo de alquiler, no una factura"
    }

    Returns:
        JSON con confirmación
    """
    try:
        data = request.get_json()

        # Validar campos requeridos
        required_fields = ['file_path', 'predicted_type', 'actual_type']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido: {field}"}), 400

        # Preparar entrada de feedback
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "file_path": data['file_path'],
            "predicted_type": data['predicted_type'],
            "actual_type": data['actual_type'],
            "confidence": data.get('confidence'),
            "username": data.get('username'),
            "comment": data.get('comment', ''),
            "was_correct": data['predicted_type'] == data['actual_type']
        }

        # Guardar en logs de feedback
        from src.ia.logger import get_logger
        logger = get_logger()
        logger.log_prediction(
            file_path=data['file_path'],
            predicted_type=data['predicted_type'],
            confidence=data.get('confidence', 0.0),
            username=data.get('username'),
            user_feedback=data['actual_type']
        )

        # También guardar en archivo separado de feedback
        feedback_file = "logs/user_feedback.jsonl"
        os.makedirs(os.path.dirname(feedback_file), exist_ok=True)

        import json
        with open(feedback_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback_entry, ensure_ascii=False) + '\n')

        return jsonify({
            "status": "success",
            "message": "Feedback recibido correctamente",
            "feedback": feedback_entry
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/stats', methods=['GET'])
def get_feedback_stats():
    """
    Obtiene estadísticas de feedback de usuarios.

    Query params:
        - days: Número de días a analizar (default: 7)

    Returns:
        JSON con estadísticas de feedback
    """
    try:
        days = int(request.args.get('days', 7))

        from src.ia.logger import get_logger
        logger = get_logger()

        # Obtener estadísticas generales
        stats = logger.get_stats(days=days)

        # Obtener feedback específico
        feedback_file = "logs/user_feedback.jsonl"
        feedback_stats = {
            "total_feedback": 0,
            "correct_predictions": 0,
            "incorrect_predictions": 0,
            "accuracy": 0.0,
            "corrections_by_type": {}
        }

        if os.path.exists(feedback_file):
            import json
            from datetime import datetime, timedelta

            cutoff_date = datetime.now() - timedelta(days=days)

            with open(feedback_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry_date = datetime.fromisoformat(entry.get("timestamp", ""))

                        if entry_date < cutoff_date:
                            continue

                        feedback_stats["total_feedback"] += 1

                        if entry.get("was_correct"):
                            feedback_stats["correct_predictions"] += 1
                        else:
                            feedback_stats["incorrect_predictions"] += 1

                            # Track corrections
                            predicted = entry.get("predicted_type")
                            actual = entry.get("actual_type")
                            key = f"{predicted} -> {actual}"

                            if key not in feedback_stats["corrections_by_type"]:
                                feedback_stats["corrections_by_type"][key] = 0
                            feedback_stats["corrections_by_type"][key] += 1

                    except Exception:
                        continue

            # Calcular accuracy
            if feedback_stats["total_feedback"] > 0:
                feedback_stats["accuracy"] = round(
                    feedback_stats["correct_predictions"] / feedback_stats["total_feedback"],
                    4
                )

        return jsonify({
            "period_days": days,
            "general_stats": stats,
            "feedback_stats": feedback_stats
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/export', methods=['GET'])
def export_feedback():
    """
    Exporta feedback para re-entrenamiento.

    Query params:
        - format: csv o jsonl (default: csv)
        - days: Número de días a exportar (default: 30)

    Returns:
        Archivo CSV o JSONL con feedback
    """
    try:
        format_type = request.args.get('format', 'csv').lower()
        days = int(request.args.get('days', 30))

        feedback_file = "logs/user_feedback.jsonl"

        if not os.path.exists(feedback_file):
            return jsonify({"error": "No hay feedback disponible"}), 404

        import json
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        entries = []

        with open(feedback_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    entry_date = datetime.fromisoformat(entry.get("timestamp", ""))

                    if entry_date >= cutoff_date:
                        entries.append(entry)
                except Exception:
                    continue

        if format_type == 'csv':
            import csv
            from io import StringIO

            output = StringIO()
            if entries:
                fieldnames = entries[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(entries)

            from flask import make_response
            response = make_response(output.getvalue())
            response.headers["Content-Disposition"] = f"attachment; filename=feedback_{days}days.csv"
            response.headers["Content-Type"] = "text/csv"
            return response

        else:  # jsonl
            output = '\n'.join(json.dumps(entry, ensure_ascii=False) for entry in entries)

            from flask import make_response
            response = make_response(output)
            response.headers["Content-Disposition"] = f"attachment; filename=feedback_{days}days.jsonl"
            response.headers["Content-Type"] = "application/jsonl"
            return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/problematic-cases', methods=['GET'])
def get_problematic_cases():
    """
    Identifica casos problemáticos (baja confianza, correcciones frecuentes).

    Query params:
        - days: Número de días a analizar (default: 7)
        - min_occurrences: Mínimo de ocurrencias para considerar (default: 2)

    Returns:
        JSON con casos problemáticos
    """
    try:
        days = int(request.args.get('days', 7))
        min_occurrences = int(request.args.get('min_occurrences', 2))

        feedback_file = "logs/user_feedback.jsonl"

        if not os.path.exists(feedback_file):
            return jsonify({"problematic_cases": []}), 200

        import json
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=days)

        # Rastrear errores frecuentes
        error_patterns = {}
        low_confidence_errors = []

        with open(feedback_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    entry_date = datetime.fromisoformat(entry.get("timestamp", ""))

                    if entry_date < cutoff_date:
                        continue

                    if not entry.get("was_correct"):
                        # Rastrear patrón de error
                        predicted = entry.get("predicted_type")
                        actual = entry.get("actual_type")
                        pattern = f"{predicted} -> {actual}"

                        if pattern not in error_patterns:
                            error_patterns[pattern] = 0
                        error_patterns[pattern] += 1

                        # Casos de baja confianza
                        confidence = entry.get("confidence", 0)
                        if confidence < 0.7:
                            low_confidence_errors.append({
                                "file": entry.get("file_path"),
                                "predicted": predicted,
                                "actual": actual,
                                "confidence": confidence,
                                "timestamp": entry.get("timestamp")
                            })

                except Exception:
                    continue

        # Filtrar patrones frecuentes
        frequent_errors = [
            {"pattern": pattern, "count": count}
            for pattern, count in error_patterns.items()
            if count >= min_occurrences
        ]

        # Ordenar por frecuencia
        frequent_errors.sort(key=lambda x: x["count"], reverse=True)

        return jsonify({
            "period_days": days,
            "frequent_error_patterns": frequent_errors,
            "low_confidence_errors": low_confidence_errors[:10],  # Top 10
            "recommendations": _generate_recommendations(frequent_errors)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _generate_recommendations(frequent_errors):
    """Genera recomendaciones basadas en errores frecuentes."""
    recommendations = []

    for error in frequent_errors[:3]:  # Top 3
        pattern = error["pattern"]
        count = error["count"]

        parts = pattern.split(" -> ")
        if len(parts) == 2:
            predicted, actual = parts

            recommendations.append({
                "issue": f"Confusión frecuente: {predicted} clasificado como {actual}",
                "occurrences": count,
                "suggestion": f"Revisar keywords o re-entrenar modelo para distinguir mejor {predicted} de {actual}",
                "priority": "high" if count > 5 else "medium"
            })

    return recommendations
