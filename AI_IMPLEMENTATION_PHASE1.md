# Implementación del Sistema de Clasificación IA - Fase 1

**Fecha**: 2025-11-09
**Estado**: ✅ COMPLETADO

## Resumen de Cambios

Se ha completado la **Fase 1** del sistema de clasificación de documentos con IA, haciendo que el endpoint `/api/clasificar` esté completamente funcional e integrado con el frontend React.

---

## 1. Cambios Realizados

### 1.1 Registro de Rutas ✅

**Archivo**: `src/routes/__init__.py`

```python
from .ia import bp as ia_bp

def register_blueprints(app):
    # ...
    app.register_blueprint(ia_bp)  # ← NUEVO
```

- Blueprint de IA ahora registrado en la aplicación Flask
- Endpoint accesible en `/api/clasificar`

---

### 1.2 Actualización del Endpoint ✅

**Archivo**: `src/routes/ia.py`

**Cambios**:
- ✅ URL prefix cambiado de `/api/ia` a `/api` → endpoint ahora es `/api/clasificar`
- ✅ Añadida documentación al endpoint
- ✅ Validación de archivo mejorada

**Request esperado**:
```
POST /api/clasificar
Content-Type: multipart/form-data

file: <archivo>
user: <username> (opcional)
```

**Response**:
```json
{
  "tipo_documento": "factura",
  "confianza": 0.85,
  "carpeta_sugerida": "/username/Documentos/Facturas"
}
```

---

### 1.3 Soporte de Múltiples Formatos ✅

**Archivo**: `src/ia/ocr/ocr.py`

**Nuevas funciones**:
- `extract_text_from_docx()` - Extrae texto de archivos DOCX/DOC
- `extract_text_from_txt()` - Lee archivos TXT con múltiples encodings

**Archivo**: `src/ia/ocr/__init__.py`

**Nueva función unificada**:
```python
def extract_text(file_path: str) -> str:
    """
    Extrae texto de cualquier formato soportado.
    Detecta automáticamente: PDF, DOCX, DOC, TXT, JPG, PNG, etc.
    """
```

**Formatos soportados**:
- ✅ **PDF** - OCR con Tesseract
- ✅ **DOCX/DOC** - python-docx
- ✅ **TXT** - Lectura directa multi-encoding
- ✅ **Imágenes** (JPG, PNG, BMP, TIFF) - OCR con Tesseract

---

### 1.4 Taxonomía de Documentos Administrativos ✅

**Archivo**: `src/ia/classifier.py`

**Nuevas categorías** (ampliado de 6 a 9 clases):

| Categoría      | Carpeta Sugerida            | Palabras Clave (ejemplos)                         |
|----------------|-----------------------------|-------------------------------------------------|
| `factura`      | `/Documentos/Facturas`      | factura, IVA, base imponible, proveedor         |
| `contrato`     | `/Documentos/Contratos`     | contrato, cláusula, partes contratantes         |
| `nomina`       | `/Documentos/Nóminas`       | nómina, IRPF, seguridad social, líquido         |
| `presupuesto`  | `/Documentos/Presupuestos`  | presupuesto, cotización, validez, oferta        |
| `recibo`       | `/Documentos/Recibos`       | recibo, pago, consumo, luz, agua, alquiler      |
| `certificado`  | `/Documentos/Certificados`  | certificado, certifica, acredita, se expide     |
| `fiscal`       | `/Documentos/Fiscales`      | declaración, renta, hacienda, modelo, IRPF      |
| `notificacion` | `/Documentos/Notificaciones`| notificación, administración, expediente        |
| `otro`         | `/Documentos/Otros`         | (documentos no clasificados)                    |

**Palabras clave expandidas**:
- Cada categoría tiene 10-15 palabras clave específicas
- Incluye variaciones y sinónimos comunes
- Optimizado para documentos administrativos españoles

---

### 1.5 Generación de Carpeta Sugerida ✅

**Archivo**: `src/ia/classifier.py`

**Nuevo método**:
```python
def classify_text(self, text: str, username: str = None) -> Dict:
    # ...
    carpeta_base = self.folder_mapping.get(tipo, "/Documentos/Otros")
    carpeta_sugerida = f"/{username}{carpeta_base}" if username else carpeta_base

    return {
        "tipo_documento": tipo,
        "confianza": float(confianza),
        "carpeta_sugerida": carpeta_sugerida  # ← NUEVO
    }
```

**Características**:
- ✅ Carpeta personalizada por usuario (`/username/Documentos/Facturas`)
- ✅ Mapeo automático de categoría → carpeta
- ✅ Fallback a `/Documentos/Otros` si tipo desconocido

---

### 1.6 Pipeline Actualizado ✅

**Archivo**: `src/ia/pipeline.py`

**Cambios**:
- ✅ Función `analizar_documento()` ahora acepta `username`
- ✅ Pasa username al clasificador para carpeta personalizada
- ✅ Manejo de errores mejorado
- ✅ Documentación completa

