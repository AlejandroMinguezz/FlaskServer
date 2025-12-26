"""
Feature extraction module for text classification
"""

from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from pathlib import Path


class TfidfFeatureExtractor:
    """
    TF-IDF based feature extractor for document classification
    """

    def __init__(
        self,
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.8,
        use_idf=True,
        sublinear_tf=True
    ):
        """
        Initialize TF-IDF vectorizer

        Args:
            max_features: Maximum number of features to extract
            ngram_range: Range of n-grams (default: unigrams and bigrams)
            min_df: Minimum document frequency
            max_df: Maximum document frequency
            use_idf: Enable inverse-document-frequency reweighting
            sublinear_tf: Apply sublinear tf scaling (replace tf with 1 + log(tf))
        """
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            min_df=min_df,
            max_df=max_df,
            use_idf=use_idf,
            sublinear_tf=sublinear_tf,
            lowercase=True,
            strip_accents='unicode',
            token_pattern=r'\b\w+\b'
        )

        self.is_fitted = False

    def fit(self, texts):
        """
        Fit the vectorizer on training texts

        Args:
            texts: List of text documents

        Returns:
            self
        """
        self.vectorizer.fit(texts)
        self.is_fitted = True
        return self

    def transform(self, texts):
        """
        Transform texts to TF-IDF features

        Args:
            texts: List of text documents

        Returns:
            Sparse matrix of TF-IDF features
        """
        if not self.is_fitted:
            raise ValueError("Vectorizer must be fitted before transform")

        return self.vectorizer.transform(texts)

    def fit_transform(self, texts):
        """
        Fit vectorizer and transform texts in one step

        Args:
            texts: List of text documents

        Returns:
            Sparse matrix of TF-IDF features
        """
        self.is_fitted = True
        return self.vectorizer.fit_transform(texts)

    def get_feature_names(self):
        """
        Get feature names (vocabulary)

        Returns:
            List of feature names
        """
        if not self.is_fitted:
            raise ValueError("Vectorizer must be fitted first")

        return self.vectorizer.get_feature_names_out()

    def get_vocabulary_size(self):
        """
        Get size of vocabulary

        Returns:
            int: Number of features
        """
        if not self.is_fitted:
            return 0

        return len(self.vectorizer.vocabulary_)

    def save(self, path):
        """
        Save vectorizer to disk

        Args:
            path: Path to save file
        """
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted vectorizer")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.vectorizer, path)
        print(f"Vectorizer saved to {path}")

    def load(self, path):
        """
        Load vectorizer from disk

        Args:
            path: Path to saved vectorizer

        Returns:
            self
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Vectorizer not found at {path}")

        self.vectorizer = joblib.load(path)
        self.is_fitted = True
        print(f"Vectorizer loaded from {path}")

        return self

    def get_top_features_per_class(self, X, y, class_labels, top_n=10):
        """
        Get top N features (words) for each class

        Args:
            X: Feature matrix
            y: Labels
            class_labels: List of class names
            top_n: Number of top features to return

        Returns:
            dict: {class_name: [(feature, score), ...]}
        """
        import numpy as np

        feature_names = self.get_feature_names()
        top_features = {}

        for class_idx, class_name in enumerate(class_labels):
            # Get indices for this class
            class_mask = (y == class_idx)

            if class_mask.sum() == 0:
                continue

            # Average TF-IDF scores for this class
            avg_tfidf = X[class_mask].mean(axis=0).A1

            # Get top N indices
            top_indices = avg_tfidf.argsort()[-top_n:][::-1]

            # Get feature names and scores
            top_features[class_name] = [
                (feature_names[idx], avg_tfidf[idx])
                for idx in top_indices
            ]

        return top_features


def extract_features(texts, vectorizer=None, fit=False):
    """
    Extract TF-IDF features from texts

    Args:
        texts: List of text documents
        vectorizer: Pre-fitted vectorizer (optional)
        fit: If True, fit a new vectorizer on the texts

    Returns:
        features, vectorizer
    """
    if vectorizer is None:
        vectorizer = TfidfFeatureExtractor()

    if fit:
        features = vectorizer.fit_transform(texts)
    else:
        features = vectorizer.transform(texts)

    return features, vectorizer


def load_vectorizer(path):
    """
    Load a saved vectorizer

    Args:
        path: Path to saved vectorizer

    Returns:
        TfidfFeatureExtractor instance
    """
    extractor = TfidfFeatureExtractor()
    extractor.load(path)
    return extractor
