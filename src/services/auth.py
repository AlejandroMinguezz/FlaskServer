import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from flask import current_app
from src.models import User

def _create_access_token(user):
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

def _create_refresh_token(user):
    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

def _verify_token(token):
    try:
        return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def register(session: Session, data: dict):
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not username or not password:
        return {"error": "Faltan campos"}, 400

    if session.query(User).filter_by(username=username).first():
        return {"error": "El usuario ya existe"}, 409
    if session.query(User).filter_by(email=email).first():
        return {"error": "El correo ya existe"}, 409

    hashed_password = generate_password_hash(password)
    nuevo_usuario = User(username=username, email=email, password_hash=hashed_password)
    session.add(nuevo_usuario)
    session.commit()

    return {"message": "Usuario registrado correctamente"}, 201


def login(session: Session, data: dict):
    username = data.get("username")
    password = data.get("password")

    user = session.query(User).filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return {"error": "Credenciales inválidas"}, 401

    # Verificar si el usuario está activo
    if not user.active:
        return {"error": "Cuenta desactivada. Contacta al administrador."}, 403

    access_token = _create_access_token(user)
    refresh_token = _create_refresh_token(user)

    # Usar localhost y el puerto desde la configuración
    port = current_app.config.get("PORT", 5001)
    admin_url = f"http://localhost:{port}/admin?token={access_token}"

    return {
        "message": "Login exitoso",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "username": user.username,
        "email": user.email,
        "role_id": user.role_id,
        "activo": user.active,
        "admin_panel": admin_url
    }, 200


def refresh_token(data: dict):
    token = data.get("refresh_token")
    payload = _verify_token(token)
    if not payload or payload.get("type") != "refresh":
        return {"error": "Token inválido"}, 401

    user_id = payload["sub"]
    role = payload.get("role", "usuario")
    new_access = jwt.encode(
        {"sub": str(user_id.id), "role": role, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)},
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )
    return {"access_token": new_access}, 200


def change_password(session: Session, data: dict):
    username = data.get("username")
    actual = data.get("actual")
    nueva = data.get("nueva")

    user = session.query(User).filter_by(username=username).first()
    if not user:
        return {"error": "Usuario no encontrado"}, 404

    if not check_password_hash(user.password_hash, actual):
        return {"error": "Contraseña actual incorrecta"}, 401

    user.password_hash = generate_password_hash(nueva)
    session.commit()
    return {"message": "Contraseña actualizada correctamente"}, 200
