import jwt, datetime
from flask import current_app

def _create_access_token(user):
    role_name = getattr(user.role, "name", None)

    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": role_name,  # ahora lleva "admin"
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def create_refresh_token(user_id):
    payload = {
        "sub": str(user_id.id),
        "type": "refresh",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

def verify_token(token):
    try:
        return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
