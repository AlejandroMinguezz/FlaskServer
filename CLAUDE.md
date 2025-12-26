# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DirectIA** is a Flask-based document management system with AI-powered OCR and classification capabilities. It integrates machine learning models for Spanish document classification, stores data in MongoDB (metadata/AI results) and PostgreSQL (users/roles/groups), and provides a comprehensive REST API for document management.

## Project Structure

```
FlaskServerTFG/
├── src/
│   ├── app.py                    # Application factory and entry point
│   ├── config.py                 # Configuration from .env
│   ├── models.py                 # SQLAlchemy models (PostgreSQL)
│   ├── utils.py                  # Utility functions
│   ├── routes/                   # API blueprints
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── files.py             # File operations
│   │   ├── ia.py                # AI classification endpoint
│   │   ├── metadata.py          # Metadata access
│   │   ├── health.py            # Health checks
│   │   ├── admin.py             # Admin panel
│   │   ├── folder_structure.py  # Folder template management
│   │   └── file_icons_route.py  # File icon utilities
│   ├── services/                 # Business logic
│   │   └── ia.py                # AI service integration
│   ├── ia/                       # AI/ML pipeline
│   │   ├── pipeline.py          # Main processing pipeline
│   │   ├── classifier.py        # Keyword-based classifier (fallback)
│   │   ├── classifier_ml.py     # ML-based classifier (primary)
│   │   ├── utils.py             # Text cleaning utilities
│   │   ├── ocr/                 # OCR processing
│   │   │   ├── __init__.py      # Unified extract_text() function
│   │   │   ├── ocr.py           # Tesseract OCR for PDF/images
│   │   │   └── mistral_ocr.py   # Alternative OCR implementation
│   │   ├── clasificadores/      # Classification modules
│   │   │   ├── beto/            # BETO (Spanish BERT) integration
│   │   │   └── fallback/        # OpenAI/Gemini verification
│   │   ├── data_generation/     # Synthetic dataset generation
│   │   │   ├── base_generator.py
│   │   │   ├── augmentation.py
│   │   │   ├── generate_dataset.py
│   │   │   └── generators/      # 8 document type generators
│   │   ├── training/            # ML model training
│   │   │   └── train_model.py
│   │   ├── datasets/            # Generated datasets
│   │   │   └── processed/       # train.csv, val.csv, test.csv
│   │   └── models/              # Trained ML models
│   │       └── tfidf_svm_v1/    # Current production model
│   └── templates/               # HTML templates (admin panel)
├── docker/                       # Docker configuration
│   ├── docker-compose.yml       # PostgreSQL + MongoDB
│   └── .env                     # Docker environment variables
├── storage/                      # File storage (not in repo)
│   └── files/                   # User-uploaded documents
├── setup.ps1 / setup.sh         # Initial project setup
├── start_databases.ps1 / .sh    # Start Docker databases
├── start_flask.ps1 / .sh        # Start Flask server
├── requirements.txt             # Python dependencies
├── .env                         # Application configuration
└── CLAUDE.md                    # This file
```

**Nota sobre almacenamiento:**
- **Archivos de usuario**: `../storage/files/` (directorio local fuera del proyecto)
- **Datos de bases de datos**: Volúmenes Docker con nombre
  - `directia_postgres_data`: PostgreSQL data
  - `directia_mongo_data`: MongoDB data
- Esto evita problemas de permisos en macOS/Windows

## Getting Started

### 0. Setup inicial (Primera vez solamente)

Antes de ejecutar la aplicación por primera vez, ejecuta el script de setup:

**Windows:**
```powershell
.\setup.ps1
```

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

Este script:
- ✅ Verifica Python 3.8+ y pip
- ✅ Crea el entorno virtual (venv)
- ✅ Instala todas las dependencias de Python
- ✅ Verifica Tesseract OCR (requerido para OCR de PDF/imágenes)
- ✅ Crea los directorios necesarios (storage/files)
- ✅ Verifica la configuración (.env)
- ✅ Verifica Docker y Docker Compose

### 1. Iniciar las bases de datos (Docker)

Las bases de datos (PostgreSQL y MongoDB) corren en Docker:

**Windows:**
```powershell
.\start_databases.ps1
```

**Linux/macOS:**
```bash
./start_databases.sh
```

