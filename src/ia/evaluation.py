"""
Herramientas para evaluar modelos con datos reales.
Permite comparar performance en documentos sintéticos vs reales.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)


class ModelEvaluator:
    """
    Evaluador de modelos de clasificación.
    """

    def __init__(self, model_name: str = "tfidf_svm_v1"):
        """
        Args:
            model_name: Nombre del modelo a evaluar
        """
        self.model_name = model_name
        self.classifier = None
        self._load_classifier()

    def _load_classifier(self):
        """Carga el clasificador a evaluar."""
        try:
            from src.ia.classifier_ml import MLDocumentClassifier
            self.classifier = MLDocumentClassifier(model_name=self.model_name)
            print(f"[INFO] Clasificador {self.model_name} cargado para evaluación")
        except Exception as e:
            print(f"[ERROR] No se pudo cargar clasificador: {e}")

    def evaluate_on_dataset(self, test_df: pd.DataFrame) -> Dict:
        """
        Evalúa el modelo en un dataset de test.

        Args:
            test_df: DataFrame con columnas 'text' y 'label'

        Returns:
            Dict con métricas de evaluación
        """
        if self.classifier is None:
            return {"error": "Clasificador no cargado"}

        if test_df.empty or 'text' not in test_df.columns or 'label' not in test_df.columns:
            return {"error": "Dataset inválido"}

        print("\n" + "=" * 70)
        print(f"EVALUANDO MODELO: {self.model_name}")
        print(f"Dataset: {len(test_df)} ejemplos")
        print("=" * 70)

        # Predecir
        predictions = []
        confidences = []

        from src.ia.utils import clean_text

        for idx, row in test_df.iterrows():
            text = clean_text(row['text'])
            result = self.classifier.classify_text(text)

            predictions.append(result.get('tipo_documento', 'otro'))
            confidences.append(result.get('confianza', 0.0))

        true_labels = test_df['label'].values

        # Calcular métricas
        accuracy = accuracy_score(true_labels, predictions)
        precision, recall, f1, support = precision_recall_fscore_support(
            true_labels,
            predictions,
            average='weighted',
            zero_division=0
        )

        # Matriz de confusión
        cm = confusion_matrix(true_labels, predictions)

        # Reporte por clase
        report = classification_report(
            true_labels,
            predictions,
            output_dict=True,
            zero_division=0
        )

        # Análisis de confianza
        avg_confidence = np.mean(confidences)
        low_confidence = sum(1 for c in confidences if c < 0.6) / len(confidences)
        high_confidence = sum(1 for c in confidences if c > 0.8) / len(confidences)

        results = {
            "model_name": self.model_name,
            "test_size": len(test_df),
            "metrics": {
                "accuracy": round(accuracy, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4)
            },
            "confidence_stats": {
                "average": round(avg_confidence, 4),
                "low_confidence_rate": round(low_confidence, 4),
                "high_confidence_rate": round(high_confidence, 4)
            },
            "confusion_matrix": cm.tolist(),
            "classification_report": report
        }

        # Imprimir resumen
        print(f"\n📊 RESULTADOS:")
        print(f"   Accuracy:  {accuracy:.2%}")
        print(f"   Precision: {precision:.2%}")
        print(f"   Recall:    {recall:.2%}")
        print(f"   F1-Score:  {f1:.2%}")
        print(f"\n📈 CONFIANZA:")
        print(f"   Promedio:       {avg_confidence:.2%}")
        print(f"   Baja (<0.6):    {low_confidence:.2%}")
        print(f"   Alta (>0.8):    {high_confidence:.2%}")

        return results

    def compare_synthetic_vs_real(
        self,
        synthetic_test_path: str = "src/ia/datasets/processed/test.csv",
        real_test_df: pd.DataFrame = None
    ) -> Dict:
        """
        Compara performance en datos sintéticos vs reales.

        Args:
            synthetic_test_path: Ruta al test sintético
            real_test_df: DataFrame con test real

        Returns:
            Dict con comparación de métricas
        """
        print("\n" + "=" * 70)
        print("COMPARACIÓN: SINTÉTICOS VS REALES")
        print("=" * 70)

        results = {"synthetic": {}, "real": {}}

        # Evaluar en sintéticos
        if os.path.exists(synthetic_test_path):
            synthetic_df = pd.read_csv(synthetic_test_path)
            results["synthetic"] = self.evaluate_on_dataset(synthetic_df)
            print("\n✅ Evaluación en datos sintéticos completada")
        else:
            print("\n⚠️ No se encontró dataset sintético")

        # Evaluar en reales
        if real_test_df is not None and not real_test_df.empty:
            results["real"] = self.evaluate_on_dataset(real_test_df)
            print("\n✅ Evaluación en datos reales completada")
        else:
            print("\n⚠️ No hay datos reales para evaluar")

        # Comparación
        if results["synthetic"] and results["real"]:
            print("\n" + "=" * 70)
            print("COMPARACIÓN DE MÉTRICAS")
            print("=" * 70)

            metrics = ["accuracy", "precision", "recall", "f1_score"]
            print(f"\n{'Métrica':<15} {'Sintético':<15} {'Real':<15} {'Diferencia'}")
            print("-" * 60)

            for metric in metrics:
                synth_val = results["synthetic"]["metrics"].get(metric, 0)
                real_val = results["real"]["metrics"].get(metric, 0)
                diff = synth_val - real_val

                print(f"{metric:<15} {synth_val:.4f}{'':<8} {real_val:.4f}{'':<8} {diff:+.4f}")

        return results

    def identify_weak_categories(self, test_df: pd.DataFrame, threshold: float = 0.7) -> List[str]:
        """
        Identifica categorías con bajo performance.

        Args:
            test_df: DataFrame de test
            threshold: Threshold de F1-score para considerar débil

        Returns:
            Lista de categorías débiles
        """
        results = self.evaluate_on_dataset(test_df)

        if "classification_report" not in results:
            return []

        weak_categories = []

        for category, metrics in results["classification_report"].items():
            if category in ['accuracy', 'macro avg', 'weighted avg']:
                continue

            if isinstance(metrics, dict):
                f1 = metrics.get('f1-score', 0)
                if f1 < threshold:
                    weak_categories.append({
                        "category": category,
                        "f1_score": round(f1, 4),
                        "precision": round(metrics.get('precision', 0), 4),
                        "recall": round(metrics.get('recall', 0), 4),
                        "support": metrics.get('support', 0)
                    })

        # Ordenar por F1-score
        weak_categories.sort(key=lambda x: x['f1_score'])

        if weak_categories:
            print("\n⚠️ CATEGORÍAS DÉBILES (F1 < {:.0%}):".format(threshold))
            for cat in weak_categories:
                print(f"   - {cat['category']}: F1={cat['f1_score']:.2%}, "
                      f"Precision={cat['precision']:.2%}, "
                      f"Recall={cat['recall']:.2%}")

        return weak_categories


def create_validation_template(output_file: str = "validation_template.csv"):
    """
    Crea una plantilla CSV para validación manual de documentos reales.

    Args:
        output_file: Nombre del archivo de salida
    """
    template_df = pd.DataFrame({
        "file_path": ["ruta/al/documento1.pdf", "ruta/al/documento2.docx"],
        "text": ["Texto extraído del documento...", "Otro texto..."],
        "predicted_label": ["factura", "nomina"],
        "confidence": [0.85, 0.92],
        "actual_label": ["", ""],  # A rellenar manualmente
        "notes": ["", ""]  # Notas opcionales
    })

    template_df.to_csv(output_file, index=False)
    print(f"[INFO] Plantilla de validación creada: {output_file}")
    print(f"[INFO] Rellena la columna 'actual_label' y guarda para evaluar")


def evaluate_from_validation_file(validation_file: str, model_name: str = "tfidf_svm_v1") -> Dict:
    """
    Evalúa el modelo usando un archivo de validación completado.

    Args:
        validation_file: Archivo CSV con validaciones
        model_name: Modelo a evaluar

    Returns:
        Dict con resultados de evaluación
    """
    if not os.path.exists(validation_file):
        return {"error": "Archivo de validación no encontrado"}

    df = pd.read_csv(validation_file)

    # Filtrar solo filas con actual_label rellenado
    df = df[df['actual_label'].notna() & (df['actual_label'] != '')]

    if df.empty:
        return {"error": "No hay validaciones completadas en el archivo"}

    # Renombrar para evaluar
    df = df.rename(columns={'actual_label': 'label'})

    # Evaluar
    evaluator = ModelEvaluator(model_name=model_name)
    results = evaluator.evaluate_on_dataset(df[['text', 'label']])

    return results
