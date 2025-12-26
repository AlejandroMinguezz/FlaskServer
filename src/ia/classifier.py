import os
import re
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from typing import Dict, List, Tuple


MODEL_NAME = "dccuchile/bert-base-spanish-wwm-cased"


class DocumentClassifier:
    def __init__(self):
        # Clases de documentos soportadas (documentos administrativos)
        self.classes = [
            "factura", "contrato", "nomina", "presupuesto", "recibo",
            "certificado", "fiscal", "notificacion", "otro"
        ]

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

        # Palabras clave para cada tipo de documento
        self.keywords = {
            "factura": [
                "factura", "invoice", "importe", "iva", "base imponible",
                "total a pagar", "número de factura", "nº factura", "cif", "nif",
                "proveedor", "cliente", "precio unitario", "cantidad", "subtotal",
                "descripción", "concepto", "fecha de emisión", "forma de pago"
            ],
            "contrato": [
                "contrato", "acuerdo", "partes contratantes", "cláusula",
                "estipula", "compromiso", "obligaciones", "derechos", "parte contratante",
                "firma", "otorga", "condiciones", "resolución", "rescisión",
                "arrendamiento", "servicios", "laboral", "vigencia", "prorroga"
            ],
            "nomina": [
                "nómina", "nomina", "salario", "irpf", "seguridad social",
                "cotización", "líquido a percibir", "devengos", "deducciones",
                "salario base", "complementos", "pagas extras", "trabajador",
                "categoría profesional", "grupo de cotización", "antigüedad"
            ],
            "presupuesto": [
                "presupuesto", "cotización", "quote", "validez", "oferta",
                "propuesta económica", "estimación", "coste", "precio orientativo",
                "válido hasta", "aceptación", "propuesta", "valoración"
            ],
            "recibo": [
                "recibo", "receipt", "pago", "recibí", "abono", "cobro",
                "cuota", "mensualidad", "domiciliación", "cargo", "titular",
                "consumo", "periodo de facturación", "luz", "agua", "gas",
                "alquiler", "arrendamiento", "renta"
            ],
            "certificado": [
                "certificado", "certifica", "acredita", "expedido por",
                "se expide", "hace constar", "certificación", "acreditación",
                "empresa", "académico", "médico", "laboral", "en vigor",
                "a petición del interesado", "diligencia"
            ],
            "fiscal": [
                "declaración", "modelo", "renta", "hacienda", "tributación",
                "irpf", "iva trimestral", "agencia tributaria", "contribuyente",
                "ejercicio fiscal", "liquidación", "retenciones", "autoliquidación",
                "ingresos", "gastos deducibles", "bases imponibles"
            ],
            "notificacion": [
                "notificación", "comunicación", "administración", "resolución",
                "se le notifica", "se le comunica", "organismo", "procede",
                "expediente", "recurso", "alegaciones", "plazo", "boletín oficial",
                "requerimiento", "apertura de procedimiento"
            ]
        }

        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        try:
            print(f"[INFO] Cargando modelo BETO: {MODEL_NAME}")
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            self.model = AutoModel.from_pretrained(MODEL_NAME)
            self.model.to(self.device)
            self.model.eval()
            print(f"[INFO] Modelo BETO cargado correctamente en {self.device}")
        except Exception as e:
            print(f"[WARNING] No se pudo cargar BETO: {e}")
            print("[WARNING] Usando clasificación basada en keywords solamente")

    def _keyword_classification(self, text: str) -> Tuple[str, float]:
        """
        Clasificación basada en palabras clave.
        Retorna (tipo, confianza)
        """
        text_lower = text.lower()
        scores = {}

        for doc_type, keywords in self.keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            scores[doc_type] = count

        # Si no hay coincidencias, clasificar como "otro"
        if max(scores.values()) == 0:
            return "otro", 0.3

        # Obtener el tipo con más coincidencias
        best_type = max(scores, key=scores.get)
        max_score = scores[best_type]

        # Calcular confianza (normalizada entre 0.5 y 0.95)
        confidence = min(0.5 + (max_score * 0.1), 0.95)

        return best_type, confidence

    def _extract_embeddings(self, text: str) -> np.ndarray:
        """
        Extrae embeddings del texto usando BETO.
        """
        if not self.model or not self.tokenizer:
            return None

        try:
            # Tokenizar (máximo 512 tokens)
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Obtener embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Usar el embedding del token [CLS] como representación del documento
                embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()

            return embeddings[0]
        except Exception as e:
            print(f"[ERROR] Error al extraer embeddings: {e}")
            return None

    def classify_text(self, text: str, username: str = None) -> Dict:
        """
        Clasifica un texto y retorna el tipo de documento con su confianza.

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
                "carpeta_sugerida": f"/{username}/Documentos/Otros" if username else "/Documentos/Otros"
            }

        # Clasificación basada en keywords
        tipo, confianza = self._keyword_classification(text)

        # Si tenemos BETO cargado, podemos mejorar la clasificación
        # (por ahora solo usamos keywords, pero dejamos preparado para fine-tuning)
        if self.model:
            embeddings = self._extract_embeddings(text)
            if embeddings is not None:
                # Aquí se podría usar un clasificador entrenado sobre los embeddings
                # Por ahora, mantenemos la clasificación por keywords pero con mayor confianza
                confianza = min(confianza + 0.1, 0.98)

        # Generar carpeta sugerida
        carpeta_base = self.folder_mapping.get(tipo, "/Documentos/Otros")
        carpeta_sugerida = f"/{username}{carpeta_base}" if username else carpeta_base

        return {
            "tipo_documento": tipo,
            "confianza": float(confianza),
            "carpeta_sugerida": carpeta_sugerida
        }

    def train(self, texts: List[str], labels: List[str]):
        """
        Placeholder para entrenamiento futuro.
        Aquí se implementaría el fine-tuning de BETO.
        """
        print("[INFO] Entrenamiento no implementado aún.")
        print("[INFO] Usar clasificación basada en keywords y embeddings.")
        pass
