# Integración del Sistema de Clasificación IA con el Backend

Este documento explica cómo integrar el sistema de clasificación de documentos con el backend Flask de DirectIA.

## Requisitos Previos

1. Instalar dependencias de IA:
```bash
pip install -r ai/requirements_ai.txt
```

2. Generar dataset y entrenar modelo:
```bash
# Generar datos sintéticos
python -m ai.data_generation.generate_dataset --num-docs 100

# Entrenar modelo
python -m ai.training.train_model
```

## Integración en Flask

### 1. Crear el endpoint `/api/clasificar`

Agregar el siguiente código al archivo principal de la aplicación Flask (por ejemplo, `backend/app.py` o `backend/routes/files.py`):

```python
from flask import Blueprint, request, jsonify
from ai.inference.classifier import DocumentClassifier
import os

# Crear blueprint (si no existe)
ai_bp = Blueprint('ai', __name__)

# Inicializar el clasificador (una sola vez al iniciar la app)
try:
    classifier = DocumentClassifier(
        model_dir='ai/models/v1_tfidf_svm',
        config_path='ai/config/categories.json'
    )
    print("✓ AI Classifier initialized successfully")
except Exception as e:
    print(f"⚠ Warning: Could not initialize AI classifier: {e}")
    classifier = None


@ai_bp.route('/api/clasificar', methods=['POST'])
def clasificar_documento():
    """
    Clasificar un documento usando IA

    Request:
        - file: archivo a clasificar (multipart/form-data)
        - user: username (opcional, para determinar carpeta base)

    Response:
        {
            "tipo_documento": "Factura",
            "confianza": 0.95,
            "confidence_level": "high",
            "carpeta_sugerida": "/username/Documentos/Facturas/",
            "descripcion": "Documentos de facturación con conceptos, IVA...",
            "top_predictions": [
                {"category": "Factura", "confidence": 0.95},
                {"category": "Presupuesto", "confidence": 0.03},
                {"category": "Recibo", "confidence": 0.01}
            ],
            "metadata": {
                "file_name": "documento.pdf",
                "file_extension": "pdf",
                "text_length": 1234,
                "text_preview": "FACTURA N.º..."
            }
        }
    """
    # Verificar que el clasificador esté disponible
    if classifier is None:
        return jsonify({
            'success': False,
            'error': 'El sistema de clasificación IA no está disponible'
        }), 503

    # Verificar que se envió un archivo
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No se proporcionó ningún archivo'
        }), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No se seleccionó ningún archivo'
        }), 400

    # Obtener username (opcional)
    username = request.form.get('user', 'usuario')

    try:
        # Leer el contenido del archivo
        file_bytes = file.read()

        # Obtener la extensión del archivo
        file_extension = os.path.splitext(file.filename)[1].lstrip('.')

        # Clasificar el documento
        result = classifier.classify_file_bytes(
            file_bytes=file_bytes,
            file_extension=file_extension,
            file_name=file.filename
        )

        # Ajustar la carpeta sugerida para incluir el username
        if 'carpeta_sugerida' in result:
            # Reemplazar /Documentos/ por /username/Documentos/
            carpeta = result['carpeta_sugerida']
            if carpeta.startswith('/Documentos/'):
                result['carpeta_sugerida'] = f'/{username}{carpeta}'

        # Agregar flag de éxito
        result['success'] = True

        return jsonify(result), 200

    except ValueError as e:
        # Error en extracción de texto
        return jsonify({
            'success': False,
            'error': f'Error al procesar el archivo: {str(e)}'
        }), 400

    except Exception as e:
        # Error general
        return jsonify({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }), 500


@ai_bp.route('/api/clasificar/categorias', methods=['GET'])
def obtener_categorias():
    """
    Obtener lista de categorías disponibles

    Response:
        {
            "success": true,
            "categories": [
                {
                    "id": "factura",
                    "name": "Factura",
                    "name_en": "Invoice",
                    "folder_path": "/Documentos/Facturas/",
                    "description": "Documentos de facturación..."
                },
                ...
            ]
        }
    """
    if classifier is None:
        return jsonify({
            'success': False,
            'error': 'El sistema de clasificación IA no está disponible'
        }), 503

    try:
        categories = classifier.get_categories()
        return jsonify({
            'success': True,
            'categories': categories
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/api/clasificar/info', methods=['GET'])
def obtener_info_modelo():
    """
    Obtener información sobre el modelo de IA

    Response:
        {
            "success": true,
            "model_info": {
                "model_type": "SVC",
                "training_date": "2025-01-15T10:30:00",
                "vocabulary_size": 5000,
                "num_categories": 9,
                "metrics": {...}
            }
        }
    """
    if classifier is None:
        return jsonify({
            'success': False,
            'error': 'El sistema de clasificación IA no está disponible'
        }), 503

    try:
        info = classifier.get_model_info()
        return jsonify({
            'success': True,
            'model_info': info
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Registrar el blueprint en la aplicación Flask
def register_ai_routes(app):
    """Registrar rutas de IA en la aplicación Flask"""
    app.register_blueprint(ai_bp)
```

### 2. Registrar el blueprint en la aplicación