---

### 1.7 Servicio de Clasificación ✅

**Archivo**: `src/services/ia.py`

**Cambios**:
- ✅ Captura `user` del FormData del request
- ✅ Pasa username al pipeline
- ✅ Validación de respuesta mejorada
- ✅ Formato de respuesta estandarizado

---

### 1.8 Dependencias ✅

**Archivo**: `requirements.txt`

**Nueva dependencia**:
```txt
python-docx==1.1.2
```

Para instalar:
```bash
pip install python-docx
```

---

## 2. Flujo Completo del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                         │
│  Usuario sube archivo con toggle "Clasificación IA" ON      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ POST /api/clasificar
                         │ FormData: {file, user}
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Flask)                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. routes/ia.py                                      │  │
│  │    - Recibe request                                  │  │
│  │    - Extrae file y user                              │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│  ┌───────────────────▼──────────────────────────────────┐  │
│  │ 2. services/ia.py                                    │  │
│  │    - Guarda archivo temporalmente                    │  │
│  │    - Llama a pipeline con username                   │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│  ┌───────────────────▼──────────────────────────────────┐  │
│  │ 3. ia/pipeline.py                                    │  │
│  │    - Detecta formato de archivo                      │  │
│  │    - Extrae texto (PDF/DOCX/TXT/IMG)                 │  │
│  │    - Limpia texto                                    │  │
│  │    - Llama al clasificador                           │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│  ┌───────────────────▼──────────────────────────────────┐  │
│  │ 4. ia/ocr/                                           │  │
│  │    • ocr.py → ejecutar_ocr() (PDF/IMG)              │  │
│  │    • ocr.py → extract_text_from_docx()              │  │
│  │    • ocr.py → extract_text_from_txt()               │  │
│  │    • __init__.py → extract_text() (unificado)       │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│  ┌───────────────────▼──────────────────────────────────┐  │
│  │ 5. ia/utils.py                                       │  │
│  │    - clean_text() → normalización                    │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│  ┌───────────────────▼──────────────────────────────────┐  │
│  │ 6. ia/classifier.py                                  │  │
│  │    - DocumentClassifier.classify_text()              │  │
│  │    - Clasificación por keywords                      │  │
│  │    - Embeddings BETO (opcional)                      │  │
│  │    - Genera carpeta_sugerida                         │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│                      │ Response                             │
│                      ▼                                      │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ JSON Response
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                         │
│  {                                                          │
│    "tipo_documento": "factura",                             │
│    "confianza": 0.85,                                       │
│    "carpeta_sugerida": "/user1/Documentos/Facturas"         │
│  }                                                          │
│                                                             │
│  ↓ Usuario confirma sugerencia                              │
│  ↓ Archivo se mueve a carpeta sugerida                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Testing

### 3.1 Test Manual del Endpoint

Para probar el endpoint directamente:

```bash
curl -X POST http://localhost:5001/api/clasificar \
  -F "file=@factura_ejemplo.pdf" \
  -F "user=testuser"
```

**Respuesta esperada**:
```json
{
  "tipo_documento": "factura",
  "confianza": 0.85,
  "carpeta_sugerida": "/testuser/Documentos/Facturas"
}
```

### 3.2 Test desde Frontend

1. Inicia el backend Flask:
   ```bash
   cd FlaskServerTFG
   python run.py
   ```

2. Inicia el frontend React:
   ```bash
   cd DirectIA
   npm run dev
   ```

3. Sube un documento con toggle "Clasificación IA" activado

4. Verifica que:
   - ✅ Archivo se sube correctamente
   - ✅ Se muestra modal con sugerencia de clasificación
   - ✅ Carpeta sugerida es correcta
   - ✅ Al aceptar, archivo se mueve a la ubicación sugerida

---

## 4. Próximos Pasos (Fase 2)

### 4.1 Generación de Datasets Sintéticos

**Objetivo**: Crear 500-1000 documentos por categoría

**Tareas**:
- [ ] Implementar generadores de templates para cada categoría
- [ ] Generar variaciones usando Faker
- [ ] Aplicar data augmentation (errores OCR, formatos)
- [ ] Dividir en train/val/test (70/15/15)

**Archivos a crear**:
```
src/ia/data_generation/
├── __init__.py
├── template_generator.py
├── generators/
│   ├── factura_generator.py
│   ├── nomina_generator.py
│   ├── contrato_generator.py
│   └── ...
└── augmentation.py
```

### 4.2 Entrenamiento de Modelo ML

**Objetivo**: Mejorar precisión con modelo entrenado

**Opciones**:
- **v1**: TF-IDF + SVM (rápido, ligero)
- **v2**: Fine-tuning de BETO (más preciso, más recursos)

