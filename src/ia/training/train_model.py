"""
Script de entrenamiento de modelos de clasificación de documentos.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score
)
from ..utils import clean_text


# Rutas
BASE_PATH = os.path.join(os.path.dirname(__file__), "..")
DATASET_PATH = os.path.join(BASE_PATH, "datasets", "processed")
MODELS_PATH = os.path.join(BASE_PATH, "models")

# Crear directorio de modelos si no existe
os.makedirs(MODELS_PATH, exist_ok=True)


def load_data(dataset_path=DATASET_PATH):
    """
    Carga los datasets de train, val y test.

    Returns:
        Tupla de DataFrames (train_df, val_df, test_df)
    """
    print("\n" + "=" * 70)
    print("CARGANDO DATASETS")
    print("=" * 70)

    train_df = pd.read_csv(os.path.join(dataset_path, "train.csv"))
    val_df = pd.read_csv(os.path.join(dataset_path, "val.csv"))
    test_df = pd.read_csv(os.path.join(dataset_path, "test.csv"))

    print(f"   - Train: {len(train_df)} ejemplos")
    print(f"   - Validation: {len(val_df)} ejemplos")
    print(f"   - Test: {len(test_df)} ejemplos")
    print(f"   - Total: {len(train_df) + len(val_df) + len(test_df)} ejemplos")

    return train_df, val_df, test_df


def preprocess_data(df):
    """
    Preprocesa los textos aplicando limpieza.

    Args:
        df: DataFrame con columnas 'text' y 'label'

    Returns:
        Tupla (X_clean, y) donde X_clean son textos limpios y y son labels
    """
    print("\n[*] Preprocesando textos...")

    X_clean = df['text'].apply(clean_text).values
    y = df['label'].values

    print(f"  [OK] {len(X_clean)} textos preprocesados")

    return X_clean, y


def train_tfidf_svm(train_df, val_df, max_features=5000, ngram_range=(1, 2), C=1.0):
    """
    Entrena un modelo SVM con vectorización TF-IDF.

    Args:
        train_df: DataFrame de entrenamiento
        val_df: DataFrame de validación
        max_features: Número máximo de features para TF-IDF
        ngram_range: Rango de n-gramas
        C: Parámetro de regularización del SVM

    Returns:
        Tupla (model, vectorizer, metadata)
    """
    print("\n" + "=" * 70)
    print("ENTRENANDO MODELO: TF-IDF + LinearSVC")
    print("=" * 70)
    print(f"Parametros:")
    print(f"   - max_features: {max_features}")
    print(f"   - ngram_range: {ngram_range}")
    print(f"   - C (regularization): {C}")
    print("=" * 70)

    # Preprocesar datos
    X_train, y_train = preprocess_data(train_df)
    X_val, y_val = preprocess_data(val_df)

    # Vectorización TF-IDF
    print("\n[*] Creando vectorizador TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=2,
        max_df=0.8,
        sublinear_tf=True
    )

    print("[*] Ajustando vectorizador en datos de train...")
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_val_tfidf = vectorizer.transform(X_val)

    print(f"  [OK] Matriz TF-IDF: {X_train_tfidf.shape}")
    print(f"  [OK] Vocabulario: {len(vectorizer.vocabulary_)} palabras")

    # Entrenar modelo SVM
    print("\n[*] Entrenando clasificador LinearSVC...")
    model = LinearSVC(C=C, max_iter=1000, class_weight='balanced', random_state=42)
    model.fit(X_train_tfidf, y_train)

    print("  [OK] Modelo entrenado")

    # Evaluar en train
    print("\n[*] Evaluando en conjunto de TRAIN...")
    y_train_pred = model.predict(X_train_tfidf)
    train_acc = accuracy_score(y_train, y_train_pred)
    train_f1 = f1_score(y_train, y_train_pred, average='weighted')

    print(f"  [TRAIN] Accuracy: {train_acc:.4f}")
    print(f"  [TRAIN] F1-Score: {train_f1:.4f}")

    # Evaluar en validación
    print("\n[*] Evaluando en conjunto de VALIDACION...")
    y_val_pred = model.predict(X_val_tfidf)
    val_acc = accuracy_score(y_val, y_val_pred)
    val_f1 = f1_score(y_val, y_val_pred, average='weighted')

    print(f"  [VAL] Accuracy: {val_acc:.4f}")
    print(f"  [VAL] F1-Score: {val_f1:.4f}")

    # Metadata
    metadata = {
        "model_type": "TF-IDF + LinearSVC",
        "trained_at": datetime.now().isoformat(),
        "train_size": len(train_df),
        "val_size": len(val_df),
        "classes": list(np.unique(y_train)),
        "n_classes": len(np.unique(y_train)),
        "vocab_size": len(vectorizer.vocabulary_),
        "hyperparameters": {
            "max_features": max_features,
            "ngram_range": ngram_range,
            "C": C
        },
        "metrics": {
            "train_accuracy": float(train_acc),
            "train_f1": float(train_f1),
            "val_accuracy": float(val_acc),
            "val_f1": float(val_f1)
        }
    }

    return model, vectorizer, metadata


def evaluate_model(model, vectorizer, test_df, output_dir=None):
    """
    Evalúa el modelo en el conjunto de test y genera reporte detallado.

    Args:
        model: Modelo entrenado
        vectorizer: Vectorizador TF-IDF
        test_df: DataFrame de test
        output_dir: Directorio donde guardar el reporte (opcional)

    Returns:
        Dict con métricas de evaluación
    """
    print("\n" + "=" * 70)
    print("EVALUACION EN CONJUNTO DE TEST")
    print("=" * 70)

    # Preprocesar
    X_test, y_test = preprocess_data(test_df)
    X_test_tfidf = vectorizer.transform(X_test)

    # Predicciones
    print("\n[*] Generando predicciones...")
    y_pred = model.predict(X_test_tfidf)

    # Métricas globales
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')

    print(f"\n  [TEST] Accuracy: {acc:.4f}")
    print(f"  [TEST] F1-Score (weighted): {f1:.4f}")

    # Reporte por clase
    print("\n" + "=" * 70)
    print("REPORTE POR CLASE")
    print("=" * 70)
    print(classification_report(y_test, y_pred, zero_division=0))

    # Matriz de confusión
    cm = confusion_matrix(y_test, y_pred)
    print("\n" + "=" * 70)
    print("MATRIZ DE CONFUSION")
    print("=" * 70)
    print(cm)

    # Guardar reporte si se especifica
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

        report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

        report_file = os.path.join(output_dir, "evaluation_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_accuracy": float(acc),
                "test_f1_weighted": float(f1),
                "classification_report": report_dict,
                "confusion_matrix": cm.tolist()
            }, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Reporte guardado en: {report_file}")

    return {
        "accuracy": acc,
        "f1_score": f1,
        "classification_report": classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    }


def save_model(model, vectorizer, metadata, model_name="tfidf_svm_v1", models_path=MODELS_PATH):
    """
    Guarda el modelo, vectorizador y metadata.

    Args:
        model: Modelo entrenado
        vectorizer: Vectorizador
        metadata: Diccionario con metadata
        model_name: Nombre del modelo
        models_path: Ruta donde guardar
    """
    model_dir = os.path.join(models_path, model_name)
    os.makedirs(model_dir, exist_ok=True)

    # Guardar modelo
    model_file = os.path.join(model_dir, "model.pkl")
    joblib.dump(model, model_file)

    # Guardar vectorizador
    vectorizer_file = os.path.join(model_dir, "vectorizer.pkl")
    joblib.dump(vectorizer, vectorizer_file)

    # Guardar metadata
    metadata_file = os.path.join(model_dir, "metadata.json")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("MODELO GUARDADO")
    print("=" * 70)
    print(f"   - Modelo: {model_file}")
    print(f"   - Vectorizador: {vectorizer_file}")
    print(f"   - Metadata: {metadata_file}")
    print("=" * 70)


def main():
    """
    Pipeline completo de entrenamiento.
    """
    print("\n" + "=" * 70)
    print("PIPELINE DE ENTRENAMIENTO DE MODELO")
    print("=" * 70)

    # 1. Cargar datos
    train_df, val_df, test_df = load_data()

    # 2. Entrenar modelo
    model, vectorizer, metadata = train_tfidf_svm(
        train_df,
        val_df,
        max_features=5000,
        ngram_range=(1, 2),
        C=1.0
    )

    # 3. Evaluar en test
    test_metrics = evaluate_model(model, vectorizer, test_df, output_dir=os.path.join(MODELS_PATH, "tfidf_svm_v1"))

    # Añadir métricas de test a metadata
    metadata["metrics"]["test_accuracy"] = float(test_metrics["accuracy"])
    metadata["metrics"]["test_f1"] = float(test_metrics["f1_score"])

    # 4. Guardar modelo
    save_model(model, vectorizer, metadata, model_name="tfidf_svm_v1")

    print("\n[OK] ENTRENAMIENTO COMPLETADO CON EXITO!\n")


if __name__ == "__main__":
    main()
