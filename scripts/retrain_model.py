"""
Script para re-entrenar el modelo con feedback de usuarios.

Uso:
    python scripts/retrain_model.py
    python scripts/retrain_model.py --days 60
    python scripts/retrain_model.py --check
"""

import sys
import os
import argparse

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ia.retraining import RetrainingPipeline, quick_retrain


def main():
    parser = argparse.ArgumentParser(description="Re-entrenar modelo con feedback")

    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Días de feedback a usar para re-entrenamiento (default: 30)"
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Solo verificar si es necesario re-entrenar"
    )

    parser.add_argument(
        "--auto",
        action="store_true",
        help="Re-entrenar automáticamente si es necesario"
    )

    parser.add_argument(
        "--min-feedback",
        type=int,
        default=50,
        help="Mínimo de feedback para re-entrenar (default: 50)"
    )

    args = parser.parse_args()

    pipeline = RetrainingPipeline()

    # Solo verificar
    if args.check:
        print("\n🔍 Verificando si es necesario re-entrenar...")
        should_retrain = pipeline.auto_retrain_if_needed(
            min_feedback_count=args.min_feedback,
            min_accuracy_drop=0.05
        )

        if should_retrain:
            print("\n✅ RE-ENTRENAMIENTO RECOMENDADO")
            print("   Ejecuta: python scripts/retrain_model.py")
        else:
            print("\n✅ Modelo funcionando bien. No es necesario re-entrenar aún.")

        return

    # Auto re-entrenar si es necesario
    if args.auto:
        print("\n🔄 Verificando si es necesario re-entrenar...")
        should_retrain = pipeline.auto_retrain_if_needed(
            min_feedback_count=args.min_feedback,
            min_accuracy_drop=0.05
        )

        if not should_retrain:
            print("\n✅ Modelo funcionando bien. No re-entrenar.")
            return

        print("\n⚡ Iniciando re-entrenamiento automático...")

    # Re-entrenar
    print(f"\n🚀 Iniciando re-entrenamiento con feedback de últimos {args.days} días...")

    result = quick_retrain(min_feedback_days=args.days)

    if "error" in result:
        print(f"\n❌ Error: {result['error']}")
        print("\nConsejos:")
        print("   - Asegúrate de tener suficiente feedback (mínimo 50 ejemplos)")
        print("   - Verifica que el archivo logs/user_feedback.jsonl existe")
        print("   - Aumenta --days para incluir más feedback")
        return

    print(f"\n✅ RE-ENTRENAMIENTO COMPLETADO")
    print(f"\n📊 RESULTADOS:")
    print(f"   Modelo: {result['model_name']}")
    print(f"   Ubicación: {result['model_path']}")
    print(f"   Train size: {result['train_size']}")
    print(f"   Val size: {result['val_size']}")
    print(f"   Test size: {result['test_size']}")

    if 'metrics' in result:
        metrics = result['metrics']
        print(f"\n📈 MÉTRICAS:")
        print(f"   Accuracy: {metrics.get('test_accuracy', 0):.2%}")
        print(f"   F1-Score: {metrics.get('test_f1', 0):.2%}")

    print(f"\n💡 PRÓXIMOS PASOS:")
    print(f"   1. Evalúa el nuevo modelo:")
    print(f"      python scripts/evaluate_model.py --model {result['model_name']}")
    print(f"\n   2. Si estás satisfecho, actualiza pipeline.py para usar el nuevo modelo:")
    print(f"      classifier_ml = MLDocumentClassifier(model_name='{result['model_name']}')")
    print(f"\n   3. Reinicia el servidor Flask para aplicar cambios")


if __name__ == "__main__":
    main()
