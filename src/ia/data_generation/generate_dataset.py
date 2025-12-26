"""
Script maestro para generar datasets sintéticos completos.
"""

import os
import pandas as pd
import random
from tqdm import tqdm

from .generators.factura_generator import FacturaGenerator
from .generators.nomina_generator import NominaGenerator
from .generators.contrato_generator import ContratoGenerator
from .generators.presupuesto_generator import PresupuestoGenerator
from .generators.recibo_generator import ReciboGenerator
from .generators.certificado_generator import CertificadoGenerator
from .generators.fiscal_generator import FiscalGenerator
from .generators.notificacion_generator import NotificacionGenerator
from .augmentation import generate_variants


# Configuración
DATASET_BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "datasets")
SYNTHETIC_PATH = os.path.join(DATASET_BASE_PATH, "synthetic")
PROCESSED_PATH = os.path.join(DATASET_BASE_PATH, "processed")

# Crear directorios si no existen
os.makedirs(SYNTHETIC_PATH, exist_ok=True)
os.makedirs(PROCESSED_PATH, exist_ok=True)


# Generadores por categoría
GENERATORS = {
    "factura": FacturaGenerator,
    "nomina": NominaGenerator,
    "contrato": ContratoGenerator,
    "presupuesto": PresupuestoGenerator,
    "recibo": ReciboGenerator,
    "certificado": CertificadoGenerator,
    "fiscal": FiscalGenerator,
    "notificacion": NotificacionGenerator
}


def generate_category_data(category: str, generator_class, num_docs: int, variants_per_doc: int = 2, seed: int = 42):
    """
    Genera documentos para una categoría específica.

    Args:
        category: Nombre de la categoría
        generator_class: Clase generadora
        num_docs: Número de documentos base a generar
        variants_per_doc: Número de variantes por documento (con augmentation)
        seed: Semilla para reproducibilidad

    Returns:
        Lista de tuplas (texto, label)
    """

    print(f"\n[*] Generando {num_docs} documentos de tipo '{category}'...")

    generator = generator_class(seed=seed)
    data = []

    for i in tqdm(range(num_docs), desc=f"  {category}"):
        # Generar documento base
        doc = generator.generate_document()

        # Generar variantes con augmentation
        variants = generate_variants(doc, num_variants=variants_per_doc)

        for variant in variants:
            data.append((variant, category))

    print(f"  [OK] Generados {len(data)} ejemplos para '{category}' ({num_docs} docs + {variants_per_doc} variantes c/u)")

    return data


def generate_full_dataset(docs_per_category: int = 200, variants_per_doc: int = 2, seed: int = 42):
    """
    Genera el dataset completo para todas las categorías.

    Args:
        docs_per_category: Número de documentos base por categoría
        variants_per_doc: Número de variantes por documento
        seed: Semilla para reproducibilidad

    Returns:
        DataFrame con columnas 'text' y 'label'
    """

    print("=" * 70)
    print("GENERACION DE DATASET SINTETICO")
    print("=" * 70)
    print(f"Configuracion:")
    print(f"   - Documentos base por categoria: {docs_per_category}")
    print(f"   - Variantes por documento: {variants_per_doc}")
    print(f"   - Total ejemplos por categoria: {docs_per_category * (variants_per_doc + 1)}")
    print(f"   - Categorias: {len(GENERATORS)}")
    print(f"   - Total ejemplos dataset: {docs_per_category * (variants_per_doc + 1) * len(GENERATORS)}")
    print("=" * 70)

    all_data = []

    for category, generator_class in GENERATORS.items():
        category_data = generate_category_data(
            category,
            generator_class,
            docs_per_category,
            variants_per_doc,
            seed
        )
        all_data.extend(category_data)

    # Crear DataFrame
    df = pd.DataFrame(all_data, columns=['text', 'label'])

    # Mezclar datos
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    print("\n" + "=" * 70)
    print("[OK] DATASET GENERADO CORRECTAMENTE")
    print("=" * 70)
    print(f"Resumen:")
    print(f"   - Total ejemplos: {len(df)}")
    print(f"   - Distribucion por categoria:")
    for label in df['label'].unique():
        count = len(df[df['label'] == label])
        percentage = (count / len(df)) * 100
        print(f"     - {label}: {count} ({percentage:.1f}%)")

    return df


def split_dataset(df: pd.DataFrame, train_ratio: float = 0.7, val_ratio: float = 0.15, test_ratio: float = 0.15, seed: int = 42):
    """
    Divide el dataset en train, validation y test.

    Args:
        df: DataFrame completo
        train_ratio: Proporción de datos para entrenamiento
        val_ratio: Proporción de datos para validación
        test_ratio: Proporción de datos para test
        seed: Semilla para reproducibilidad

    Returns:
        Tupla (train_df, val_df, test_df)
    """

    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.01, "Las proporciones deben sumar 1.0"

    # Mezclar
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    # Calcular puntos de corte
    n = len(df)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)

    # Dividir
    train_df = df[:train_end]
    val_df = df[train_end:val_end]
    test_df = df[val_end:]

    print("\n" + "=" * 70)
    print("DIVISION DEL DATASET")
    print("=" * 70)
    print(f"   - Train: {len(train_df)} ejemplos ({len(train_df)/n*100:.1f}%)")
    print(f"   - Validation: {len(val_df)} ejemplos ({len(val_df)/n*100:.1f}%)")
    print(f"   - Test: {len(test_df)} ejemplos ({len(test_df)/n*100:.1f}%)")

    return train_df, val_df, test_df


def save_dataset(train_df, val_df, test_df, output_path: str = PROCESSED_PATH):
    """
    Guarda los datasets en archivos CSV.

    Args:
        train_df: DataFrame de entrenamiento
        val_df: DataFrame de validación
        test_df: DataFrame de test
        output_path: Ruta donde guardar los archivos
    """

    os.makedirs(output_path, exist_ok=True)

    train_file = os.path.join(output_path, "train.csv")
    val_file = os.path.join(output_path, "val.csv")
    test_file = os.path.join(output_path, "test.csv")

    train_df.to_csv(train_file, index=False, encoding='utf-8')
    val_df.to_csv(val_file, index=False, encoding='utf-8')
    test_df.to_csv(test_file, index=False, encoding='utf-8')

    print("\n" + "=" * 70)
    print("DATASETS GUARDADOS")
    print("=" * 70)
    print(f"   - Train: {train_file}")
    print(f"   - Validation: {val_file}")
    print(f"   - Test: {test_file}")
    print("=" * 70)


def main():
    """
    Función principal: genera y guarda el dataset completo.
    """

    # Configuración
    DOCS_PER_CATEGORY = 200  # Documentos base por categoría
    VARIANTS_PER_DOC = 2     # Variantes con augmentation
    SEED = 42

    # Generar dataset completo
    df = generate_full_dataset(
        docs_per_category=DOCS_PER_CATEGORY,
        variants_per_doc=VARIANTS_PER_DOC,
        seed=SEED
    )

    # Dividir en train/val/test
    train_df, val_df, test_df = split_dataset(df, seed=SEED)

    # Guardar
    save_dataset(train_df, val_df, test_df)

    print("\n[OK] PROCESO COMPLETADO CON EXITO!\n")


if __name__ == "__main__":
    main()
