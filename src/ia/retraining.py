"""
Sistema de re-entrenamiento del modelo con feedback de usuarios.
Permite mejorar el modelo usando correcciones reales.
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class RetrainingPipeline:
    """
    Pipeline para re-entrenar el modelo con datos de feedback.
    """

    def __init__(self):
        self.feedback_file = "logs/user_feedback.jsonl"
        self.predictions_file = "logs/predictions.jsonl"

    def collect_feedback_data(self, min_days: int = 30) -> pd.DataFrame:
        """
        Recolecta datos de feedback para re-entrenamiento.

        Args:
            min_days: Mínimo de días de datos requeridos

        Returns:
            DataFrame con texto y etiquetas corregidas
        """
        if not os.path.exists(self.feedback_file):
            print("[WARNING] No hay archivo de feedback")
            return pd.DataFrame()

        cutoff_date = datetime.now() - timedelta(days=min_days)
        feedback_entries = []

        with open(self.feedback_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    entry_date = datetime.fromisoformat(entry.get("timestamp", ""))

                    if entry_date >= cutoff_date:
                        feedback_entries.append(entry)
                except Exception:
                    continue

        if not feedback_entries:
            print(f"[WARNING] No hay feedback en los últimos {min_days} días")
            return pd.DataFrame()

        # Buscar el texto original en predictions.jsonl
        feedback_with_text = []

        for feedback in feedback_entries:
            file_path = feedback.get("file_path")
            text_preview = self._find_text_for_file(file_path)

            if text_preview:
                feedback_with_text.append({
                    "text": text_preview,
                    "label": feedback.get("actual_type"),  # Etiqueta corregida
                    "original_prediction": feedback.get("predicted_type"),
                    "timestamp": feedback.get("timestamp")
                })

        if not feedback_with_text:
            print("[WARNING] No se pudo recuperar texto para ningún feedback")
            return pd.DataFrame()

        df = pd.DataFrame(feedback_with_text)
        print(f"[INFO] Recolectados {len(df)} ejemplos de feedback con texto")

        return df

    def _find_text_for_file(self, file_path: str) -> str:
        """Busca el texto original en el log de predicciones."""
        if not os.path.exists(self.predictions_file):
            return ""

        with open(self.predictions_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("file") == os.path.basename(file_path):
                        return entry.get("text_preview", "")
                except Exception:
                    continue

        return ""

    def prepare_retraining_dataset(
        self,
        feedback_df: pd.DataFrame,
        original_train_path: str = "src/ia/datasets/processed/train.csv"
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Prepara dataset para re-entrenamiento combinando feedback con datos originales.

        Args:
            feedback_df: DataFrame con feedback de usuarios
            original_train_path: Ruta al dataset de entrenamiento original

        Returns:
            Tupla (train_df, val_df, test_df)
        """
        print("\n" + "=" * 70)
        print("PREPARANDO DATASET PARA RE-ENTRENAMIENTO")
        print("=" * 70)

        # Cargar datos originales
        if os.path.exists(original_train_path):
            original_df = pd.read_csv(original_train_path)
            print(f"[INFO] Cargados {len(original_df)} ejemplos originales")
        else:
            print("[WARNING] No se encontró dataset original")
            original_df = pd.DataFrame()

        # Validar feedback
        if feedback_df.empty:
            print("[WARNING] No hay datos de feedback")
            return original_df, pd.DataFrame(), pd.DataFrame()

        # Estadísticas del feedback
        print(f"\n[INFO] Feedback recolectado:")
        print(f"   - Total ejemplos: {len(feedback_df)}")
        print(f"   - Distribución por clase:")
        for label, count in feedback_df['label'].value_counts().items():
            print(f"     * {label}: {count}")

        # Combinar datasets
        if not original_df.empty:
            # Asegurar mismas columnas
            feedback_df = feedback_df[['text', 'label']]
            combined_df = pd.concat([original_df, feedback_df], ignore_index=True)
            print(f"\n[INFO] Dataset combinado: {len(combined_df)} ejemplos")
        else:
            combined_df = feedback_df[['text', 'label']]

        # Split 70/15/15
        from sklearn.model_selection import train_test_split

        train_df, temp_df = train_test_split(
            combined_df,
            test_size=0.3,
            stratify=combined_df['label'],
            random_state=42
        )

        val_df, test_df = train_test_split(
            temp_df,
            test_size=0.5,
            stratify=temp_df['label'],
            random_state=42
        )

        print(f"\n[INFO] Split realizado:")
        print(f"   - Train: {len(train_df)} ({len(train_df)/len(combined_df)*100:.1f}%)")
        print(f"   - Val: {len(val_df)} ({len(val_df)/len(combined_df)*100:.1f}%)")
        print(f"   - Test: {len(test_df)} ({len(test_df)/len(combined_df)*100:.1f}%)")

        return train_df, val_df, test_df

    def retrain_model(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame,
        model_name: str = None
    ) -> Dict:
        """
        Re-entrena el modelo con los nuevos datos.

        Args:
            train_df, val_df, test_df: Datasets
            model_name: Nombre para el nuevo modelo (auto-generado si None)

        Returns:
            Dict con métricas y ruta del modelo
        """
        if model_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name = f"tfidf_svm_retrained_{timestamp}"

        print("\n" + "=" * 70)
        print(f"RE-ENTRENANDO MODELO: {model_name}")
        print("=" * 70)

        # Guardar datasets temporales
        temp_dir = "src/ia/datasets/retraining"
        os.makedirs(temp_dir, exist_ok=True)

        train_path = os.path.join(temp_dir, "train.csv")
        val_path = os.path.join(temp_dir, "val.csv")
        test_path = os.path.join(temp_dir, "test.csv")

        train_df.to_csv(train_path, index=False)
        val_df.to_csv(val_path, index=False)
        test_df.to_csv(test_path, index=False)

        # Entrenar usando el pipeline existente
        from src.ia.training.train_model import train_tfidf_svm

        model, vectorizer, metadata = train_tfidf_svm(
            train_df=train_df,
            val_df=val_df,
            max_features=5000,
            ngram_range=(1, 2),
            C=1.0
        )

        # Guardar modelo
        import joblib

        model_dir = os.path.join("src/ia/models", model_name)
        os.makedirs(model_dir, exist_ok=True)

        joblib.dump(model, os.path.join(model_dir, "model.pkl"))
        joblib.dump(vectorizer, os.path.join(model_dir, "vectorizer.pkl"))

        with open(os.path.join(model_dir, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\n[SUCCESS] Modelo guardado en: {model_dir}")

        return {
            "model_name": model_name,
            "model_path": model_dir,
            "metrics": metadata.get("metrics", {}),
            "train_size": len(train_df),
            "val_size": len(val_df),
            "test_size": len(test_df)
        }

    def auto_retrain_if_needed(
        self,
        min_feedback_count: int = 50,
        min_accuracy_drop: float = 0.05
    ) -> bool:
        """
        Determina si es necesario re-entrenar automáticamente.

        Args:
            min_feedback_count: Mínimo de feedback para re-entrenar
            min_accuracy_drop: Mínimo drop de accuracy para re-entrenar

        Returns:
            True si se debe re-entrenar
        """
        # Contar feedback
        if not os.path.exists(self.feedback_file):
            return False

        feedback_count = 0
        correct_count = 0

        with open(self.feedback_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    feedback_count += 1
                    if entry.get("was_correct"):
                        correct_count += 1
                except Exception:
                    continue

        if feedback_count < min_feedback_count:
            print(f"[INFO] Solo {feedback_count}/{min_feedback_count} feedback. No re-entrenar aún.")
            return False

        # Calcular accuracy del feedback
        current_accuracy = correct_count / feedback_count if feedback_count > 0 else 1.0

        # Comparar con accuracy esperada (del modelo actual)
        try:
            with open("src/ia/models/tfidf_svm_v1/metadata.json", 'r') as f:
                metadata = json.load(f)
                expected_accuracy = metadata.get("metrics", {}).get("test_accuracy", 1.0)
        except Exception:
            expected_accuracy = 0.9  # Default

        accuracy_drop = expected_accuracy - current_accuracy

        print(f"\n[INFO] Análisis de re-entrenamiento:")
        print(f"   - Feedback total: {feedback_count}")
        print(f"   - Accuracy actual: {current_accuracy:.2%}")
        print(f"   - Accuracy esperada: {expected_accuracy:.2%}")
        print(f"   - Drop: {accuracy_drop:.2%}")

        if accuracy_drop >= min_accuracy_drop:
            print(f"[WARNING] Drop de accuracy >= {min_accuracy_drop:.2%}. RE-ENTRENAR RECOMENDADO.")
            return True

        print(f"[INFO] Modelo funcionando bien. No re-entrenar aún.")
        return False


# Función de utilidad para uso rápido
def quick_retrain(min_feedback_days: int = 30) -> Dict:
    """
    Re-entrena el modelo rápidamente con feedback disponible.

    Args:
        min_feedback_days: Días mínimos de feedback a usar

    Returns:
        Dict con resultados del re-entrenamiento
    """
    pipeline = RetrainingPipeline()

    # Recolectar feedback
    feedback_df = pipeline.collect_feedback_data(min_days=min_feedback_days)

    if feedback_df.empty:
        return {"error": "No hay feedback suficiente para re-entrenar"}

    # Preparar dataset
    train_df, val_df, test_df = pipeline.prepare_retraining_dataset(feedback_df)

    if train_df.empty:
        return {"error": "No se pudo preparar dataset de re-entrenamiento"}

    # Re-entrenar
    result = pipeline.retrain_model(train_df, val_df, test_df)

    return result
