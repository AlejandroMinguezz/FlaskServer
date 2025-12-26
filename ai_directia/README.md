# DirectIA - Sistema de Clasificación IA de Documentos

Sistema de clasificación automática de documentos administrativos usando Machine Learning.

## 📋 Índice

- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Guía de Uso Rápida](#guía-de-uso-rápida)
- [Categorías de Documentos](#categorías-de-documentos)
- [Pipeline de Clasificación](#pipeline-de-clasificación)
- [Integración con Backend](#integración-con-backend)
- [Testing y Debugging](#testing-y-debugging)
- [Métricas y Rendimiento](#métricas-y-rendimiento)

## Estructura del Proyecto

```
ai/
├── datasets/              # Datasets para entrenamiento
│   ├── raw/              # Documentos originales por categoría
│   ├── processed/        # Datos procesados (train/val/test CSV)
│   └── synthetic/        # Datos sintéticos generados
├── models/               # Modelos entrenados y vectorizadores
│   └── v1_tfidf_svm/    # Modelo v1 (TF-IDF + SVM)
│       ├── model.pkl
│       ├── vectorizer.pkl
│       └── metadata.json
├── extractors/           # Extracción de texto (PDF, DOCX, TXT, OCR)
│   ├── pdf_extractor.py
│   ├── docx_extractor.py
│   ├── txt_extractor.py
│   ├── ocr_extractor.py
│   └── unified_extractor.py
├── preprocessing/        # Pipeline de preprocesamiento
│   ├── text_cleaner.py
│   └── feature_extractor.py
├── training/            # Scripts de entrenamiento
│   └── train_model.py
├── inference/           # Clasificación en tiempo real
│   └── classifier.py
├── data_generation/     # Generación de datos sintéticos
│   ├── template_generator.py
│   ├── augmentation.py
│   └── generate_dataset.py
├── config/              # Configuración y categorías
│   └── categories.json
├── requirements_ai.txt  # Dependencias del sistema IA
├── test_classifier.py   # Script de pruebas
├── BACKEND_INTEGRATION.md  # Guía de integración
└── README.md           # Este archivo
```

## Instalación

### 1. Instalar Dependencias Python

```bash
pip install -r ai/requirements_ai.txt
```

### 2. Descargar Recursos de NLP

```bash
# Stopwords de NLTK (opcional pero recomendado)
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

### 3. Instalar Tesseract OCR (para reconocimiento de imágenes)

**Windows:**
- Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
- Instalar y agregar al PATH

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-spa
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

## Guía de Uso Rápida

### Paso 1: Generar Dataset Sintético

```bash
# Generar 100 documentos por categoría (+ 3 variaciones = 400 por categoría)
python -m ai.data_generation.generate_dataset --num-docs 100 --num-variations 3

# Resultado: ~3,600 documentos en total (9 categorías × 400 docs)
# Guardados en: ai/datasets/processed/ (train.csv, val.csv, test.csv)
```

**Opciones adicionales:**
```bash
# Generar más documentos para mejor precisión
python -m ai.data_generation.generate_dataset --num-docs 200

# No guardar archivos TXT individuales (más rápido)
python -m ai.data_generation.generate_dataset --no-txt

# Ajustar proporciones del split
python -m ai.data_generation.generate_dataset --train-ratio 0.8 --val-ratio 0.1 --test-ratio 0.1
```

### Paso 2: Entrenar el Modelo

```bash
# Entrenar modelo SVM (recomendado)
python -m ai.training.train_model

# Opciones avanzadas:
python -m ai.training.train_model \
  --model-type svm \
  --max-features 5000 \
  --svm-kernel linear \
  --svm-c 1.0 \
  --output-dir ai/models/v1_tfidf_svm
```

**Modelos disponibles:**
- `svm`: Support Vector Machine (mejor precisión, recomendado)
- `naive_bayes`: Naive Bayes (más rápido, menor precisión)
- `random_forest`: Random Forest (balance entre velocidad y precisión)

### Paso 3: Usar el Clasificador

#### Desde Python:

```python
from ai.inference.classifier import DocumentClassifier

# Inicializar clasificador
classifier = DocumentClassifier(
    model_dir='ai/models/v1_tfidf_svm',
    config_path='ai/config/categories.json'
)

# Clasificar archivo
result = classifier.classify_file('ruta/a/documento.pdf')

print(f"Tipo: {result['tipo_documento']}")
print(f"Confianza: {result['confianza']:.2%}")
print(f"Carpeta sugerida: {result['carpeta_sugerida']}")

# Clasificar desde bytes (útil para APIs)
with open('documento.pdf', 'rb') as f:
    file_bytes = f.read()

result = classifier.classify_file_bytes(file_bytes, 'pdf', 'documento.pdf')
```

#### Desde línea de comandos:

```bash
# Clasificar un archivo
python ai/test_classifier.py --file ruta/a/documento.pdf

# Clasificar texto directo
python ai/test_classifier.py --text "FACTURA N.º 1234..."

# Probar con documentos sintéticos
python ai/test_classifier.py --test-synthetic

# Ver categorías disponibles
python ai/test_classifier.py --show-categories

# Ver información del modelo
python ai/test_classifier.py --show-info
```

## Categorías de Documentos

El sistema clasifica documentos en 9 categorías:

| ID | Nombre | Carpeta | Palabras Clave |
|----|--------|---------|----------------|
| `factura` | Factura | `/Documentos/Facturas/` | factura, invoice, IVA, total, importe, CIF |
| `contrato` | Contrato | `/Documentos/Contratos/` | contrato, cláusula, firmante, vigencia |
| `nomina` | Nómina | `/Documentos/Nóminas/` | nómina, salario, IRPF, seguridad social |
| `presupuesto` | Presupuesto | `/Documentos/Presupuestos/` | presupuesto, cotización, validez, oferta |
| `recibo` | Recibo | `/Documentos/Recibos/` | recibo, pago, consumo, alquiler |
| `certificado` | Certificado | `/Documentos/Certificados/` | certificado, acredita, expedido por |
| `fiscal` | Declaración Fiscal | `/Documentos/Fiscales/` | declaración, modelo, renta, hacienda |
| `notificacion` | Notificación Admin | `/Documentos/Notificaciones/` | notificación, administración, expediente |
| `otro` | Otro | `/Documentos/Otros/` | (catch-all para documentos no clasificables) |

## Pipeline de Clasificación

```
Documento (PDF/DOCX/TXT/IMG)
         ↓
[1. EXTRACCIÓN DE TEXTO]
  - PDF: pdfplumber
  - DOCX: python-docx
  - TXT: lectura directa
  - IMG: Tesseract OCR
         ↓
      Texto plano
         ↓
[2. PREPROCESAMIENTO]
  - Normalización Unicode
  - Limpieza de espacios
  - Eliminación de URLs/emails
  - Tokenización
  - Eliminación de stopwords
         ↓
  Texto preprocesado
         ↓
[3. EXTRACCIÓN DE FEATURES]
  - Vectorización TF-IDF
  - Max features: 5000
  - N-grams: (1, 2)
         ↓
   Vector de características
         ↓
[4. CLASIFICACIÓN]
  - Modelo SVM entrenado
  - Predicción + probabilidades
         ↓
[5. POST-PROCESAMIENTO]
  - Mapeo a categoría
  - Generación de carpeta sugerida
  - Determinación de nivel de confianza
         ↓
Resultado JSON con predicción
```

## Integración con Backend

Ver documentación completa en: [BACKEND_INTEGRATION.md](ai/BACKEND_INTEGRATION.md:1)

### Resumen Rápido

```python
# En tu aplicación Flask
from ai.inference.classifier import DocumentClassifier

classifier = DocumentClassifier()

@app.route('/api/clasificar', methods=['POST'])
def clasificar_documento():
    file = request.files['file']
    file_bytes = file.read()
    file_extension = os.path.splitext(file.filename)[1].lstrip('.')

    result = classifier.classify_file_bytes(
        file_bytes=file_bytes,
        file_extension=file_extension,
        file_name=file.filename
    )

    return jsonify(result), 200
```

## Testing y Debugging

### Probar el Sistema Completo

```bash
# 1. Generar datos
python -m ai.data_generation.generate_dataset --num-docs 50

# 2. Entrenar modelo
python -m ai.training.train_model

# 3. Probar con documentos sintéticos
python ai/test_classifier.py --test-synthetic

# 4. Ver información del modelo
python ai/test_classifier.py --show-info
```

### Verificar Extracción de Texto

```python
from ai.extractors import extract_text

result = extract_text('documento.pdf')
print(f"Éxito: {result['success']}")
print(f"Texto extraído: {result['text'][:500]}")
print(f"Error: {result.get('error', 'N/A')}")
```

### Verificar Preprocesamiento

```python
from ai.preprocessing import preprocess_text

text = "FACTURA N.º 1234, TOTAL: 1,500.00€"
processed = preprocess_text(text)
print(f"Original: {text}")
print(f"Procesado: {processed}")
```

## Métricas y Rendimiento

### Objetivos de Rendimiento

| Métrica | Objetivo | Descripción |
|---------|----------|-------------|
| **Accuracy** | > 85% | Porcentaje de predicciones correctas |
| **F1-Score (macro)** | > 0.80 | Balance entre precisión y recall |
| **Tiempo de inferencia** | < 2s | Tiempo para clasificar un documento |
| **Formatos soportados** | PDF, DOCX, TXT, IMG | Tipos de documentos procesables |

### Ver Métricas del Modelo

```bash
# Ver métricas desde CLI
python ai/test_classifier.py --show-info

# O desde Python:
from ai.inference.classifier import DocumentClassifier
classifier = DocumentClassifier()
info = classifier.get_model_info()
print(f"Accuracy: {info['metrics']['test']['accuracy']:.2%}")
print(f"F1-Score: {info['metrics']['test']['f1_macro']:.2%}")
```

### Mejorar el Rendimiento

Si la precisión es baja:

1. **Generar más datos:**
   ```bash
   python -m ai.data_generation.generate_dataset --num-docs 200 --num-variations 5
   ```

2. **Ajustar hiperparámetros:**
   ```bash
   python -m ai.training.train_model --max-features 10000 --svm-c 2.0
   ```

3. **Probar otros modelos:**
   ```bash
   python -m ai.training.train_model --model-type random_forest
   ```

4. **Reentrenar con documentos reales** (si están disponibles)

## Troubleshooting

### Error: "Model not found"

```bash
# Solución: Entrenar el modelo
python -m ai.training.train_model
```

### Error: "Tesseract not found"

```bash
# Windows: Instalar Tesseract y agregar al PATH
# Linux: sudo apt-get install tesseract-ocr tesseract-ocr-spa
# macOS: brew install tesseract tesseract-lang
```

### Baja precisión en clasificación

1. Generar más datos sintéticos
2. Ajustar hiperparámetros del modelo
3. Verificar que las palabras clave en `config/categories.json` sean representativas
4. Considerar reentrenar con documentos reales

### Lentitud en clasificación

1. Usar modelo más ligero: `--model-type naive_bayes`
2. Reducir features: `--max-features 3000`
3. Implementar caché para documentos repetidos

## Próximos Pasos

- [ ] Implementar feedback del usuario para mejorar el modelo
- [ ] Agregar soporte para más tipos de documentos
- [ ] Implementar modelo v2 con BERT fine-tuned
- [ ] Agregar clasificación multiidioma
- [ ] Implementar extracción de entidades (fechas, importes, nombres)
- [ ] Agregar detección de duplicados
- [ ] Implementar búsqueda semántica

## Versión

- **v1.0** (actual): ML tradicional (TF-IDF + SVM)
- **v2.0** (futuro): Deep Learning (BERT fine-tuned para español)
