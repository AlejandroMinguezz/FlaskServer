# src/config.py
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cargar variables de entorno desde .env
env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_file):
    load_dotenv(env_file, override=True)
    print(f"[CONFIG] Cargado desde {env_file}")
else:
    print("[CONFIG] Advertencia: archivo .env no encontrado")

class Config:
    """Configuración única de la aplicación"""

    # Environment
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    # Postgres (en Docker, acceso desde localhost)
    POSTGRES_USER = os.getenv("POSTGRES_USER", "directia_user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "directia_pass")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "directia")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    # Mongo (en Docker, acceso desde localhost)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://directia_user:directia_pass@localhost:27017/directia?authSource=admin")
    MONGO_DB = os.getenv("MONGO_DB", "directia")

    # Storage
    STORAGE_PATH = os.getenv("STORAGE_PATH", "../storage/files")

    # App
    SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
    PORT = int(os.getenv("PORT", "5001"))
    CREATE_TABLES = os.getenv("CREATE_TABLES", "true").lower() == "true"


# Configuración activa
ActiveConfig = Config
