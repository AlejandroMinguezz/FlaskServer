"""
Clasificador de documentos optimizado basado en keywords.
Versión simplificada sin BETO para mejor performance.
"""

import re
from typing import Dict, Tuple


class DocumentClassifier:
    """
    Clasificador ligero basado en keywords para fallback.
    Sin BETO - Optimizado para velocidad y bajo consumo de recursos.
    """

    def __init__(self):
        # Clases de documentos soportadas
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

        # Palabras clave para cada tipo (optimizadas y priorizadas)
        self.keywords = {
            "factura": {
                "strong": ["factura", "invoice", "nº factura", "número de factura"],
                "medium": ["iva", "base imponible", "total a pagar", "proveedor"],
                "weak": ["importe", "precio unitario", "cantidad", "subtotal"]
            },
            "contrato": {
                "strong": ["contrato", "cláusula", "partes contratantes"],
                "medium": ["acuerdo", "estipula", "compromiso", "obligaciones"],
                "weak": ["firma", "condiciones", "vigencia"]
            },
            "nomina": {
                "strong": ["nómina", "nomina", "líquido a percibir"],
                "medium": ["irpf", "seguridad social", "devengos", "deducciones"],
                "weak": ["salario", "cotización", "trabajador"]
            },
            "presupuesto": {
                "strong": ["presupuesto", "cotización", "validez"],
                "medium": ["oferta", "propuesta económica", "estimación"],
                "weak": ["coste", "válido hasta"]
            },
            "recibo": {
                "strong": ["recibo", "receipt", "recibí"],
                "medium": ["pago", "abono", "mensualidad", "consumo"],
                "weak": ["cuota", "domiciliación", "cargo"]
            },
            "certificado": {
                "strong": ["certificado", "certifica", "se expide"],
                "medium": ["acredita", "expedido por", "certificación"],
                "weak": ["hace constar", "acreditación"]
            },
            "fiscal": {
                "strong": ["declaración", "modelo", "hacienda", "agencia tributaria"],
                "medium": ["renta", "tributación", "irpf trimestral"],
                "weak": ["contribuyente", "ejercicio fiscal"]
            },
            "notificacion": {
                "strong": ["notificación", "se le notifica", "resolución administrativa"],
                "medium": ["comunicación", "administración", "expediente"],
                "weak": ["recurso", "alegaciones", "plazo"]
            }
        }

        print("[INFO] Clasificador optimizado inicializado (sin BETO)")

    def _keyword_classification(self, text: str) -> Tuple[str, float]:
        """
        Clasificación optimizada basada en palabras clave priorizadas.

        Returns:
            Tupla (tipo, confianza)
        """
        text_lower = text.lower()
        scores = {}

        # Pesos para diferentes niveles de keywords
        weights = {
            "strong": 3.0,
            "medium": 1.5,
            "weak": 0.5
        }

        for doc_type, keyword_levels in self.keywords.items():
            score = 0.0

            for level, keywords in keyword_levels.items():
                weight = weights[level]
                for keyword in keywords:
                    if keyword in text_lower:
                        score += weight

            scores[doc_type] = score

        # Si no hay coincidencias, clasificar como "otro"
        if max(scores.values()) == 0:
            return "otro", 0.3

        # Obtener el tipo con más puntuación
        best_type = max(scores, key=scores.get)
        max_score = scores[best_type]

        # Calcular confianza (normalizada entre 0.5 y 0.92)
        # Puntuaciones típicas: 0.5-2.0 (baja), 3.0-10.0 (media), 10+ (alta)
        if max_score < 2.0:
            confidence = 0.50 + (max_score / 2.0) * 0.15  # 0.50-0.65
        elif max_score < 10.0:
            confidence = 0.65 + ((max_score - 2.0) / 8.0) * 0.20  # 0.65-0.85
        else:
            confidence = 0.85 + min((max_score - 10.0) / 10.0, 1.0) * 0.07  # 0.85-0.92

        return best_type, confidence

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
                "carpeta_sugerida": "/Documentos/Otros"
            }

        # Clasificación basada en keywords
        tipo, confianza = self._keyword_classification(text)

        # Generar carpeta sugerida (sin prefijo de usuario/grupo)
        carpeta_sugerida = self.folder_mapping.get(tipo, "/Documentos/Otros")

        return {
            "tipo_documento": tipo,
            "confianza": float(confianza),
            "carpeta_sugerida": carpeta_sugerida
        }

    def get_supported_classes(self) -> list:
        """Retorna las clases soportadas."""
        return self.classes
