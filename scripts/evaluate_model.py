"""
Script para evaluar el modelo de clasificación.

Uso:
    python scripts/evaluate_model.py --model tfidf_svm_v1
    python scripts/evaluate_model.py --validation validation.csv
    python scripts/evaluate_model.py --compare
"""

import sys
import os
import argparse

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ia.evaluation import (
    ModelEvaluator,
    create_validation_template,
    evaluate_from_validation_file
)


def main():
    parser = argparse.ArgumentParser(description="Evaluar modelo de clasificación")

    parser.add_argument(
        "--model",
        default="tfidf_svm_v1",
        help="Nombre del modelo a evaluar"
    )

    parser.add_argument(
        "--validation",
        help="Archivo CSV con validaciones manuales"
    )

    parser.add_argument(
        "--create-template",
        action="store_true",
        help="Crear plantilla de validación"
    )

    parser.add_argument(
        "--compare",
        action="store_true",
        help="Comparar sintéticos vs reales"
    )

    parser.add_argument(
        "--output",
        default="validation_template.csv",
        help="Archivo de salida para plantilla"
    )

    args = parser.parse_args()

    # Crear plantilla
    if args.create_template:
        create_validation_template(args.output)
        return

    # Evaluar desde archivo de validación
    if args.validation:
        print(f"\nEvaluando modelo {args.model} con validaciones de {args.validation}")
        results = evaluate_from_validation_file(args.validation, args.model)

        if "error" in results:
            print(f"\n❌ Error: {results['error']}")
        else:
            print(f"\n✅ Evaluación completada")
            print(f"\nResultados guardados en memoria")

        return

    # Evaluación estándar
    evaluator = ModelEvaluator(model_name=args.model)

    # Comparación
    if args.compare:
        import pandas as pd

        # Intentar cargar datos reales desde feedback
        feedback_file = "logs/user_feedback.jsonl"

        if os.path.exists(feedback_file):
            print("\n📂 Cargando datos reales desde feedback...")

            import json
            entries = []

            with open(feedback_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        # Buscar texto en predictions.jsonl
                        # (simplificado - en producción usar método completo)
                        entries.append({
                            "text": entry.get("comment", ""),
                            "label": entry.get("actual_type")
                        })
                    except Exception:
                        continue

            if entries:
                real_df = pd.DataFrame(entries)
                real_df = real_df[real_df['text'] != '']

                results = evaluator.compare_synthetic_vs_real(
                    real_test_df=real_df
                )
            else:
                print("\n⚠️ No hay datos reales suficientes")
        else:
            print("\n⚠️ No hay archivo de feedback")

    else:
        # Evaluación en sintéticos
        import pandas as pd

        test_path = "src/ia/datasets/processed/test.csv"

        if os.path.exists(test_path):
            test_df = pd.read_csv(test_path)
            results = evaluator.evaluate_on_dataset(test_df)

            # Identificar categorías débiles
            weak_cats = evaluator.identify_weak_categories(test_df, threshold=0.8)

        else:
            print(f"\n❌ No se encontró dataset de test en {test_path}")


if __name__ == "__main__":
    main()