En el archivo principal de la aplicación (por ejemplo, `backend/app.py`):

```python
from flask import Flask
# ... otros imports

# Importar función de registro
from routes.ai import register_ai_routes  # o donde hayas puesto el código

app = Flask(__name__)

# ... configuración de Flask

# Registrar rutas de IA
register_ai_routes(app)

# ... resto de la aplicación
```

### 3. Actualizar CORS (si es necesario)

Si usas Flask-CORS, asegúrate de permitir el endpoint:

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## Integración en el Frontend

### Actualizar UploadModal.jsx

El frontend ya tiene el código para llamar al endpoint `/api/clasificar`. Verificar que el archivo `src/components/UploadModal.jsx` tenga algo similar a:

```javascript
const handleAIClassification = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user', username);

    const response = await api.post('/api/clasificar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (response.data.success) {
      const { tipo_documento, confianza, carpeta_sugerida, confidence_level } = response.data;

      // Mostrar sugerencia al usuario
      const shouldMove = window.confirm(
        `IA sugiere clasificar como "${tipo_documento}" (confianza: ${(confianza * 100).toFixed(1)}%)\n\n` +
        `Carpeta sugerida: ${carpeta_sugerida}\n\n` +
        `¿Deseas mover el archivo a esta ubicación?`
      );

      if (shouldMove) {
        // Mover archivo a la carpeta sugerida
        await api.post('/api/files/move', {
          source: currentPath + file.name,
          destination: carpeta_sugerida + file.name,
        });
      }
    }
  } catch (error) {
    console.error('Error en clasificación IA:', error);
  }
};
```

## Manejo de Errores

El endpoint maneja varios casos de error:

1. **Clasificador no inicializado** (503): El modelo no se pudo cargar
2. **Sin archivo** (400): No se envió ningún archivo
3. **Error de extracción** (400): No se pudo extraer texto del documento
4. **Error interno** (500): Error inesperado

## Testing

### Test básico con curl

```bash
curl -X POST http://localhost:5001/api/clasificar \
  -F "file=@/path/to/factura.pdf" \
  -F "user=testuser"
```

### Test desde Python

```python
import requests

url = 'http://localhost:5001/api/clasificar'

with open('factura.pdf', 'rb') as f:
    files = {'file': f}
    data = {'user': 'testuser'}
    response = requests.post(url, files=files, data=data)

print(response.json())
```

## Optimizaciones

### 1. Cache de predicciones

Para evitar clasificar el mismo documento múltiples veces:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def classify_cached(file_hash, file_extension):
    return classifier.classify_file_bytes(file_bytes, file_extension)
```

### 2. Clasificación asíncrona

Para documentos grandes, usar Celery o RQ:

```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def classify_document_async(file_path, username):
    result = classifier.classify_file(file_path)
    # Guardar resultado en base de datos
    return result
```

### 3. Batch processing

Para clasificar múltiples documentos:

```python
@ai_bp.route('/api/clasificar/batch', methods=['POST'])
def clasificar_batch():
    files = request.files.getlist('files')
    results = []

    for file in files:
        result = classifier.classify_file_bytes(...)
        results.append(result)

    return jsonify({'results': results})
```

## Monitoreo

### Logging

Agregar logs para monitorear el rendimiento:

```python
import logging
import time

logger = logging.getLogger(__name__)

@ai_bp.route('/api/clasificar', methods=['POST'])
def clasificar_documento():
    start_time = time.time()

    try:
        result = classifier.classify_file_bytes(...)

        elapsed = time.time() - start_time
        logger.info(f"Classification successful in {elapsed:.2f}s: {result['tipo_documento']}")

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        raise
```

### Métricas

Guardar métricas de uso:

```python
from collections import Counter

classification_stats = Counter()

@ai_bp.route('/api/clasificar', methods=['POST'])
def clasificar_documento():
    result = classifier.classify_file_bytes(...)

    # Registrar estadísticas
    classification_stats[result['tipo_documento']] += 1

    return jsonify(result), 200

@ai_bp.route('/api/clasificar/stats', methods=['GET'])
def obtener_estadisticas():
    return jsonify({
        'total_classifications': sum(classification_stats.values()),
        'by_category': dict(classification_stats)
    })
```

## Troubleshooting

### Problema: "Model not found"

**Solución**: Asegúrate de haber entrenado el modelo:
```bash
python -m ai.training.train_model
```

### Problema: "Tesseract not found" (OCR)

**Solución**: Instalar Tesseract OCR:
- Windows: Descargar de https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-spa`
- macOS: `brew install tesseract tesseract-lang`

### Problema: Baja precisión

**Soluciones**:
1. Generar más datos sintéticos: `--num-docs 200`
2. Ajustar hiperparámetros del modelo
3. Reentrenar con documentos reales anonimizados
4. Considerar migrar a modelo v2 (BERT)

## Próximos Pasos

1. ✓ Integrar endpoint básico
2. Implementar clasificación asíncrona
3. Agregar feedback del usuario para mejorar el modelo
4. Implementar re-entrenamiento automático
5. Migrar a modelo v2 (BERT) para mayor precisión
