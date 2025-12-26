"""
Módulo de generación de datos sintéticos para entrenamiento del clasificador.
"""

from .base_generator import BaseDocumentGenerator
from .augmentation import augment_text

__all__ = ['BaseDocumentGenerator', 'augment_text']
