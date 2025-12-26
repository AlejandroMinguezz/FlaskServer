"""
Model training script for document classification
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import argparse
from datetime import datetime
import joblib

from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score
)

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from ai.preprocessing.text_cleaner import preprocess_text
from ai.preprocessing.feature_extractor import TfidfFeatureExtractor


def load_data(data_dir='ai/datasets/processed'):
    """
    Load train, validation, and test datasets

    Returns:
        train_df, val_df, test_df
    """
    data_path = Path(data_dir)

    train_df = pd.read_csv(data_path / 'train.csv')
    val_df = pd.read_csv(data_path / 'val.csv')
    test_df = pd.read_csv(data_path / 'test.csv')

    print(f"[OK] Data loaded:")
    print(f"  Train: {len(train_df)} documents")
    print(f"  Val:   {len(val_df)} documents")
    print(f"  Test:  {len(test_df)} documents")
    print(f"  Categories: {train_df['category'].nunique()}")

    return train_df, val_df, test_df


def preprocess_data(df, verbose=True):
    """
    Preprocess text data

    Args:
        df: DataFrame with 'text' column
        verbose: Print progress

    Returns:
        List of preprocessed texts
    """
    if verbose:
        print(f"Preprocessing {len(df)} documents...")

    from tqdm import tqdm
    processed_texts = []

    for text in tqdm(df['text'], desc="Preprocessing", disable=not verbose):
        processed = preprocess_text(text, remove_stop=True, language='spanish')
        processed_texts.append(processed)

    return processed_texts


def extract_features_from_data(train_texts, val_texts, test_texts, vectorizer_params=None):
    """
    Extract TF-IDF features from text data

    Args:
        train_texts: Training texts
        val_texts: Validation texts
        test_texts: Test texts
        vectorizer_params: Parameters for TfidfFeatureExtractor

    Returns:
        X_train, X_val, X_test, vectorizer
    """
    if vectorizer_params is None:
        vectorizer_params = {
            'max_features': 5000,
            'ngram_range': (1, 2),
            'min_df': 2,
            'max_df': 0.8,
        }

    print("Extracting TF-IDF features...")
    vectorizer = TfidfFeatureExtractor(**vectorizer_params)

    X_train = vectorizer.fit_transform(train_texts)
    X_val = vectorizer.transform(val_texts)
    X_test = vectorizer.transform(test_texts)

    print(f"[OK] Feature extraction complete:")
    print(f"  Vocabulary size: {vectorizer.get_vocabulary_size()}")
    print(f"  Feature shape: {X_train.shape}")

    return X_train, X_val, X_test, vectorizer


def train_svm_model(X_train, y_train, kernel='linear', C=1.0):
    """
    Train SVM classifier

    Args:
        X_train: Training features
        y_train: Training labels
        kernel: SVM kernel type
        C: Regularization parameter

    Returns:
        Trained model
    """
    print(f"\nTraining SVM (kernel={kernel}, C={C})...")

    model = SVC(
        kernel=kernel,
        C=C,
        class_weight='balanced',
        probability=True,
        random_state=42
    )

    model.fit(X_train, y_train)
    print("[OK] SVM training complete")

    return model


def train_naive_bayes_model(X_train, y_train, alpha=1.0):
    """
    Train Naive Bayes classifier

    Args:
        X_train: Training features
        y_train: Training labels
        alpha: Smoothing parameter

    Returns:
        Trained model
    """
    print(f"\nTraining Naive Bayes (alpha={alpha})...")

    model = MultinomialNB(alpha=alpha)
    model.fit(X_train, y_train)

    print("[OK] Naive Bayes training complete")

    return model


def train_random_forest_model(X_train, y_train, n_estimators=100):
    """
    Train Random Forest classifier

    Args:
        X_train: Training features
        y_train: Training labels
        n_estimators: Number of trees

    Returns:
        Trained model
    """
    print(f"\nTraining Random Forest (n_estimators={n_estimators})...")

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    print("[OK] Random Forest training complete")

    return model


def evaluate_model(model, X, y, class_labels, dataset_name='Test'):
    """
    Evaluate model performance

    Args:
        model: Trained model
        X: Features
        y: True labels
        class_labels: List of class names
        dataset_name: Name of dataset for display

    Returns:
        dict with metrics
    """
    print(f"\n{'='*70}")
    print(f"Evaluating on {dataset_name} set...")
    print(f"{'='*70}")

    # Predictions
    y_pred = model.predict(X)
    y_pred_proba = model.predict_proba(X) if hasattr(model, 'predict_proba') else None

    # Metrics
    accuracy = accuracy_score(y, y_pred)
    f1_macro = f1_score(y, y_pred, average='macro')
    f1_weighted = f1_score(y, y_pred, average='weighted')

    print(f"\nOverall Metrics:")
    print(f"  Accuracy:     {accuracy:.4f}")
    print(f"  F1 (macro):   {f1_macro:.4f}")
    print(f"  F1 (weighted): {f1_weighted:.4f}")

    # Classification report
    print(f"\nClassification Report:")
    print(classification_report(y, y_pred, target_names=class_labels))

    # Confusion matrix
    cm = confusion_matrix(y, y_pred)
    print(f"\nConfusion Matrix:")
    print(cm)

    metrics = {
        'accuracy': float(accuracy),
        'f1_macro': float(f1_macro),
        'f1_weighted': float(f1_weighted),
        'classification_report': classification_report(y, y_pred, target_names=class_labels, output_dict=True),
        'confusion_matrix': cm.tolist(),
    }

    return metrics


def save_model(model, vectorizer, metrics, model_dir='ai/models/v1_tfidf_svm'):
    """
    Save trained model and vectorizer

    Args:
        model: Trained model
        vectorizer: Fitted vectorizer
        metrics: Evaluation metrics
        model_dir: Directory to save model
    """
    model_path = Path(model_dir)
    model_path.mkdir(parents=True, exist_ok=True)

    # Save model
    model_file = model_path / 'model.pkl'
    joblib.dump(model, model_file)
    print(f"\n[OK] Model saved to {model_file}")

    # Save vectorizer
    vectorizer_file = model_path / 'vectorizer.pkl'
    vectorizer.save(vectorizer_file)

    # Save metadata
    metadata = {
        'model_type': type(model).__name__,
        'training_date': datetime.now().isoformat(),
        'vocabulary_size': vectorizer.get_vocabulary_size(),
        'metrics': metrics,
    }

    metadata_file = model_path / 'metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"[OK] Metadata saved to {metadata_file}")
    print(f"\n{'='*70}")
    print(f"Model training complete! Model saved to: {model_path}")
    print(f"{'='*70}")


def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description='Train document classification model')
    parser.add_argument('--model-type', type=str, default='svm',
                       choices=['svm', 'naive_bayes', 'random_forest'],
                       help='Type of model to train')
    parser.add_argument('--data-dir', type=str, default='ai/datasets/processed',
                       help='Directory with processed datasets')
    parser.add_argument('--output-dir', type=str, default='ai/models/v1_tfidf_svm',
                       help='Directory to save trained model')
    parser.add_argument('--max-features', type=int, default=5000,
                       help='Maximum number of TF-IDF features')
    parser.add_argument('--svm-kernel', type=str, default='linear',
                       help='SVM kernel type')
    parser.add_argument('--svm-c', type=float, default=1.0,
                       help='SVM regularization parameter')

    args = parser.parse_args()

    print("=" * 70)
    print("DOCUMENT CLASSIFICATION MODEL TRAINING")
    print("=" * 70)

    # Load data
    train_df, val_df, test_df = load_data(args.data_dir)

    # Preprocess text
    train_texts = preprocess_data(train_df)
    val_texts = preprocess_data(val_df)
    test_texts = preprocess_data(test_df)

    # Extract features
    X_train, X_val, X_test, vectorizer = extract_features_from_data(
        train_texts, val_texts, test_texts,
        vectorizer_params={'max_features': args.max_features}
    )

    # Prepare labels
    y_train = train_df['category'].values
    y_val = val_df['category'].values
    y_test = test_df['category'].values

    # Get class labels
    class_labels = sorted(train_df['category'].unique())

    # Encode labels to integers
    from sklearn.preprocessing import LabelEncoder
    label_encoder = LabelEncoder()
    label_encoder.fit(class_labels)

    y_train_encoded = label_encoder.transform(y_train)
    y_val_encoded = label_encoder.transform(y_val)
    y_test_encoded = label_encoder.transform(y_test)

    # Train model
    if args.model_type == 'svm':
        model = train_svm_model(X_train, y_train_encoded, kernel=args.svm_kernel, C=args.svm_c)
    elif args.model_type == 'naive_bayes':
        model = train_naive_bayes_model(X_train, y_train_encoded)
    elif args.model_type == 'random_forest':
        model = train_random_forest_model(X_train, y_train_encoded)

    # Evaluate on validation set
    val_metrics = evaluate_model(model, X_val, y_val_encoded, class_labels, dataset_name='Validation')

    # Evaluate on test set
    test_metrics = evaluate_model(model, X_test, y_test_encoded, class_labels, dataset_name='Test')

    # Combine metrics
    all_metrics = {
        'validation': val_metrics,
        'test': test_metrics,
    }

    # Save model with label encoder
    model_with_encoder = {
        'model': model,
        'label_encoder': label_encoder,
    }

    save_model(model_with_encoder, vectorizer, all_metrics, model_dir=args.output_dir)


if __name__ == '__main__':
    main()
