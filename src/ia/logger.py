"""
Sistema de logging de predicciones para monitoreo de IA en producción.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict


class PredictionLogger:
    """
    Logger para registrar predicciones del sistema de IA.
    Permite tracking de performance y análisis de errores.
    """

    def __init__(self, log_file="logs/predictions.jsonl"):
        """
        Args:
            log_file: Ruta al archivo de log (formato JSONL)
        """
        self.log_file = log_file
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        """Crea el directorio de logs si no existe."""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            print(f"[INFO] Directorio de logs creado: {log_dir}")

    def log_prediction(
        self,
        file_path: str,
        predicted_type: str,
        confidence: float,
        username: Optional[str] = None,
        suggested_folder: Optional[str] = None,
        text_preview: Optional[str] = None,
        user_feedback: Optional[str] = None,
        processing_time: Optional[float] = None,
        classifier_type: str = "ml"
    ) -> None:
        """
        Registra una predicción en el log.

        Args:
            file_path: Ruta del archivo clasificado
            predicted_type: Tipo de documento predicho
            confidence: Confianza de la predicción (0-1)
            username: Usuario que subió el archivo
            suggested_folder: Carpeta sugerida
            text_preview: Preview del texto extraído (primeros 200 chars)
            user_feedback: Feedback del usuario (corrección manual)
            processing_time: Tiempo de procesamiento en segundos
            classifier_type: Tipo de clasificador usado ('ml' o 'keywords')
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "file": os.path.basename(file_path),
            "file_extension": Path(file_path).suffix.lower(),
            "predicted": predicted_type,
            "confidence": round(float(confidence), 4),
            "username": username,
            "suggested_folder": suggested_folder,
            "text_preview": text_preview[:200] if text_preview else None,
            "user_feedback": user_feedback,
            "processing_time_sec": round(processing_time, 3) if processing_time else None,
            "classifier": classifier_type
        }

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"[WARNING] Error al escribir log de predicción: {e}")

    def log_error(
        self,
        file_path: str,
        error_message: str,
        username: Optional[str] = None,
        error_type: str = "classification_error"
    ) -> None:
        """
        Registra un error en el procesamiento.

        Args:
            file_path: Ruta del archivo que causó el error
            error_message: Descripción del error
            username: Usuario que subió el archivo
            error_type: Tipo de error
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "error",
            "file": os.path.basename(file_path),
            "error_type": error_type,
            "error_message": error_message,
            "username": username
        }

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"[WARNING] Error al escribir log de error: {e}")

    def get_stats(self, days: int = 7) -> Dict:
        """
        Obtiene estadísticas de las predicciones de los últimos N días.

        Args:
            days: Número de días a analizar

        Returns:
            Dict con estadísticas
        """
        try:
            from datetime import timedelta

            cutoff_date = datetime.now() - timedelta(days=days)
            stats = {
                "total_predictions": 0,
                "by_type": {},
                "by_confidence": {"low": 0, "medium": 0, "high": 0},
                "avg_confidence": 0.0,
                "errors": 0,
                "with_feedback": 0
            }

            if not os.path.exists(self.log_file):
                return stats

            with open(self.log_file, 'r', encoding='utf-8') as f:
                confidences = []
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry_date = datetime.fromisoformat(entry.get("timestamp", ""))

                        if entry_date < cutoff_date:
                            continue

                        if entry.get("type") == "error":
                            stats["errors"] += 1
                            continue

                        stats["total_predictions"] += 1

                        # Por tipo
                        pred_type = entry.get("predicted", "unknown")
                        stats["by_type"][pred_type] = stats["by_type"].get(pred_type, 0) + 1

                        # Por confianza
                        confidence = entry.get("confidence", 0)
                        confidences.append(confidence)

                        if confidence < 0.6:
                            stats["by_confidence"]["low"] += 1
                        elif confidence < 0.8:
                            stats["by_confidence"]["medium"] += 1
                        else:
                            stats["by_confidence"]["high"] += 1

                        # Feedback
                        if entry.get("user_feedback"):
                            stats["with_feedback"] += 1

                    except Exception as e:
                        continue

                # Calcular promedio de confianza
                if confidences:
                    stats["avg_confidence"] = round(sum(confidences) / len(confidences), 4)

            return stats

        except Exception as e:
            print(f"[WARNING] Error al calcular estadísticas: {e}")
            return {}


# Instancia global del logger
_logger = None


def get_logger(log_file="logs/predictions.jsonl") -> PredictionLogger:
    """
    Obtiene la instancia global del logger (singleton).

    Args:
        log_file: Ruta al archivo de log

    Returns:
        Instancia de PredictionLogger
    """
    global _logger
    if _logger is None:
        _logger = PredictionLogger(log_file)
    return _logger
