"""
Script para revisar estadísticas de feedback.

Uso:
    python scripts/check_feedback.py
    python scripts/check_feedback.py --days 30
"""

import sys
import os
import argparse
import json
from datetime import datetime, timedelta
from collections import Counter

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def main():
    parser = argparse.ArgumentParser(description="Revisar estadísticas de feedback")

    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Días a analizar (default: 7)"
    )

    args = parser.parse_args()

    feedback_file = "logs/user_feedback.jsonl"
    predictions_file = "logs/predictions.jsonl"

    print("\n" + "=" * 70)
    print("ESTADÍSTICAS DE FEEDBACK")
    print("=" * 70)

    # Análisis de feedback
    if os.path.exists(feedback_file):
        print(f"\n📊 Analizando feedback de últimos {args.days} días...")

        cutoff_date = datetime.now() - timedelta(days=args.days)

        feedback_stats = {
            "total": 0,
            "correct": 0,
            "incorrect": 0,
            "by_type": Counter(),
            "corrections": Counter()
        }

        with open(feedback_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    entry_date = datetime.fromisoformat(entry.get("timestamp", ""))

                    if entry_date < cutoff_date:
                        continue

                    feedback_stats["total"] += 1

                    if entry.get("was_correct"):
                        feedback_stats["correct"] += 1
                    else:
                        feedback_stats["incorrect"] += 1

                        pred = entry.get("predicted_type")
                        actual = entry.get("actual_type")
                        feedback_stats["corrections"][f"{pred} -> {actual}"] += 1

                    feedback_stats["by_type"][entry.get("actual_type")] += 1

                except Exception:
                    continue

        if feedback_stats["total"] > 0:
            accuracy = feedback_stats["correct"] / feedback_stats["total"]

            print(f"\n✅ RESUMEN:")
            print(f"   Total feedback: {feedback_stats['total']}")
            print(f"   Correctas: {feedback_stats['correct']} ({feedback_stats['correct']/feedback_stats['total']:.1%})")
            print(f"   Incorrectas: {feedback_stats['incorrect']} ({feedback_stats['incorrect']/feedback_stats['total']:.1%})")
            print(f"   Accuracy: {accuracy:.2%}")

            print(f"\n📂 Por tipo de documento:")
            for doc_type, count in feedback_stats["by_type"].most_common():
                print(f"   - {doc_type}: {count}")

            if feedback_stats["corrections"]:
                print(f"\n⚠️ Correcciones frecuentes:")
                for correction, count in feedback_stats["corrections"].most_common(5):
                    print(f"   - {correction}: {count} veces")

            # Recomendaciones
            print(f"\n💡 RECOMENDACIONES:")

            if feedback_stats["total"] < 50:
                print(f"   - Feedback insuficiente ({feedback_stats['total']}/50)")
                print(f"   - Continúa recopilando feedback antes de re-entrenar")

            elif accuracy < 0.85:
                print(f"   - Accuracy baja ({accuracy:.1%})")
                print(f"   - RE-ENTRENAMIENTO RECOMENDADO")
                print(f"   - Ejecuta: python scripts/retrain_model.py")

            else:
                print(f"   - Modelo funcionando bien ({accuracy:.1%})")
                print(f"   - Continúa monitoreando")

        else:
            print("\n⚠️ No hay feedback en el período especificado")

    else:
        print(f"\n⚠️ No existe archivo de feedback: {feedback_file}")

    # Análisis de predicciones
    if os.path.exists(predictions_file):
        print(f"\n📈 Analizando predicciones...")

        cutoff_date = datetime.now() - timedelta(days=args.days)

        pred_stats = {
            "total": 0,
            "by_type": Counter(),
            "by_confidence": {"low": 0, "medium": 0, "high": 0},
            "avg_confidence": []
        }

        with open(predictions_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)

                    if entry.get("type") == "error":
                        continue

                    entry_date = datetime.fromisoformat(entry.get("timestamp", ""))

                    if entry_date < cutoff_date:
                        continue

                    pred_stats["total"] += 1

                    pred_type = entry.get("predicted")
                    pred_stats["by_type"][pred_type] += 1

                    confidence = entry.get("confidence", 0)
                    pred_stats["avg_confidence"].append(confidence)

                    if confidence < 0.6:
                        pred_stats["by_confidence"]["low"] += 1
                    elif confidence < 0.8:
                        pred_stats["by_confidence"]["medium"] += 1
                    else:
                        pred_stats["by_confidence"]["high"] += 1

                except Exception:
                    continue

        if pred_stats["total"] > 0:
            avg_conf = sum(pred_stats["avg_confidence"]) / len(pred_stats["avg_confidence"])

            print(f"\n✅ PREDICCIONES:")
            print(f"   Total: {pred_stats['total']}")
            print(f"   Confianza promedio: {avg_conf:.2%}")

            print(f"\n🎯 Distribución de confianza:")
            total = pred_stats["total"]
            print(f"   - Baja (<0.6): {pred_stats['by_confidence']['low']} ({pred_stats['by_confidence']['low']/total:.1%})")
            print(f"   - Media (0.6-0.8): {pred_stats['by_confidence']['medium']} ({pred_stats['by_confidence']['medium']/total:.1%})")
            print(f"   - Alta (>0.8): {pred_stats['by_confidence']['high']} ({pred_stats['by_confidence']['high']/total:.1%})")

            print(f"\n📊 Predicciones por tipo:")
            for doc_type, count in pred_stats["by_type"].most_common():
                print(f"   - {doc_type}: {count} ({count/total:.1%})")

    else:
        print(f"\n⚠️ No existe archivo de predicciones: {predictions_file}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
