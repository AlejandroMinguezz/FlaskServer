# src/app.py
import os
from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from pymongo import MongoClient
from src.config import ActiveConfig
from src.routes import register_blueprints
from src.models import Base, Role
from sqlalchemy import inspect
from src.routes.admin import bp as admin_bp


def init_roles(session):
    """Inicializa los roles básicos si no existen"""
    try:
        admin_role = session.query(Role).filter_by(name="admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrador del sistema")
            session.add(admin_role)
            print("Rol 'admin' creado")

        user_role = session.query(Role).filter_by(name="usuario").first()
        if not user_role:
            user_role = Role(name="usuario", description="Usuario estándar")
            session.add(user_role)
            print("Rol 'usuario' creado")

        session.commit()
        print("Roles inicializados correctamente")
    except Exception as e:
        session.rollback()
        print(f"Error inicializando roles: {e}")


def create_app():
    app = Flask(__name__)

    # Habilitar CORS para todas las rutas
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",  # Permite todas las IPs en la red local
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        },
        r"/admin/*": {
            "origins": "*",  # Permite todas las IPs en la red local
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    app.register_blueprint(admin_bp)
    app.config.from_object(ActiveConfig)

    storage_path = app.config.get("STORAGE_PATH", "./storage/files")
    os.makedirs(storage_path, exist_ok=True)

    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))
    app.session = SessionLocal

    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    defined_tables = Base.metadata.tables.keys()

    missing = [t for t in defined_tables if t not in existing_tables]
    if missing:
        Base.metadata.create_all(engine)
        print(f"Tablas creadas: {', '.join(missing)}")
    else:
        print("Todas las tablas ya existen.")

    # Inicializar roles básicos
    session = SessionLocal()
    init_roles(session)
    session.close()

    mongo_client = MongoClient(app.config["MONGO_URI"])
    app.mongo = mongo_client[app.config.get("MONGO_DB", "directia")]

    register_blueprints(app)

    @app.teardown_appcontext
    def remove_session(exception=None):
        SessionLocal.remove()

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", "5001"))
    debug = bool(os.getenv("FLASK_DEBUG", "1") == "1")
    app.run(host="0.0.0.0", port=port, debug=debug)
