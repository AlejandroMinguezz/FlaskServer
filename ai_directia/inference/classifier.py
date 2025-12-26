"""
Document classification inference module
"""

import json
import joblib
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from ai_directia.extractors.unified_extractor import extract_text, extract_text_from_bytes
from ai_directia.preprocessing.text_cleaner import preprocess_text
from ai_directia.preprocessing.feature_extractor import load_vectorizer


class DocumentClassifier:
    """
    Document classifier for inference
    """

    def __init__(self, model_dir='ai/models/v1_tfidf_svm', config_path='ai/config/categories.json'):
        """
        Initialize classifier

        Args:
            model_dir: Directory containing trained model and vectorizer
            config_path: Path to categories configuration
        """
        self.model_dir = Path(model_dir)
        self.config_path = Path(config_path)

        self.model = None
        self.label_encoder = None
        self.vectorizer = None
        self.categories = None
        self.confidence_thresholds = None

        self._load_model()
        self._load_config()

    def _load_model(self):
        """Load trained model and vectorizer"""
        model_file = self.model_dir / 'model.pkl'
        vectorizer_file = self.model_dir / 'vectorizer.pkl'

        if not model_file.exists():
            raise FileNotFoundError(f"Model not found at {model_file}")

        if not vectorizer_file.exists():
            raise FileNotFoundError(f"Vectorizer not found at {vectorizer_file}")

        # Load model (with label encoder)
        model_data = joblib.load(model_file)

        if isinstance(model_data, dict):
            self.model = model_data['model']
            self.label_encoder = model_data.get('label_encoder')
        else:
            # Backward compatibility
            self.model = model_data
            self.label_encoder = None

        # Load vectorizer
        self.vectorizer = load_vectorizer(vectorizer_file)

        print(f"[OK] Model loaded from {model_file}")
        print(f"[OK] Vectorizer loaded from {vectorizer_file}")

    def _load_config(self):
        """Load categories configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found at {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        self.categories = {cat['id']: cat for cat in config['categories']}
        self.confidence_thresholds = config.get('confidence_thresholds', {
            'high': 0.80,
            'medium': 0.50,
            'low': 0.30,
        })

        print(f"[OK] Configuration loaded from {self.config_path}")
        print(f"  Categories: {len(self.categories)}")

    def _extract_text_from_file(self, file_path):
        """
        Extract text from file

        Args:
            file_path: Path to document

        Returns:
            Extracted text
        """
        result = extract_text(file_path)

        if not result['success']:
            raise ValueError(f"Text extraction failed: {result['error']}")

        return result['text']

    def _extract_text_from_bytes(self, file_bytes, file_extension):
        """
        Extract text from file bytes

        Args:
            file_bytes: File content as bytes
            file_extension: File extension (e.g., 'pdf', 'docx')

        Returns:
            Extracted text
        """
        result = extract_text_from_bytes(file_bytes, file_extension)

        if not result['success']:
            raise ValueError(f"Text extraction failed: {result['error']}")

        return result['text']

    def _preprocess_text(self, text):
        """
        Preprocess text for classification

        Args:
            text: Raw text

        Returns:
            Preprocessed text
        """
        return preprocess_text(text, remove_stop=True, language='spanish')

    def _get_category_info(self, category_id):
        """
        Get category information

        Args:
            category_id: Category ID

        Returns:
            dict with category info
        """
        if category_id not in self.categories:
            return {
                'id': category_id,
                'name': 'Desconocido',
                'folder_path': '/Documentos/Otros/',
            }

        cat = self.categories[category_id]
        return {
            'id': cat['id'],
            'name': cat['name'],
            'name_en': cat.get('name_en', cat['name']),
            'folder_path': cat['folder_path'],
            'description': cat.get('description', ''),
        }

    def _determine_confidence_level(self, confidence):
        """
        Determine confidence level based on thresholds

        Args:
            confidence: Confidence score (0-1)

        Returns:
            str: 'high', 'medium', or 'low'
        """
        if confidence >= self.confidence_thresholds['high']:
            return 'high'
        elif confidence >= self.confidence_thresholds['medium']:
            return 'medium'
        else:
            return 'low'

    def classify_text(self, text):
        """
        Classify preprocessed text

        Args:
            text: Raw text to classify

        Returns:
            dict with classification results
        """
        # Preprocess
        preprocessed = self._preprocess_text(text)

        # Extract features
        features = self.vectorizer.transform([preprocessed])

        # Predict
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]

        # Decode label
        if self.label_encoder:
            category_id = self.label_encoder.inverse_transform([prediction])[0]
        else:
            # Fallback: assume prediction is already category ID
            category_id = prediction

        # Get confidence (max probability)
        confidence = float(probabilities[prediction])

        # Get category info
        category_info = self._get_category_info(category_id)

        # Determine confidence level
        confidence_level = self._determine_confidence_level(confidence)

        # Get top 3 predictions
        top_3_indices = probabilities.argsort()[-3:][::-1]
        top_3_predictions = []

        for idx in top_3_indices:
            if self.label_encoder:
                cat_id = self.label_encoder.inverse_transform([idx])[0]
            else:
                cat_id = idx

            cat_info = self._get_category_info(cat_id)
            top_3_predictions.append({
                'category': cat_info['name'],
                'category_id': cat_id,
                'confidence': float(probabilities[idx])
            })

        return {
            'tipo_documento': category_info['name'],
            'tipo_documento_en': category_info['name_en'],
            'category_id': category_id,
            'confianza': confidence,
            'confidence_level': confidence_level,
            'carpeta_sugerida': category_info['folder_path'],
            'descripcion': category_info['description'],
            'top_predictions': top_3_predictions,
        }

    def classify_file(self, file_path):
        """
        Classify a document file

        Args:
            file_path: Path to document file

        Returns:
            dict with classification results
        """
        # Extract text
        text = self._extract_text_from_file(file_path)

        if not text or len(text.strip()) < 10:
            return {
                'tipo_documento': 'Desconocido',
                'confianza': 0.0,
                'confidence_level': 'low',
                'carpeta_sugerida': '/Documentos/Otros/',
                'error': 'No se pudo extraer texto suficiente del documento',
            }

        # Classify
        result = self.classify_text(text)

        # Add metadata
        result['metadata'] = {
            'file_name': Path(file_path).name,
            'text_length': len(text),
            'text_preview': text[:200] + '...' if len(text) > 200 else text,
        }

        return result

    def classify_file_bytes(self, file_bytes, file_extension, file_name=None):
        """
        Classify a document from bytes

        Args:
            file_bytes: File content as bytes
            file_extension: File extension (e.g., 'pdf', 'docx')
            file_name: Optional file name

        Returns:
            dict with classification results
        """
        # Extract text
        text = self._extract_text_from_bytes(file_bytes, file_extension)

        if not text or len(text.strip()) < 10:
            return {
                'tipo_documento': 'Desconocido',
                'confianza': 0.0,
                'confidence_level': 'low',
                'carpeta_sugerida': '/Documentos/Otros/',
                'error': 'No se pudo extraer texto suficiente del documento',
            }

        # Classify
        result = self.classify_text(text)

        # Add metadata
        result['metadata'] = {
            'file_name': file_name if file_name else f'document.{file_extension}',
            'file_extension': file_extension,
            'text_length': len(text),
            'text_preview': text[:200] + '...' if len(text) > 200 else text,
        }

        return result

    def get_categories(self):
        """
        Get all available categories

        Returns:
            list of category dicts
        """
        return [
            {
                'id': cat['id'],
                'name': cat['name'],
                'name_en': cat.get('name_en', cat['name']),
                'folder_path': cat['folder_path'],
                'description': cat.get('description', ''),
            }
            for cat in self.categories.values()
        ]

    def get_model_info(self):
        """
        Get information about the loaded model

        Returns:
            dict with model info
        """
        metadata_file = self.model_dir / 'metadata.json'

        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {}

        return {
            'model_type': metadata.get('model_type', 'Unknown'),
            'training_date': metadata.get('training_date', 'Unknown'),
            'vocabulary_size': metadata.get('vocabulary_size', 0),
            'metrics': metadata.get('metrics', {}),
            'num_categories': len(self.categories),
        }