**Tareas**:
- [ ] Crear pipeline de preprocesamiento
- [ ] Entrenar modelo baseline (Naive Bayes)
- [ ] Entrenar modelo SVM con TF-IDF
- [ ] Evaluar y comparar modelos
- [ ] Integrar modelo entrenado en classifier.py

**Archivos a crear**:
```
src/ia/training/
├── __init__.py
├── train_model.py
├── evaluate_model.py
└── feature_extraction.py
```

### 4.3 Mejoras Futuras

- [ ] Sistema de feedback del usuario
- [ ] Re-entrenamiento periódico con datos reales
- [ ] Extracción de metadatos (fechas, importes, nombres)
- [ ] Detección de duplicados
- [ ] Búsqueda semántica

---

## 5. Archivos Modificados

```
✅ src/routes/__init__.py          - Registrar blueprint IA
✅ src/routes/ia.py                - Actualizar endpoint a /api/clasificar
✅ src/services/ia.py              - Capturar username, validación mejorada
✅ src/ia/pipeline.py              - Aceptar username, documentación
✅ src/ia/classifier.py            - Taxonomía completa, carpeta_sugerida
✅ src/ia/ocr/ocr.py               - Soporte DOCX y TXT
✅ src/ia/ocr/__init__.py          - Función extract_text() unificada
✅ requirements.txt                - Añadir python-docx
```

---

## 6. Configuración Necesaria

### 6.1 Instalar Dependencias

```bash
cd FlaskServerTFG
pip install -r requirements.txt
```

### 6.2 Verificar Tesseract OCR

El sistema requiere Tesseract para OCR de PDFs e imágenes:

```bash
# Windows
tesseract --version

# Si no está instalado, descargar desde:
# https://github.com/UB-Mannheim/tesseract/wiki
```

### 6.3 Descargar Modelo BETO (Opcional)

El modelo BERT español se descarga automáticamente en el primer uso:

```python
# src/ia/classifier.py
MODEL_NAME = "dccuchile/bert-base-spanish-wwm-cased"
```

Si no tienes internet o quieres usar solo keywords, el sistema funciona sin BETO.

---

## 7. Notas de Rendimiento

### 7.1 Tiempos de Respuesta Estimados

| Formato | Tamaño | OCR/Extracción | Clasificación | Total   |
|---------|--------|----------------|---------------|---------|
| TXT     | 50KB   | ~0.01s         | ~0.1s         | ~0.2s   |
| DOCX    | 100KB  | ~0.05s         | ~0.1s         | ~0.3s   |
| PDF     | 1 pág  | ~2-3s          | ~0.1s         | ~3s     |
| IMG     | 1MB    | ~3-4s          | ~0.1s         | ~4s     |

### 7.2 Optimizaciones Aplicadas

- ✅ Clasificador cargado una sola vez (singleton)
- ✅ Modelo BETO cargado al inicio (no en cada request)
- ✅ Limpieza de archivos temporales
- ✅ Manejo eficiente de errores

---

## 8. Troubleshooting

### Error: "python-docx no instalado"

```bash
pip install python-docx==1.1.2
```

### Error: "Tesseract no encontrado"

1. Instalar Tesseract OCR
2. Añadir a PATH del sistema
3. Reiniciar terminal

### Error: "No se pudo cargar BETO"

El sistema funciona sin BETO usando solo keywords. Para usar BETO:

```bash
pip install transformers torch
```

### Clasificación incorrecta

**Posibles causas**:
- Texto extraído con errores (OCR de mala calidad)
- Documento no tiene suficientes palabras clave
- Categoría ambigua o mixta

**Solución temporal**: Usar clasificación manual hasta entrenar modelo en Fase 2

---

## 9. Estado del Proyecto

| Componente                  | Estado        | Notas                                    |
|-----------------------------|---------------|------------------------------------------|
| Endpoint /api/clasificar    | ✅ Funcional  | Completamente integrado                  |
| Extracción PDF              | ✅ Funcional  | OCR con Tesseract                        |
| Extracción DOCX             | ✅ Funcional  | python-docx                              |
| Extracción TXT              | ✅ Funcional  | Multi-encoding                           |
| Extracción Imágenes         | ✅ Funcional  | OCR con Tesseract                        |
| Taxonomía de documentos     | ✅ Completa   | 9 categorías administrativas             |
| Generación carpeta_sugerida | ✅ Funcional  | Personalizada por usuario                |
| Clasificación por keywords  | ✅ Funcional  | Sistema básico pero efectivo             |
| Modelo ML entrenado         | ⏳ Pendiente  | Fase 2 - Requiere datasets               |
| Datasets sintéticos         | ⏳ Pendiente  | Fase 2                                   |

---

**Conclusión Fase 1**: Sistema de clasificación IA completamente funcional con soporte multi-formato y taxonomía completa de documentos administrativos. Listo para uso inmediato con clasificación basada en keywords. La Fase 2 mejorará la precisión mediante datasets sintéticos y modelos ML entrenados.

**Autor**: Claude Code
**Fecha**: 2025-11-09