Esto iniciará:
- PostgreSQL en `localhost:5432`
- MongoDB en `localhost:27017`

### 2. Iniciar Flask localmente

Una vez las bases de datos están corriendo, inicia Flask:

**Windows:**
```powershell
.\start_flask.ps1
```

**Linux/macOS:**
```bash
./start_flask.sh
```

El servidor Flask estará disponible en `http://localhost:5001`

### 3. Detener las bases de datos

```bash
cd docker
docker-compose down
```

## Architecture

### Database Architecture (Dual Storage)

**PostgreSQL** (`src/models.py`): User authentication, authorization, and folder templates
- `users`: User accounts with password hashing (Werkzeug)
- `roles`: User roles (admin, user, etc.)
- `groups` / `group_members`: User group management
- `folder_templates`: Hierarchical folder structure templates

**MongoDB** (via `app.mongo`): Document metadata and AI processing results
- Collection: `metadata` - Stores file metadata, OCR results, and classification data

### Application Factory Pattern

The app is initialized using `create_app()` in `src/app.py`:
1. Creates Flask app and loads config from `src/config.py`
2. Establishes PostgreSQL connection with SQLAlchemy (scoped sessions)
3. Auto-creates missing tables by inspecting existing schema
4. Connects to MongoDB and exposes via `app.mongo`
5. Registers blueprints from `src/routes/__init__.py`

Access database connections in routes:
- PostgreSQL: `session = current_app.session()`
- MongoDB: `current_app.mongo[collection_name]`

### Route Blueprints

All API routes are registered via blueprints in `src/routes/`:

- **`/api/auth`** (`auth.py`): User registration, login, password changes
  - JWT tokens generated with 15min expiry (access) and 7 days (refresh)
  - Admin panel URL returned in login response

- **`/api/files`** (`files.py`): File operations
  - `GET /list`: List all files
  - `POST /upload?ia=true`: Upload file with optional AI processing
  - `GET /download/<path>`: Download file
  - `DELETE /delete/<path>`: Delete file/folder
  - `POST /create_folder`: Create directory
  - `POST /move`: Move files between folders

- **`/api/clasificar`** (`ia.py`): AI document classification
  - `POST /clasificar`: Classify a document and suggest folder location
  - Accepts: PDF, DOCX, DOC, TXT, JPG, PNG, BMP, TIFF
  - Returns: document type, confidence score, suggested folder path

- **`/api/metadata`** (`metadata.py`): Access file metadata from MongoDB
  - Retrieve OCR results and classification data

- **`/api/folder-structure`** (`folder_structure.py`): Folder template management
  - CRUD operations for hierarchical folder templates

- **`/api/health`** (`health.py`): Health check endpoints
  - System status and database connectivity checks

- **`/api/file-icons`** (`file_icons_route.py`): File icon utilities

- **`/admin`** (`admin.py`): Admin panel (requires JWT token in query param)

### AI Pipeline (2 Phases Implemented)

#### Phase 1: Multi-format OCR and Basic Classification

The AI processing flow (`src/ia/pipeline.py`):

1. **Text Extraction** (`src/ia/ocr/__init__.py`): Unified `extract_text()` function
   - **PDF**: Tesseract OCR (300 DPI, Spanish language model)
   - **DOCX/DOC**: python-docx library
   - **TXT**: Multi-encoding support (utf-8, latin-1, cp1252)
   - **Images** (JPG, PNG, BMP, TIFF): Tesseract OCR with preprocessing

2. **Text Cleaning** (`src/ia/utils.py`): Normalize and clean extracted text
   - Remove extra whitespace, normalize punctuation
   - Lowercase conversion
   - Special character handling

