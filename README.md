# 🧠 DirectIA – Sistema Inteligente de Gestión Documental

**DirectIA** es una aplicación de escritorio con interfaz **PyQt** y backend **Flask**, diseñada para la **gestión y clasificación automática de documentos empresariales**.
Permite subir, organizar, visualizar y clasificar documentos mediante IA (OCR + BERT), con almacenamiento en **MongoDB** y **PostgreSQL**.

---

## 🚀 Características principales

- Interfaz tipo explorador de archivos desarrollada en **PyQt**.
- OCR con **Tesseract** para extracción de texto de PDFs e imágenes.
- Clasificación automática con modelo **BERT (BETO)** para español.
- **Flask backend** con endpoints REST y panel de administración integrado.
- Almacenamiento híbrido:
  - Archivos en `../storage/files/`
  - Metadatos y resultados IA en **MongoDB**
  - Usuarios y roles en **PostgreSQL**
- **Bases de datos en Docker**, Flask ejecutado localmente.

---

## 🧩 Estructura del proyecto

```
directia/
├── flaskserver/          (este repositorio)
│   ├── src/
│   │   ├── app.py                  # Servidor Flask principal
│   │   ├── routes/                 # Rutas Flask (auth, admin, files, ia)
│   │   ├── ia/                     # Módulos de IA (OCR + Clasificación BERT)
│   │   └── config.py               # Configuración
│   │
│   ├── docker/
│   │   ├── docker-compose.yml      # Solo PostgreSQL y MongoDB
│   │   └── .env                    # Variables para Docker
│   │
│   ├── .env                        # Configuración principal
│   ├── setup.ps1/sh                # Setup inicial (ejecutar una vez)
│   ├── start_databases.ps1/sh      # Inicia bases de datos
│   ├── start_flask.ps1/sh          # Inicia Flask
│   └── requirements.txt
│
└── storage/                        # Archivos subidos por usuarios
    └── files/
```

**Nota:** Los datos de las bases de datos se almacenan en volúmenes Docker con nombre (`directia_postgres_data`, `directia_mongo_data`), no en directorios locales.

---

## ⚙️ Requisitos previos

- **Docker** y **Docker Compose** instalados.
- **Python 3.12** o superior.
- Dependencias de Python (ver `requirements.txt`).

---

## 🧭 Inicio rápido

### 0️⃣ Setup inicial (Primera vez solamente)

Antes de ejecutar la aplicación por primera vez:

**Windows:**
```powershell
.\setup.ps1
```

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

Este script configura automáticamente:
- ✅ Entorno virtual de Python
- ✅ Instalación de dependencias
- ✅ Verificación de Tesseract OCR
- ✅ Creación de directorios necesarios
- ✅ Verificación de Docker

### 1️⃣ Iniciar las bases de datos (Docker)

Las bases de datos PostgreSQL y MongoDB corren en Docker:

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

### 2️⃣ Iniciar Flask localmente

Una vez las bases de datos están corriendo:

**Windows:**
```powershell
.\start_flask.ps1
```

**Linux/macOS:**
```bash
./start_flask.sh
```

El servidor Flask estará disponible en `http://localhost:5001`

### 3️⃣ Detener las bases de datos

```bash
cd docker
docker-compose down
```

---

## 🔑 Acceso al panel administrativo

Una vez iniciado el servidor:

```
http://localhost:5001/admin?token=<TOKEN_JWT>
```

El token se obtiene al hacer **login** con un usuario con rol de **admin**:
```
POST http://localhost:5001/api/auth/login
```

Respuesta:
```json
{
  "access_token": "<TOKEN>",
  "admin_panel": "http://localhost:5001/admin?token=<TOKEN>"
}
```

---

## 🧠 Inteligencia Artificial

- **OCR:** Tesseract OCR con modelo en español para extracción de texto.
- **Clasificador:** modelo BETO (BERT en español) para clasificar documentos.
- **Clases:** `factura`, `recibo`, `cv`, `pagare`, `contrato`, `otro`.
- **Modo híbrido:** verificación con OpenAI/Gemini cuando la confianza es baja.

---

## 📦 Configuración (.env)

Archivo: `.env` (raíz del proyecto)

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

**Nota:** Los datos de las bases de datos se almacenan en volúmenes Docker con nombre, no en el archivo `.env`.

---

## 🧩 Próximas mejoras

- [ ] Endpoints REST versionados.
- [ ] Canal WebSocket o Celery para resultados IA en tiempo real.
- [ ] Autenticación JWT multiusuario.
- [ ] Configuración de nomenclaturas de archivo personalizadas por carpeta.
- [ ] Modo admin/debug con trazabilidad IA y diagrama ER.

---

## 🧾 Licencia

Proyecto desarrollado por **Alejandro Mínguez**  
© 2025 — Todos los derechos reservados.  
Uso académico y de investigación dentro del proyecto **DirectIA**.
