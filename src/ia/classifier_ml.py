"""
Clasificador de documentos usando modelo ML entrenado (TF-IDF + SVM).
Este clasificador reemplaza o complementa el basado en keywords.
"""

import os
import joblib
import json
from typing import Dict
from .utils import clean_text


class MLDocumentClassifier:
    """
    Clasificador de documentos usando modelo ML entrenado.
    """

    def __init__(self, model_name="tfidf_svm_v1"):
        """
        Args:
            model_name: Nombre del directorio del modelo a cargar
        """
        self.model_name = model_name
        self.model = None
        self.vectorizer = None
        self.metadata = None
        self.classes = []

        # Mapeo de categorías a carpetas
        self.folder_mapping = {
            "factura": "/Documentos/Facturas",
            "contrato": "/Documentos/Contratos",
            "nomina": "/Documentos/Nóminas",
            "presupuesto": "/Documentos/Presupuestos",
            "recibo": "/Documentos/Recibos",
            "certificado": "/Documentos/Certificados",
            "fiscal": "/Documentos/Fiscales",
            "notificacion": "/Documentos/Notificaciones",
            "otro": "/Documentos/Otros"
        }

        self.load_model()

    def load_model(self):
        """
        Carga el modelo, vectorizador y metadata desde disco.
        """
        model_dir = os.path.join(
            os.path.dirname(__file__),
            "models",
            self.model_name
        )

        model_file = os.path.join(model_dir, "model.pkl")
        vectorizer_file = os.path.join(model_dir, "vectorizer.pkl")
        metadata_file = os.path.join(model_dir, "metadata.json")

        # Verificar que los archivos existen
        if not os.path.exists(model_file):
            print(f"[WARNING] Modelo no encontrado en: {model_file}")
            print("[WARNING] Usando clasificación por keywords como fallback")
            return

        try:
            print(f"[INFO] Cargando modelo ML: {self.model_name}")

            # Cargar modelo
            self.model = joblib.load(model_file)
            print(f"[INFO] Modelo cargado: {type(self.model).__name__}")

            # Cargar vectorizador
            self.vectorizer = joblib.load(vectorizer_file)
            print(f"[INFO] Vectorizador cargado (vocab: {len(self.vectorizer.vocabulary_)} palabras)")

            # Cargar metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
                self.classes = self.metadata.get("classes", [])

            print(f"[INFO] Modelo ML cargado correctamente")
            print(f"[INFO] Clases: {self.classes}")
            print(f"[INFO] Accuracy en test: {self.metadata['metrics'].get('test_accuracy', 'N/A'):.4f}")

        except Exception as e:
            print(f"[ERROR] Error al cargar modelo: {e}")
            print("[WARNING] Usando clasificación por keywords como fallback")
            self.model = None
            self.vectorizer = None

    def classify_text(self, text: str, username: str = None) -> Dict:
        """
        Clasifica un texto usando el modelo ML.

        Args:
            text: Texto extraído del documento
            username: Nombre de usuario (opcional, para rutas personalizadas)

        Returns:
            Dict con 'tipo_documento', 'confianza' y 'carpeta_sugerida'
        """
        if not text or not text.strip():
            return {
                "tipo_documento": "desconocido",
                "confianza": 0.0,
                "carpeta_sugerida": "/Documentos/Otros"
            }

        # Si no hay modelo cargado, retornar error
        if not self.model or not self.vectorizer:
            return {
                "tipo_documento": "error",
                "confianza": 0.0,
                "carpeta_sugerida": "/Documentos/Otros",
                "error": "Modelo ML no disponible"
            }

        try:
            # Limpiar texto
            text_clean = clean_text(text)

            # Vectorizar
            text_tfidf = self.vectorizer.transform([text_clean])

            # Predecir
            prediction = self.model.predict(text_tfidf)[0]

            # Calcular confianza usando decision function
            if hasattr(self.model, 'decision_function'):
                # Para SVM, usar decision function como proxy de confianza
                decision_scores = self.model.decision_function(text_tfidf)[0]

                # Obtener el score de la clase predicha
                predicted_idx = list(self.classes).index(prediction)
                predicted_score = decision_scores[predicted_idx]

                # Calcular margin (distancia a segunda mejor clase)
                # Margin = diferencia entre mejor y segundo mejor score
                sorted_scores = sorted(decision_scores, reverse=True)
                margin = sorted_scores[0] - sorted_scores[1]

                # Normalizar margin a confianza [0.5, 0.98]
                # Margins típicos en nuestro modelo:
                # - Baja confianza: margin ~ 0.1-0.5 → confidence 0.5-0.65
                # - Media confianza: margin ~ 0.5-2.0 → confidence 0.65-0.85
                # - Alta confianza: margin > 2.0 → confidence 0.85-0.98
                if margin < 0.5:
                    # Baja confianza
                    confidence = 0.5 + (margin / 0.5) * 0.15
                elif margin < 2.0:
                    # Media confianza
                    confidence = 0.65 + ((margin - 0.5) / 1.5) * 0.20
                else:
                    # Alta confianza
                    confidence = 0.85 + min((margin - 2.0) / 3.0, 1.0) * 0.13

            else:
                # Fallback a confianza fija (para modelos sin decision_function)
                confidence = 0.85

            # Generar carpeta sugerida (sin prefijo de usuario/grupo)
            carpeta_sugerida = self.folder_mapping.get(prediction, "/Documentos/Otros")

            return {
                "tipo_documento": prediction,
                "confianza": float(confidence),
                "carpeta_sugerida": carpeta_sugerida
            }

        except Exception as e:
            print(f"[ERROR] Error en clasificación ML: {e}")
            return {
                "tipo_documento": "error",
                "confianza": 0.0,
                "carpeta_sugerida": "/Documentos/Otros",
                "error": str(e)
            }

    def get_model_info(self) -> Dict:
        """
        Retorna información sobre el modelo cargado.

        Returns:
            Dict con metadata del modelo
        """
        if not self.metadata:
            return {"error": "Modelo no cargado"}

        return {
            "model_name": self.model_name,
            "model_type": self.metadata.get("model_type"),
            "trained_at": self.metadata.get("trained_at"),
            "classes": self.classes,
            "metrics": self.metadata.get("metrics", {})
        }