3. **Classification** (src/ia/pipeline.py` uses ML classifier with fallback):
   - **Primary**: `MLDocumentClassifier` (TF-IDF + Linear SVC)
   - **Fallback**: `DocumentClassifier` (keyword-based)

#### Phase 2: ML Model Training (COMPLETED)

**Dataset Generation** (`src/ia/data_generation/`):
- 8 specialized generators for Spanish administrative documents:
  - `factura` (invoice)
  - `nomina` (payroll)
  - `contrato` (contract)
  - `presupuesto` (budget)
  - `recibo` (receipt)
  - `certificado` (certificate)
  - `fiscal` (tax document)
  - `notificacion` (notification)
- Uses **Faker** library for realistic Spanish data
- **Data augmentation**: Simulates OCR errors, typos, formatting variations
- **Dataset size**: 4,800 examples (600 per category)
- **Split**: 70% train, 15% validation, 15% test

**ML Model** (`src/ia/classifier_ml.py`):
- Architecture: TF-IDF vectorization (5,000 features) + Linear SVC
- Performance: **100% accuracy** on synthetic data (85-95% expected on real documents)
- Training time: ~40 seconds
- Model size: ~1.7 MB
- Inference time: ~0.1 seconds per document

**Document Categories**:
| Category | Suggested Folder | Keywords |
|----------|-----------------|----------|
| factura | /Documentos/Facturas | factura, IVA, base imponible |
| nomina | /Documentos/Nóminas | nómina, IRPF, seguridad social |
| contrato | /Documentos/Contratos | contrato, cláusula, partes |
| presupuesto | /Documentos/Presupuestos | presupuesto, cotización, validez |
| recibo | /Documentos/Recibos | recibo, pago, consumo |
| certificado | /Documentos/Certificados | certificado, certifica, se expide |
| fiscal | /Documentos/Fiscales | declaración, hacienda, modelo |
| notificacion | /Documentos/Notificaciones | notificación, administración |

### File Upload with AI Classification

When uploading via `/api/files/upload?ia=true`:
1. File is saved to `storage/files/`
2. Optional: AI classification triggered
3. `extract_text()` extracts text from document
4. `clean_text()` normalizes the text
5. `MLDocumentClassifier.classify_text()` predicts document type
6. Results stored in MongoDB `metadata` collection
7. Response includes: document type, confidence, suggested folder path

When using `/api/clasificar` directly:
1. Upload file with username
2. Returns classification immediately
3. Frontend can suggest moving file to recommended folder

### Configuration

La configuración es simple y centralizada en un único archivo `.env`:

**Archivo `.env` (raíz del proyecto):**
```bash
# Flask
FLASK_DEBUG=1
PORT=5001
SECRET_KEY=fe8d9cbee10295cf3227f0541a64c9ec84d3951c2e93575d54568763d05ebe60

# PostgreSQL (en Docker, acceso desde localhost)
POSTGRES_USER=directia_user
POSTGRES_PASSWORD=directia_pass
POSTGRES_DB=directia
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# MongoDB (en Docker, acceso desde localhost)
MONGO_USER=directia_user
MONGO_PASS=directia_pass
MONGO_DB=directia
MONGO_URI=mongodb://directia_user:directia_pass@localhost:27017/directia?authSource=admin

# Storage (un nivel arriba del proyecto)
STORAGE_PATH=../storage/files
```

**Archivo `docker/.env` (solo para Docker Compose):**
```bash
# Credenciales de bases de datos
POSTGRES_USER=directia_user
POSTGRES_PASSWORD=directia_pass
POSTGRES_DB=directia

MONGO_USER=directia_user
MONGO_PASS=directia_pass
MONGO_DB=directia
```

**Configuración** (`src/config.py`):
- Una única clase `Config` que lee del archivo `.env`
- No hay múltiples entornos (development/production/test)
- Configuración simple y directa

### Docker Services

El `docker-compose.yml` define solo las bases de datos:
- **postgres**: PostgreSQL 15 con health checks
  - Volumen: `directia_postgres_data` (datos persistentes)
- **mongo**: MongoDB 6.0 con autenticación
  - Volumen: `directia_mongo_data` (datos persistentes)

**Nota importante:** Se usan volúmenes Docker con nombre para evitar problemas de permisos en macOS/Windows.

Flask se ejecuta localmente fuera de Docker.

## Development Notes

### Database Session Management
Always close PostgreSQL sessions in routes:
```python
session = current_app.session()
try:
    # ... database operations
finally:
    session.close()
```

### JWT Authentication
Admin endpoints require token verification. The token is included in login responses and can be passed as a query parameter (`?token=...`).

### AI Model Management

**Current Model**: `tfidf_svm_v1`
- Location: `src/ia/models/tfidf_svm_v1/`
- Files: `model.pkl`, `vectorizer.pkl`, `metadata.json`, `evaluation_report.json`
- Automatically loaded on Flask startup
- Fallback: If ML model fails to load, system uses keyword-based classifier

**Regenerating Dataset**:
```bash
python -m src.ia.data_generation.generate_dataset
```

**Retraining Model**:
```bash
python -m src.ia.training.train_model
```

**Testing Classification**:
```python
from src.ia.classifier_ml import MLDocumentClassifier

classifier = MLDocumentClassifier()
result = classifier.classify_text("FACTURA N.º 2025/001...", username="testuser")
# Returns: {"tipo_documento": "factura", "confianza": 0.95, "carpeta_sugerida": "/testuser/Documentos/Facturas"}
```

### Startup Scripts

**Setup inicial (ejecutar una sola vez):**
- `setup.ps1` / `setup.sh`: Configura el entorno de desarrollo completo
- Crea entorno virtual y instala dependencias
- Verifica Python, pip, Tesseract OCR y Docker
- Crea directorios necesarios y verifica configuración

**Bases de datos (Docker):**
- `start_databases.ps1` / `start_databases.sh`: Inicia PostgreSQL y MongoDB en Docker
- Verifica que Docker esté instalado y corriendo
- Muestra información de conexión y logs

**Flask (local):**
- `start_flask.ps1` / `start_flask.sh`: Inicia el servidor Flask localmente
- Verifica que Python esté instalado
- Verifica que las bases de datos estén corriendo
- Ejecuta `python src/app.py`

### Configuration Tips

1. **Variables de debug**: Cambia `FLASK_DEBUG` en `.env` para activar/desactivar el modo debug
2. **Puerto**: Cambia `PORT` en `.env` si necesitas otro puerto (default: 5001)
3. **SECRET_KEY**: Genera una clave segura con `python -c "import secrets; print(secrets.token_hex(32))"`
4. **Storage**: Ajusta `STORAGE_PATH` si quieres cambiar la ubicación de archivos
5. **Docker Volumes**: Para gestionar los volúmenes Docker:
   - Listar: `docker volume ls`
   - Inspeccionar: `docker volume inspect directia_postgres_data`
   - Eliminar (¡CUIDADO!): `cd docker && docker-compose down -v`

## Key Dependencies

```txt
# Core Framework
Flask==2.3.3                    # Web framework
flask-cors==6.0.1              # CORS support
SQLAlchemy==2.0.44             # PostgreSQL ORM
psycopg2-binary==2.9.11        # PostgreSQL driver
pymongo==4.6.3                 # MongoDB driver

# Authentication
pyjwt==2.10.1                  # JWT tokens
Werkzeug==2.3.8                # Password hashing

# AI/ML
scikit-learn==1.7.2            # ML models (TF-IDF, SVM)
transformers>=4.40             # BERT/BETO models
torch>=2.6                     # PyTorch (for BERT)
tensorflow==2.19.1             # TensorFlow (alternative)

# OCR
pytesseract==0.3.13            # Tesseract OCR wrapper
opencv-python==4.12.0.88       # Image preprocessing
pillow==11.3.0                 # Image handling
pdf2image==1.17.0              # PDF to image conversion
python-docx==1.1.2             # DOCX text extraction

# Data Generation
Faker==22.6.0                  # Synthetic data generation
tqdm==4.66.1                   # Progress bars

# Utilities
python-dotenv==1.1.1           # .env file support
joblib==1.5.2                  # Model serialization
pandas==2.3.2                  # Dataset handling
numpy==2.1.3                   # Numerical operations
```

## AI Implementation Status

### ✅ Phase 1: Multi-format OCR & Basic Classification (COMPLETED)
- Multi-format text extraction (PDF, DOCX, TXT, images)
- Keyword-based classification (9 categories)
- Suggested folder generation
- Fully integrated with frontend

### ✅ Phase 2: ML Model & Synthetic Dataset (COMPLETED)
- 8 document type generators
- 4,800 synthetic examples with data augmentation
- TF-IDF + Linear SVC model (100% accuracy on synthetic data)
- Automatic fallback to keyword classifier
- Personalized folder suggestions by username

### 🎯 Phase 3: Production Improvements (OPTIONAL)
- User feedback collection system
- Retraining with real-world documents
- Entity extraction (dates, amounts, names)
- Duplicate detection
- Semantic search using embeddings
- Performance monitoring dashboard

## Testing

### Test Classification Endpoint
```bash
curl -X POST http://localhost:5001/api/clasificar \
  -F "file=@factura_ejemplo.pdf" \
  -F "user=testuser"
```

**Expected Response:**
```json
{
  "tipo_documento": "factura",
  "confianza": 0.95,
  "carpeta_sugerida": "/testuser/Documentos/Facturas"
}
```

### Test File Upload with AI
```bash
curl -X POST "http://localhost:5001/api/files/upload?ia=true" \
  -H "Authorization: Bearer <token>" \
  -F "file=@documento.pdf" \
  -F "path=/testuser/"
```

### Test ML Model Directly
```python
from src.ia.classifier_ml import MLDocumentClassifier

classifier = MLDocumentClassifier()
text = "FACTURA N.º 2025/001\nFecha: 15/03/2025\nTotal: 1.250,00€\nIVA: 262,50€"
result = classifier.classify_text(text, username="testuser")
print(result)
```

## Performance Metrics

### Response Times
| Operation | Time |
|-----------|------|
| TXT classification | ~0.2s |
| DOCX classification | ~0.3s |
| PDF classification (1 page) | ~3s |
| Image classification | ~4s |

### Model Performance
| Dataset | Accuracy | F1-Score |
|---------|----------|----------|
| Train | 100% | 1.00 |
| Validation | 100% | 1.00 |
| Test | 100% | 1.00 |
| Real-world (expected) | 85-95% | 0.85-0.95 |

## Troubleshooting

### Error: "Tesseract no encontrado"
1. Instalar Tesseract OCR desde https://github.com/UB-Mannheim/tesseract/wiki
2. Añadir a PATH del sistema
3. Reiniciar terminal

### Error: "No se pudo cargar modelo ML"
El sistema usará clasificador de keywords automáticamente. Para habilitar ML:
```bash
python -m src.ia.training.train_model
```

### Error: "python-docx no instalado"
```bash
pip install python-docx==1.1.2
```

### Clasificación incorrecta
- Verificar calidad del OCR (texto extraído)
- Revisar confianza del modelo (< 0.7 indica incertidumbre)
- Considerar re-entrenamiento con documentos reales

## Additional Documentation

For detailed implementation notes, see:
- `AI_IMPLEMENTATION_PHASE1.md`: Phase 1 implementation details
- `AI_IMPLEMENTATION_PHASE2.md`: Phase 2 ML training and dataset generation

## Testing

### Test Suite

DirectIA includes a comprehensive test suite with **60 tests** achieving **98.3% pass rate**.

**Structure**:
```
tests/
├── unit/                 # Fast, isolated unit tests (48 tests)
│   ├── test_utils.py           # Text cleaning utilities
│   ├── test_ocr.py             # OCR functionality
│   ├── test_pipeline.py        # AI pipeline
│   └── test_classifier.py      # ML and keyword classifiers
├── integration/          # API integration tests (12 tests)
│   └── test_api.py             # All API endpoints
├── fixtures/             # Sample test data
└── conftest.py           # Pytest configuration
```

**Running Tests**:

```bash
# All tests
pytest

# Only unit tests (fast)
pytest tests/unit/

# Only integration tests
pytest tests/integration/

# With coverage report
pytest --cov=src --cov-report=html

# Verbose output
pytest -v

# Using helper scripts
python run_tests.py              # All tests
python run_tests.py --unit       # Unit tests only
python run_tests.py --cov        # With coverage

# Windows
.\run_tests.ps1
.\run_tests.ps1 -Unit
.\run_tests.ps1 -Coverage

# Linux/macOS
./run_tests.sh
./run_tests.sh --unit
./run_tests.sh --coverage
```

**Test Coverage**:
- Utilities: 100%
- OCR: 100%
- Pipeline: 100%
- Classifiers: 100%
- API endpoints: 92%

**Current Status**: ✅ 59/60 tests passing

See `TEST_RESULTS.md` for detailed test report.

## Contributing

When adding new features:
1. Update this CLAUDE.md file with architectural changes
2. Document new API endpoints in the Route Blueprints section
3. Update configuration examples if new env variables are added
4. **Add tests for new functionality** (unit + integration)
5. Update AI categories if modifying classification system
6. Ensure all tests pass before committing: `pytest`
