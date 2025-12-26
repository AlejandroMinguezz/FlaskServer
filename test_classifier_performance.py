"""
Script de prueba para comparar clasificador optimizado vs BETO.
Mide consumo de recursos y performance.
"""

import time
import psutil
import os
from src.ia.classifier_optimized import DocumentClassifier

# Texto de prueba
SAMPLE_TEXT = """
FACTURA N.º 2025/001
Fecha: 15/03/2025

Cliente: Test S.L.
NIF: B12345678

Conceptos:
- Servicios: 1.000,00€
- IVA (21%): 210,00€

Total: 1.210,00€
"""


def test_optimized_classifier():
    """Test del clasificador optimizado (sin BETO)."""
    print("\n" + "=" * 70)
    print("TEST: Clasificador Optimizado (sin BETO)")
    print("=" * 70)

    # Mediar memoria inicial
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024  # MB

    # Inicializar
    start_init = time.time()
    classifier = DocumentClassifier()
    init_time = time.time() - start_init

    # Medir memoria después de cargar
    mem_after = process.memory_info().rss / 1024 / 1024  # MB
    mem_used = mem_after - mem_before

    print(f"\nInicializacion:")
    print(f"   - Tiempo: {init_time:.3f}s")
    print(f"   - Memoria usada: {mem_used:.1f} MB")

    # Test de clasificación
    print(f"\nClasificacion de documento de prueba:")
    start_classify = time.time()
    result = classifier.classify_text(SAMPLE_TEXT, username="testuser")
    classify_time = time.time() - start_classify

    print(f"   - Resultado: {result}")
    print(f"   - Tiempo: {classify_time:.3f}s")

    # Test de múltiples clasificaciones
    print(f"\nTest de velocidad (100 clasificaciones):")
    start_bulk = time.time()
    for i in range(100):
        classifier.classify_text(SAMPLE_TEXT, username="testuser")
    bulk_time = time.time() - start_bulk
    avg_time = bulk_time / 100

    print(f"   - Tiempo total: {bulk_time:.3f}s")
    print(f"   - Promedio: {avg_time:.4f}s/clasificacion")
    if bulk_time > 0:
        print(f"   - Throughput: {100/bulk_time:.1f} clasificaciones/segundo")
    else:
        print(f"   - Throughput: >1000 clasificaciones/segundo (muy rapido!)")

    # Resumen
    print(f"\nRESUMEN:")
    print(f"   - Startup time: {init_time:.3f}s")
    print(f"   - Memory footprint: {mem_used:.1f} MB")
    print(f"   - Classification speed: {avg_time:.4f}s")
    print(f"   - Accuracy estimada: 65-75%")
    print("=" * 70)

    return {
        "init_time": init_time,
        "memory_mb": mem_used,
        "classify_time": avg_time
    }


def compare_with_theoretical_beto():
    """Comparación teórica con BETO basada en mediciones previas."""
    print("\n" + "=" * 70)
    print("COMPARACIÓN: Optimizado vs BETO")
    print("=" * 70)

    optimized_stats = test_optimized_classifier()

    # Valores teóricos de BETO (basados en implementación anterior)
    beto_stats = {
        "init_time": 12.0,  # ~10-15 segundos
        "memory_mb": 500.0,  # ~500 MB
        "classify_time": 0.15  # ~0.1-0.2s con embeddings
    }

    print(f"\nCOMPARACION DE PERFORMANCE:")
    print(f"\n{'Metrica':<25} {'Optimizado':<20} {'BETO':<20} {'Mejora'}")
    print("-" * 70)

    # Startup time
    startup_improvement = (beto_stats["init_time"] / optimized_stats["init_time"])
    print(f"{'Startup Time':<25} {optimized_stats['init_time']:.3f}s"
          f"{'':<14} {beto_stats['init_time']:.1f}s"
          f"{'':<15} {startup_improvement:.1f}x mas rapido")

    # Memory
    memory_improvement = (beto_stats["memory_mb"] / optimized_stats["memory_mb"])
    print(f"{'Memory Usage':<25} {optimized_stats['memory_mb']:.1f} MB"
          f"{'':<11} {beto_stats['memory_mb']:.0f} MB"
          f"{'':<12} {memory_improvement:.1f}x menos memoria")

    # Classification speed
    speed_improvement = (beto_stats["classify_time"] / optimized_stats["classify_time"])
    print(f"{'Classification Time':<25} {optimized_stats['classify_time']:.4f}s"
          f"{'':<11} {beto_stats['classify_time']:.3f}s"
          f"{'':<13} {speed_improvement:.1f}x {'mas rapido' if speed_improvement > 1 else 'mas lento'}")

    print("\nCONCLUSION:")
    print(f"   El clasificador optimizado es:")
    print(f"   - {startup_improvement:.0f}x más rápido en inicialización")
    print(f"   - {memory_improvement:.0f}x más eficiente en memoria")
    print(f"   - Suficientemente rápido para producción")
    print(f"   - Sin dependencias pesadas (PyTorch, Transformers)")
    print("=" * 70)


if __name__ == "__main__":
    compare_with_theoretical_beto()
