"""
Script para probar el clasificador de documentos
"""

import argparse
from pathlib import Path
from inference.classifier import DocumentClassifier


def print_result(result):
    """Print classification result in a nice format"""
    print("\n" + "=" * 70)
    print("RESULTADO DE LA CLASIFICACIÓN")
    print("=" * 70)

    if 'error' in result:
        print(f"\n[\!] Error: {result['error']}")
        return

    print(f"\n[OK] Tipo de documento: {result['tipo_documento']}")
    print(f"  Confianza: {result['confianza']:.2%}")
    print(f"  Nivel de confianza: {result['confidence_level'].upper()}")
    print(f"  Carpeta sugerida: {result['carpeta_sugerida']}")

    if 'descripcion' in result:
        print(f"\n  Descripción: {result['descripcion']}")

    if 'top_predictions' in result:
        print(f"\n  Top 3 predicciones:")
        for i, pred in enumerate(result['top_predictions'], 1):
            print(f"    {i}. {pred['category']}: {pred['confidence']:.2%}")

    if 'metadata' in result:
        meta = result['metadata']
        print(f"\n  Metadata:")
        if 'file_name' in meta:
            print(f"    Archivo: {meta['file_name']}")
        if 'text_length' in meta:
            print(f"    Longitud del texto: {meta['text_length']} caracteres")
        if 'text_preview' in meta:
            print(f"\n  Vista previa del texto:")
            print(f"    {meta['text_preview'][:150]}...")

    print("\n" + "=" * 70)


def test_text_classification(classifier, text):
    """Test classification with raw text"""
    print(f"\nClasificando texto...")
    result = classifier.classify_text(text)
    print_result(result)


def test_file_classification(classifier, file_path):
    """Test classification with a file"""
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"[ERROR] Error: Archivo no encontrado: {file_path}")
        return

    print(f"\nClasificando archivo: {file_path.name}")
    result = classifier.classify_file(file_path)
    print_result(result)


def test_synthetic_documents(classifier):
    """Test with synthetic documents"""
    from data_generation.template_generator import GENERATORS

    print("\n" + "=" * 70)
    print("PROBANDO CON DOCUMENTOS SINTÉTICOS")
    print("=" * 70)

    for category_id, generator in GENERATORS.items():
        print(f"\n\n{'-' * 70}")
        print(f"Categoría: {category_id.upper()}")
        print(f"{'-' * 70}")

        # Generate synthetic document
        text = generator()

        # Classify
        result = classifier.classify_text(text)

        # Check if prediction matches expected category
        correct = result['category_id'] == category_id
        status = "[OK]" if correct else "[X]"

        print(f"\n{status} Predicción: {result['tipo_documento']}")
        print(f"  Esperado: {category_id}")
        print(f"  Confianza: {result['confianza']:.2%}")

        if not correct:
            print(f"  [\!] PREDICCIÓN INCORRECTA")


def show_categories(classifier):
    """Show all available categories"""
    print("\n" + "=" * 70)
    print("CATEGORÍAS DISPONIBLES")
    print("=" * 70)

    categories = classifier.get_categories()

    for i, cat in enumerate(categories, 1):
        print(f"\n{i}. {cat['name']} ({cat['id']})")
        print(f"   Carpeta: {cat['folder_path']}")
        if cat.get('description'):
            print(f"   Descripción: {cat['description']}")


def show_model_info(classifier):
    """Show model information"""
    print("\n" + "=" * 70)
    print("INFORMACIÓN DEL MODELO")
    print("=" * 70)

    info = classifier.get_model_info()

    print(f"\n  Tipo de modelo: {info['model_type']}")
    print(f"  Fecha de entrenamiento: {info['training_date']}")
    print(f"  Tamaño del vocabulario: {info['vocabulary_size']}")
    print(f"  Número de categorías: {info['num_categories']}")

    if 'metrics' in info and info['metrics']:
        print(f"\n  Métricas del modelo:")

        if 'test' in info['metrics']:
            test_metrics = info['metrics']['test']
            print(f"    Accuracy (test): {test_metrics.get('accuracy', 0):.4f}")
            print(f"    F1-score macro (test): {test_metrics.get('f1_macro', 0):.4f}")
            print(f"    F1-score weighted (test): {test_metrics.get('f1_weighted', 0):.4f}")


def main():
    parser = argparse.ArgumentParser(description='Probar clasificador de documentos')
    parser.add_argument('--file', type=str, help='Archivo a clasificar')
    parser.add_argument('--text', type=str, help='Texto a clasificar')
    parser.add_argument('--test-synthetic', action='store_true',
                       help='Probar con documentos sintéticos')
    parser.add_argument('--show-categories', action='store_true',
                       help='Mostrar categorías disponibles')
    parser.add_argument('--show-info', action='store_true',
                       help='Mostrar información del modelo')
    parser.add_argument('--model-dir', type=str, default='ai/models/v1_tfidf_svm',
                       help='Directorio del modelo')
    parser.add_argument('--config', type=str, default='ai/config/categories.json',
                       help='Archivo de configuración de categorías')

    args = parser.parse_args()

    # Initialize classifier
    print("Inicializando clasificador...")
    try:
        classifier = DocumentClassifier(
            model_dir=args.model_dir,
            config_path=args.config
        )
    except FileNotFoundError as e:
        print(f"\n[ERROR] Error: {e}")
        print("\n[TIP] Tip: Primero debes generar datos y entrenar el modelo:")
        print("   1. python -m ai.data_generation.generate_dataset")
        print("   2. python -m ai.training.train_model")
        return
    except Exception as e:
        print(f"\n[ERROR] Error al inicializar el clasificador: {e}")
        return

    print("[OK] Clasificador inicializado correctamente\n")

    # Execute requested action
    if args.show_categories:
        show_categories(classifier)
    elif args.show_info:
        show_model_info(classifier)
    elif args.test_synthetic:
        test_synthetic_documents(classifier)
    elif args.file:
        test_file_classification(classifier, args.file)
    elif args.text:
        test_text_classification(classifier, args.text)
    else:
        # Default: show help and info
        print("No se especificó ninguna acción.\n")
        parser.print_help()
        print("\n")
        show_model_info(classifier)
        show_categories(classifier)


if __name__ == '__main__':
    main()
