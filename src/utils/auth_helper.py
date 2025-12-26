"""
Helper para extraer información de autenticación de las peticiones
"""
import jwt
from flask import request, current_app


def get_user_from_token():
    """
    Extrae el username del token JWT de la petición.

    Returns:
        str: Username del usuario autenticado, o "unknown" si no hay token válido
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return "unknown"

    try:
        # El header debe ser "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return "unknown"

        token = parts[1]

        # Decodificar el token
        payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )

        # Extraer el username del payload
        return payload.get("username", "unknown")

    except jwt.ExpiredSignatureError:
        return "unknown"
    except jwt.InvalidTokenError:
        return "unknown"
    except Exception:
        return "unknown"